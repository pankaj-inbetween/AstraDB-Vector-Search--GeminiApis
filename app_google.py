import os
import json
from flask import Flask, request, jsonify, send_from_directory
from astrapy import DataAPIClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

from langchain_google_genai import GoogleGenerativeAIEmbeddings

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "{Google AI API}"

client = DataAPIClient(os.environ["ASTRA_DB_APPLICATION_TOKEN"])
database = client.get_database(os.environ["ASTRA_DB_API_ENDPOINT"])
# collection = database.get_collection("apis")
collection = database.get_collection("apis_google")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


@app.route('/')
def home():
    return send_from_directory('.', 'index.html')
@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    vector = embeddings.embed_query(query)
    doc_iterator = collection.find(sort={"$vector": vector}, limit=5, include_similarity=True)
    results = [doc for doc in doc_iterator]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
