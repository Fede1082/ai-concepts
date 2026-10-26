###1 - Extraction of relevant information from the documents before injection
### 2 - Cleaning and preprocessing of the documents before injection
### 3 - Chunking the documents into smaller pieces before injection
### 4 - Indexing the documents into the collection
### 5 - Embedding the documents into the collection
### 6- Chromadb collection injection
###################################################


from pathlib import Path
from pypdf import PdfReader
from data_cleaning import preprocess_text

##### Injection of documents into the collection

#get the document content
document_path = Path("./rag/dataset")
document_list = []


# Saving the document names into a list
for file in document_path.glob("*.pdf"):
    counter = 0
    if file.is_file():
        counter += 1
        reader = PdfReader(file)
        document_content = '\f'.join(page.extract_text() or '' for page in reader.pages)
        document_list.append((file.name, preprocess_text(document_content)))
    
print("Document content:" + str(document_list))

##Cleaning and preprocessing of the documents

#Remove noise, stopwords, and irrelevant content from the documents before injection



# #Chunking fixed size + overlap
# for file in document_list:
#     # Load the document content
#     document_content = (document_path / file).read_text()

#     # Split the document into chunks
#     chunk_size = 10  # Adjust the chunk size as needed
#     chunks = [document_content[i:i + chunk_size] for i in range(0, len(document_content), chunk_size)]

#     # Add each chunk to the collection
#     for chunk in chunks:
#         add_documents_to_collection(documents=[chunk], metadatas=[], ids=[])



