###1 - Extraction of relevant information from the documents before injection
### 2 - Cleaning and preprocessing of the documents before injection
### 3 - Chunking the documents into smaller pieces before injection
### 4 - Indexing the documents into the collection
### 5 - Embedding the documents into the collection
### 6- Chromadb collection injection
###################################################


import json
from pathlib import Path
from pypdf import PdfReader
if __package__:
    from ...ingestion_old.data_cleaning import preprocess_text
    from ...ingestion_old.validation import ValidationConfig, validate_document
else:
    from rag.src.ingestion.data_cleaning import preprocess_text
    from rag.src.ingestion.validation import ValidationConfig, validate_document

##### Injection of documents into the collection

#get the document content
document_path = Path(__file__).resolve().parents[1] / "dataset"
report_path = document_path.parent / "validation_reports"
validation_config = ValidationConfig()
document_list = []


# Saving the document names into a list
for file in document_path.glob("*.pdf"):
    if file.is_file():
        reader = PdfReader(file)
        document_content = '\f'.join(page.extract_text() or '' for page in reader.pages)
        cleaned_content = preprocess_text(document_content)
        report = validate_document(
            document_content, cleaned_content, validation_config, document_id=file.name
        )
        report_path.mkdir(parents=True, exist_ok=True)
        report_file = report_path / f"{file.stem}.json"
        report_file.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Validation {file.name}: {report['status']} "
              f"({len(report['anomalies'])} segnalazioni) — {report_file}")
        document_list.append((file.name, cleaned_content))
    
print("Document content:" + str(document_list))







