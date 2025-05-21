import os
import pandas as pd
from neo4j import GraphDatabase
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
import csv
import json
import time # Import time module
from tqdm import tqdm # Import tqdm

def calculate_jaccard_similarity(list1, list2):
    """Calculates the Jaccard similarity between two lists."""
    set1 = set(list1)
    set2 = set(list2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    if union == 0:
        # If both lists/sets are empty, similarity is conventionally 1.0
        return 1.0 
    
    return intersection / union

# Set up environment variables
NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


# Initialize deepseek LLM
model_name = 'deepseek-chat'
llm = ChatDeepSeek(
    model=model_name,
    temperature=0,
    max_tokens=None,
    api_key=DEEPSEEK_API_KEY
)

# # Initialize openai LLM
# model_name = 'gpt-4o-mini'
# refiner_llm = ChatOpenAI(
#     model=model_name,
#     temperature=0,
#     max_tokens=None,
#     api_key=OPENAI_API_KEY
# )

# Initialize Neo4j graph
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    enhanced_schema=True
)

# Define Cypher generation templates
CYPHER_GENERATION_TEMPLATE_STANDARD = """Task:
```
Generate Cypher statement to query a graph database.
The graph database contains restaurants and dishes from an alien galaxy.
Each restaurant is located in a planet.
Each planet has a given distance from the other ones expressed in light years.
The distance between planets is specified as a property of the 'HA_DISTANZA_ANNI_LUCE' relationship. This property is named 'distanza'.
Each Chef can have one or more licenses with a specific grade/score. The score is specified as an attribute in the relationship POSSIEDE_LICENZA that connects the nodes Chef and Licenza.
When you need to find a node Licenza, you must use his attributes 'nome' and 'sigla' in OR condition to find the match.
Sirius Cosmo is mainly known as the boss of the galaxy, not as a chef, and he defines all the main rules.
```

Instructions:
```
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Your goal is always to find a dish (Piatto) or a list of dishes starting from some filters.
You will never be provided with a name of a dish in the initial question.
```

Schema:
```
{schema}

Note: Do not include any text except the generated Cypher statement.
Always use piatto.nome in your RETURN statement
```

Examples: 
```
# example 1
Question-answer:
Quali sono i piatti che includono le Chocobo Wings come ingrediente?

MATCH (i:Ingrediente {{nome: "Chocobo Wings"}}),
(piatto:Piatto)-[:CONTIENE]->(i)
RETURN DISTINCT piatto.nome


# example 2
Question-answer:
Quali sono i piatti disponibili nei ristoranti entro 200 anni luce da Pandora?

MATCH (p1:Pianeta {{nome: "Pandora"}})-[rel:HA_DISTANZA_ANNI_LUCE]->(p2:Pianeta),
      (r:Ristorante)-[:SI_TROVA_SU]->(p2),
      (r)-[:OFFRE_IL_PIATTO]->(piatto:Piatto)
WHERE rel.distanza <= 200
RETURN DISTINCT piatto.nome
```

Question-answer:
{question}"""

CYPHER_GENERATION_TEMPLATE_FUZZY = """Task:Generate Cypher statement to query a graph database.
The graph database contains restaurants and dishes from an alien galaxy.
Each restaurant is located in a planet.
Each planet has a given distance from the other ones expressed in light years.
The distance between planets is specified as a property of the 'HA_DISTANZA_ANNI_LUCE' relationship. This property is named 'distanza'.
Each Chef can have one or more licenses with a specific grade/score. The score is specified as an attribute in the relationship POSSIEDE_LICENZA that connects the nodes Chef and Licenza.
When you need to find a node Licenza, you must use his attributes 'nome' and 'sigla' in OR condition to find the match.
When you need to find a node Tecnica, you must use his attributes 'nome' and 'description' in OR condition to find the match.
Sirius Cosmo is mainly known as the boss of the galaxy, not as a chef, and he defines all the main rules.


Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Your goal is always to find a dish (Piatto) or a list of dishes starting from some filters.
You will never be provided with a name of a dish in the initial question.
In order to be resilient to possible mispelling, always use the Levenshtein Distance with a threshold of 3, after applying the toLower function.


Schema:
{schema}

Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.

Examples: Here are a few examples of generated Cypher statements for particular questions:
# Quali sono i piatti disponibili nei ristoranti entro 200 anni luce da Pandora?

MATCH (p1:Pianeta {{nome: "Pandora"}})-[rel:HA_DISTANZA_ANNI_LUCE]->(p2:Pianeta),
      (r:Ristorante)-[:SI_TROVA_SU]->(p2),
      (r)-[:OFFRE_IL_PIATTO]->(piatto:Piatto)
WHERE rel.distanza <= 200
RETURN DISTINCT piatto.nome


The question is:
{question}"""

REFINER_LLM_TEMPLATE = """You are a Neo4j Query Refiner. Your task is to analyze natural language questions about a graph database and extract ONLY the essential information needed to construct a valid Cypher query. Remove all irrelevant details, conversational fluff, and non-essential context while preserving the core query intent and all necessary entities/relationships.

The relevant information can be deducted by the schema of the graph.

Schema:
```
{schema}
```

Note: Most of the questions are okay and they do not need to be refined.

Examples: 
```
question-refinement:
Quali sono i piatti che includono i Sashimi di Magikarp?
Quali sono i piatti che includono i Sashimi di Magikarp?

question-refinement:
"Quali piatti sono accompagnati dai misteriosi Frutti del Diavolo, che donano poteri speciali a chi li consuma?"
"Quali piatti sono accompagnati dai misteriosi Frutti del Diavolo?"

question-refinement:
Quali piatti sono preparati utilizzando il Vero Ghiaccio e le tecniche di Cottura Sottovuoto Frugale Energeticamente Negativa e Cottura Sottovuoto Bioma Sintetico?
Quali piatti sono preparati utilizzando il Vero Ghiaccio e le tecniche di Cottura Sottovuoto Frugale Energeticamente Negativa e Cottura Sottovuoto Bioma Sintetico?

question-refinement:
Quali sono i piatti preparati da chef con licenza LTK di grado 7 o superiore che utilizzano le Spezie Melange come ingrediente?
Quali sono i piatti preparati da chef con licenza LTK di grado 7 o superiore che utilizzano le Spezie Melange come ingrediente?

question-refinement:
Quali piatti dovrei scegliere per un banchetto a tema magico che includa le celebri Cioccorane?
Quali piatti contengono le celebri Cioccorane?

```

question-refinement:
{question}"""

# initialize driver
# Create a driver instance
driver = GraphDatabase.driver(uri=NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# define number of questions
NUM_OF_QUESTIONS = 5

# Load the CSV file
df = pd.read_csv("data/domande.csv")  # Replace with the actual file path

# Extract the column as a list
questions = df["domanda"].tolist()
questions = questions[0:2]
results = []

# ...
with open("data/Misc/dish_mapping.json", "r", encoding="utf-8") as file:
    dish_mapping = json.load(file)  # Parses JSON into a Python dictionary or list

# ...
solutions = []

with open("solution/ground_truth_mapped.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Convert the "result" column into a list of integers
        solutions.append([int(x) for x in row["result"].split(",")])

solutions = solutions[:10]

# ...
step = 0
# Wrap enumerate(questions) with tqdm for progress bar
print(f"Processing {len(questions)} questions...")
for index, question in tqdm(enumerate(questions), total=len(questions), desc="Evaluating Questions"):

    # initialize result element
    result = {"question": question, "refined_query": "", "cypher_query": "", "llm_call_duration_seconds": None, "answer": [], "solution": [], "Jaccard similarity": None, "error_log": ""}

    # define step
    step = step + 1

    # get graph's schema
    schema = graph.schema

    # ### REFINEMENT
    # system_template = REFINER_LLM_TEMPLATE
    # prompt_template = ChatPromptTemplate.from_messages([("system", system_template), ("user", "")])
    # prompt = prompt_template.invoke({"schema": schema, "question": question})

    # try:
    #     response = llm.invoke(prompt)
    #     refined_query = response.content 

    #     # add cypher query to results
    #     result["refined_query"] = refined_query
                  
    # except Exception as e:
    #     # Log the error if query generation or execution fails
    #     result["error_log"] = f"Query refinement failed: {str(e)}"
    #     # dishes_found remains empty

    ### TRANSLATION
    # define prompt
    system_template = CYPHER_GENERATION_TEMPLATE_STANDARD
    prompt_template = ChatPromptTemplate.from_messages([("system", system_template), ("user", "")])
    prompt = prompt_template.invoke({"schema": schema, "question": question})

    dishes_found = [] # Initialize before try block
    llm_start_time = None
    llm_end_time = None
    try:
        llm_start_time = time.time() # Record start time
        response = llm.invoke(prompt)
        llm_end_time = time.time() # Record end time
        cypher_query = response.content

        # add cypher query and duration to results
        result["llm_call_duration_seconds"] = llm_end_time - llm_start_time
        result["cypher_query"] = cypher_query
        
        # run cypher query
        with driver.session() as session:
            answer = session.run(cypher_query)
            # Ensure dishes_found is populated only if query succeeds
            dishes_found = [record["piatto.nome"] for record in answer] 
            
    except Exception as e:
        # Log the error if query generation or execution fails
        result["error_log"] = f"Cypher query failed: {str(e)}"
        # dishes_found remains empty

    # ...       
    #print(step)
    # The line below seems like a placeholder/debug line, let's remove it 
    # as dishes_found should now come from the query or be empty on error.
    # dishes_found = ["Galassia di Sapori: Il Viaggio Senza Tempo"] 
    
    # Map dish names to their IDs using the loaded dish_mapping
    # This part will run even if dishes_found is empty due to an error
    mapped_dishes = []
    if not result["error_log"]: # if there ano previous error proceed with the mapping
        for dish_name in dishes_found:
            if dish_name in dish_mapping:
                mapped_dishes.append(dish_mapping[dish_name])
                result["answer"] = mapped_dishes
            else:
                print(f"Warning: Dish '{dish_name}' not found in dish_mapping.json") # Or handle as needed
                result["error_log"] = "dish mapping was not successful"

    
    # add solutions
    solution = solutions[index]
    result["solution"] = solution

    # compute jaccard score
    jaccard_score = calculate_jaccard_similarity(result["answer"], result["solution"])
    result["Jaccard similarity"] = jaccard_score

    # Append the final result for this question
    results.append(result)

# After processing all questions, save the results to a JSON file
report_dir = "report"
output_file = os.path.join(report_dir, "report.json")

# Create the report directory if it doesn't exist
os.makedirs(report_dir, exist_ok=True)

# Write the results list to the JSON file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"Results saved to {output_file}")
