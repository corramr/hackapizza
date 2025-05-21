PROMPT_RESTAURANT_PLANET_RETRIEVAL = """
Ti fornirò in input il testo di un menù di un ristorante, contenente informazioni riguardo il suo chef, i piatti proposti nel ristorante con relativi ingredienti e tecniche.
Voglio che tu estragga due informazioni (nome_ristorante e nome_pianeta) e le strutturi in modo rigoroso in un JSON avente la seguente struttura:
{
  "nome_ristorante": "Anima Cosmica",
  "nome_pianeta": "Aurora Pandora"
}

I nomi possibili dei Pianeti sono: Arrakis, Pandora, Cybertron, Ego, Montressor, Krypton, Namecc, Klyntar, Asgard, Tatooine

Produci in output solo il JSON corretto. Non aggiungere altri commenti o testo superfluo.

Testo da convertire in JSON:

"""

PROMPT_RESTAURANT_MENU_RETRIEVAL = """
Ti fornirò in input il testo di un menù di un ristorante, contenente informazioni riguardo il suo chef, i piatti proposti nel ristorante con relativi ingredienti e tecniche.
Voglio che tu estragga le informazioni e le strutturi in modo rigoroso in un JSON avente la seguente struttura di esempio:
{
  "nome_ristorante": "Anima Cosmica",
  "nome_chef": "Aurora Stellaris",
  "menu": [
      {
        "nome_piatto": "Nebulosa Celestiale alla Stellaris",
        "ingredienti": [
          "Shard di Materia Oscura",
          "Carne di Balena Spaziale"
        ],
        "tecniche": [
          "Cottura a Vapore con Flusso di Particelle Isoarmoniche",
          "Cottura a Vapore Termocinetica Multipla"
        ]
      },
            {
        "nome_piatto": "Sinfonia Tempolare Galattica",
        "ingredienti": [
          "Polvere di Crononite",
          "Carne di Kraken"
        ],
        "tecniche": [
          "Bollitura Infrasonica Armonizzata",
          "Cottura con Microonde Entropiche Sincronizzate"
        ]
      }
    ]
}

Produci in output solo il JSON corretto. Non aggiungere altri commenti o testo superfluo.

Testo da convertire in JSON: 

"""

PROMPT_RESTAURANT_LICENSES_RETRIEVAL = """
Ti fornirò in input la descrizione di un ristorante e il tuo compito e di estrarre tutte le licenze/certificazioni possedute dallo Chef e/o dal ristorante.
Voglio che tu estragga tali informazioni e le strutturi in un JSON avente il seguente formato di esempio:
{
    "nome_ristorante": "SuperRistorante",
    "licenze": [
        {
        "nome_licenza": "licenza magica",
        "grado_licenza" "1"
        }
    ]
}

Le uniche licenze disponibili sono: 
"nome_licenza": "Psionica",
"sigla_licenza": "P",

"nome_licenza": "Temporale",
"sigla_licenza": "t",

"nome_licenza": "Gravitazionale",
"sigla_licenza": "G",

"nome_licenza": "Antimateria",
"sigla_licenza": "e+",

"nome_licenza": "Magnetica",
"sigla_licenza": "Mx",

"nome_licenza": "Quantistica",
"sigla_licenza": "Q",

"nome_licenza": "Luce",
"sigla_licenza": "c",

"nome_licenza": "Livello di Sviluppo Tecnologico",
"sigla_licenza": "LTK"

Produci in output solo il JSON corretto. Non aggiungere altri commenti o testo superfluo.

Testo da convertire in JSON:
"""


PROMPT_MANUAL_LICENSES_RETRIEVAL = """
Ti fornirò in input un manuale e il tuo compito è estrarre tutte le licenze menzionate, la loro sigla breve e i rispettivi livelli.
Voglio che tu estragga le informazioni e le strutturi in modo rigoroso in un JSON avente la seguente struttura di esempio:
[
    {
        "nome_licenza" : "Magica",
        "sigla_licenza" : "Mg",
        "livelli": ["primo livello", "livello secondo"]
    }
]

Produci in output solo il JSON corretto. Non aggiungere altri commenti o testo superfluo.

Testo da convertire in JSON:
"""