

## local database hosted in our computer
## Data is passed to model and get the relevant reply for users


from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

df = pd.read_csv("Information/PlantDatabase.csv")
 ## df = dataframe

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./TrainedDataForAIBot" ## folder to store database. Chroma vector store ho hai

add_documents = not os.path.exists(db_location) ## check if database exists

if add_documents:
    documents = []
    ids = []

    for i, row in df.iterrows():        ## this acess platdatabase row by row
        document = Document(
    page_content=f"{row['PlantName']} (Scientific Name: {row['ScientificName']}): {row['Usage']}",
    id=str(i)
)
        ids.append(str(i))
        documents.append(document)

vector_store = Chroma(
    collection_name="PlantName",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    vector_store.add_documents(documents=documents, ids=ids)


retriever = vector_store.as_retriever(
    search_kwargs={"k": 2}  # 'k' means number of results to return
)






