from init_chromadb import init_collection, add_documents_to_collection, query_collection
from pathlib import Path



# Initialize the collection
init_collection()

##### Injection of documents into the collection

#get the document content
document_path = Path("./rag/dataset")
document_list = []



for file in document_path.glob("*.pdf"):
    if file.is_file():
        document_list.append(file.name)

print("Document content:" + str(document_list))




#chunking
# chunks = []
# chunk_size = 10  # Adjust the chunk size as needed
# for i in range(0, len(document), chunk_size):
#     chunk = document[i:i + chunk_size]
#     chunks.append(chunk)





# Example documents, metadatas, and ids

# indexing



#embedding

# Add documents to the collection
# add_documents_to_collection(documents=[document], metadatas=[], ids=[])



# # querying
# query = "What is the main topic of the document?"
# results = query_collection(query_texts=[query], n_results=1)