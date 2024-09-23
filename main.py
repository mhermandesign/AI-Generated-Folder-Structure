import openai.types.chat
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
import pprint

'''
This script is designed to generate a folder structure on a local machine by using a generative model as the logic engine, rather than hard-coding it. Its intent is simply to help you overcome the blank-page part of starting a project.

It does this by sending a request to a generative model, considering a project type and topic, and responding with an outline of a (hopefully) useful folder structure. On user confirmation, Python's 'json' module is called in to help parse the output, pprint formats the text for user legibility, and os is used for actually creating the folder structure. This script specifically calls to the 'openai' module, but could be refactored to work with other models and APIs. It also uses 'dotenv' to access the .env file, which should be created by the user in the root of the project directory.
'''


# ==================================
# Script Setup
# ==================================

load_dotenv()

_api_key = os.getenv("API_KEY") # Ensure you have a .env file at the root of the project folder containing a key-pair for API_KEY.

client = OpenAI(api_key=_api_key)


# Model Request Config. | Change these as needed to work within the parameters of the model you're using.

_model: str = "gpt-4o-mini" # The model being called.

_language: str = "English" # The desired language of the response, expecting the model to have access to the language.

_max_depth: int = 5 # How many levels deep the folder structure can be nested. A larger number leads to more granular outputs.

_max_tokens: int = 3200 # The max amount of tokens the model will attempt to reach. ***This has real-world cost to your API billing account!***

_temperature: float = 0.1 # 0.0 - 1.0 | how much wiggle room the model has to go out of scope regarding the folder names.

# Folder Structure Config. | Change these to meet your operating system needs.
_base_path = "./example_folder_structures" # By default, this is set to the current project directory as a root. Change to whatever works for your needs.


# ==================================
# Function Definitions
# ==================================

# Folder Structure Generation | Uses 'os' to make the directory structure on your machine.
def create_folders(directory_structure, base_path="."):
    # Recursively dig into the
    for folder_name, sub_structure in directory_structure.items():

        folder_path: str = os.path.join(base_path, folder_name)

        os.makedirs(folder_path, exist_ok=True)

        if sub_structure:
            create_folders(sub_structure, base_path=folder_path)

    print("Complete!")


def get_folder_structure_proposal(project_type=input("Project Type:"), topic=input("Topic:")):
    proposed_folder_structure: dict # This is set after getting a completion below.


    # System Prompt | Modify this prompt as needed.
    # === START PROMPT ===
    system_prompt = f"""
    You are a structured-data generator, whose goal is to create a nested dictionary on the topic of '{topic}'.
    
    This response will be used to create a directory structure outlined in JSON format.
    
    '{project_type}' is the type of project the response should facilitate.
    
    The response should include any and all potentially-necessary folders for the defined project. For example,
    if the project type is "Static Website", some folders might include "html", "css", "js", "images", "fonts", etc.
    If the project type is "Research", the folders may include the likes of "sources", "images", "drafts", etc.
    
    Create folders with any names that might be necessary for the specified topic and type, considering the disciplines
    which would have need of the folder structure as well as the types of work the folders would host.

    Do not include any language outside of the structured data response.
    
    Limit to, and attempt to reach a depth of, {_max_depth}, excluding the root.
    
    The first key in the response should be topical and project-appropriate.
    
    All keys should be intended as names for folders, and *not* files.
    
    Keys should be in {_language}.
    """
    # === END PROMPT ===

    try:
        # Completion
        completion: openai.types.chat.ChatCompletion = client.chat.completions.create(
            model = _model,
            messages = [{"role": "system", "content": system_prompt}],
            temperature = _temperature,
            max_completion_tokens= _max_tokens,
            presence_penalty=0.2,
            response_format={"type":"json_object"}
        )

        proposed_folder_structure = json.loads(completion.choices[0].message.content)


        # PrettyPrint Formatting
        print("Does this response look good?")
        print("============================================")
        pprint.pp(proposed_folder_structure)
        print("============================================")


        # User Response Handling
        user_response = input("> Y or N: ")

        while user_response not in ['Y', 'y', 'N', 'n']:
            print("Invalid input. Please enter 'Y' or 'N'.")
            user_response = input("> Y or N: ")

        if user_response in ['N', 'n']:
            print("Try again!")
            return

        elif user_response in ['Y', 'y']:
            print("Great, I'll get started!")
            return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"{e}")



# The main script loop | Requests a proposal from a generative model and, if it exists, builds the folder structure.
def main():
    proposed_folder_structure: dict = get_folder_structure_proposal()
    if proposed_folder_structure:
        create_folders(proposed_folder_structure, _base_path)


# ==================================
# Script Initialization
# ==================================

if __name__ == '__main__':
    main()
