from dotenv import load_dotenv
from neo4j import GraphDatabase
import os
from utils import (
    add_chef_licenses_relationships,
    add_license_nodes,
    add_planet_distances_relationships,
    add_planet_nodes,
    add_menu_nodes,
    aggiorna_tecniche,
    create_indexes,
    get_graph_schema,
)

# set up FLAGS
CREATE_MENU_NODES = False
CREATE_PLANET_NODES = False
CREATE_PLANET_DISTANCES_RELATIONSHIPS = False
CREATE_LICENSE_NODES = False
CREATE_CHEF_LICENSES_RELATIONSHIPS = False

# set up environment variables
os.environ["NEO4J_URI"] = os.getenv("NEO4J_URI")
os.environ["NEO4J_USERNAME"] = os.getenv("NEO4J_USERNAME")
os.environ["NEO4J_PASSWORD"] = os.getenv("NEO4J_PASSWORD")

# set up neo4j driver
driver = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]))

# get schema
schema = get_graph_schema(driver)

# add nodes: restaurants, chef, dishes, ingredients, techniques
if CREATE_MENU_NODES:
    restaurant_menu_directory = 'restaurant_menu'
    add_menu_nodes(driver, restaurant_menu_directory)                

# add nodes: planets
if CREATE_PLANET_NODES:
    restaurant_planet_directory = 'restaurant_planet'
    add_planet_nodes(driver, restaurant_planet_directory)

# add additonal relationship: distance between planets
if CREATE_PLANET_DISTANCES_RELATIONSHIPS:
    planet_distances_path = "data/Misc/Distanze.csv"
    add_planet_distances_relationships(driver, planet_distances_path)

# add nodes: licenses 
if CREATE_LICENSE_NODES:
    manual_licenses_path = "manual_licenses/licenze.json"
    add_license_nodes(driver, manual_licenses_path)

# add additional relationship: chef --> licenses
if CREATE_CHEF_LICENSES_RELATIONSHIPS:
    restaurant_licenses_directory = "restaurant_licenses"
    add_chef_licenses_relationships(driver, restaurant_licenses_directory)



# tecniche_directory = "tecniche.json"
# aggiorna_tecniche(driver, tecniche_directory)
create_indexes(driver)