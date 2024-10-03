
import os
import json
import time
from datetime import datetime
from astrapy import DataAPIClient
from dotenv import load_dotenv
import getpass
import os

load_dotenv()
from langchain_google_genai import GoogleGenerativeAIEmbeddings

script_dir = os.path.dirname(__file__)  # Directory of the script
file_path = os.path.join(script_dir, 'api_data.json')
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "{Google AI API Key}"

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

with open(file_path) as user_file:
    file_contents = user_file.read()

client = DataAPIClient(os.environ["ASTRA_DB_APPLICATION_TOKEN"])
database = client.get_database(os.environ["ASTRA_DB_API_ENDPOINT"])
collection = database.get_collection("apis_google")

apis = json.loads(file_contents)
# movies = movies[:100]
for api in apis:
    print(api.get('api_name'))
    print("\n")
    content = api.get('api_name') + f" - {api.get('description')} - within project {api.get('owner_project')} with ID {api.get('owner_project_ID')}\n\n"
    vector = embeddings.embed_query(content)

    while True:
        try:
            collection.update_one(
                {'_id': api.get('id')},
                {'$set': {
                    'title': api.get('api_name'),
                    'description': api.get('description'),
                    '$vector': vector,
                    'api_method': api.get('api_method'),
                    'project': api.get('owner_project'),
                    'project_id': api.get('owner_project_ID'),
                    'metadata': {'ingested': datetime.now()}
                }},
                upsert=True
            )
        except Exception as ex:
            print(ex)
            print("Retrying...")
            continue
        break
