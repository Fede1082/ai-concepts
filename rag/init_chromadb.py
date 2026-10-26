import chromadb


#Create a collection
def init_collection():
    print("Initializing the collection...")
    client = chromadb.Client()

    collection = client.create_collection("my_collection")
    print("Collection initialized.")

#Add documents to the collection
# ie collection.add(
#     documents=[
#         "This is the first document.",
#         "This is the second document.",
#         "This is the third document."
#     ],
#     metadatas=[
#         {"source": "document_1"},
#         {"source": "document_2"},
#         {"source": "document_3"}
#     ],
#     ids=["doc1", "doc2", "doc3"]    
# )
def add_documents_to_collection(documents, metadatas, ids):

    print("Adding documents to the collection...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Documents added to the collection.")

#Query the collection
def query_collection(query_texts, n_results):
    print("Querying the collection...")
    results = collection.query(
        query_texts=query_texts,
        n_results=n_results
    )
    print("Query results obtained.")
    return results

