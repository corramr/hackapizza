from openai import OpenAI
import os
from utils import parse_pdfs_folder, save_manual_info_to_json_file, save_restaurant_info_to_json_file
from prompts import (
    PROMPT_RESTAURANT_MENU_RETRIEVAL,
    PROMPT_RESTAURANT_PLANET_RETRIEVAL,
    PROMPT_RESTAURANT_LICENSES_RETRIEVAL,
    PROMPT_MANUAL_LICENSES_RETRIEVAL,
)

# define FLAGS
GET_RESTAURANT_MENU_INFO = True
GET_RESTAURANT_PLANET_INFO = False
GET_RESTAURANT_LICENSES_INFO = False
GET_MANUAL_LICENSES_INFO = True

# set model and its api key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
model_name = "gpt-4o-mini"


########## PARSE RESTAURANTS ##########
# define restaurant file path
restaurant_path = "data/Ristoranti"

# extracting info by reading menus
for restaurant_filename in os.listdir(restaurant_path):

    # extract menu from each restaurant
    if GET_RESTAURANT_MENU_INFO:
        restaurant_menu = parse_pdfs_folder(
            pdf_folder_path=restaurant_path,
            filename=restaurant_filename,
            customized_prompt=PROMPT_RESTAURANT_MENU_RETRIEVAL,
            client=client,
            model_name=model_name,
        )
        save_restaurant_info_to_json_file(restaurant_menu, "menu")

    # extract planets on which resturant is located
    if GET_RESTAURANT_PLANET_INFO:
        restaurant_planet = parse_pdfs_folder(
            pdf_folder_path=restaurant_path,
            filename=restaurant_filename,
            customized_prompt=PROMPT_RESTAURANT_PLANET_RETRIEVAL,
            client=client,
            model_name=model_name,
        )
        save_restaurant_info_to_json_file(restaurant_planet, "planet")

    # extract licenses used by resturants
    if GET_RESTAURANT_LICENSES_INFO:
        restaurant_licenses = parse_pdfs_folder(
            pdf_folder_path=restaurant_path,
            filename=restaurant_filename,
            customized_prompt=PROMPT_RESTAURANT_LICENSES_RETRIEVAL,
            client=client,
            model_name=model_name,
        )
        save_restaurant_info_to_json_file(restaurant_licenses, "licenses")


########## PARSE MANUAL ##########
# define manual file path
pdf_folder_path = "data/Manuale"
manual_filename = "manuale_di_cucina.pdf"

# extract licenses from manual file
if GET_MANUAL_LICENSES_INFO:
    manual_licenses = parse_pdfs_folder(
        pdf_folder_path=pdf_folder_path,
        filename=manual_filename,
        customized_prompt=PROMPT_MANUAL_LICENSES_RETRIEVAL,
        client=client,
        model_name=model_name,
    )
    save_manual_info_to_json_file(manual_licenses)
