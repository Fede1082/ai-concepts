# Checklist RAG

1. Ingestione dei 3 PDF: estrazione, pulizia, metadati e ID di sezione. ok
2. Baseline: chunking fixed-size + overlap, Sentence Transformers, ChromaDB.

3. Esegui 30 domande e salva gli ID di sezione recuperati in top-5 e top-10.
4. Calcola Recall@5, Recall@10, Precision@5 e MRR con pytest.
5. Confronta fixed-size e recursive chunking, lasciando invariato l'embedding.
6. Confronta embedding locale e OpenAI, ricreando l'indice.
7. Aggiungi hybrid search e reranking solo dopo la baseline.
8. Valuta le risposte con Ragas: faithfulness e answer correctness.
9. Registra latenza, costi, errori, citazioni, casi senza risposta.
10. Completa FastAPI, logging, test e README di progetto.

**Nota:** le 30 domande hanno ciascuna un solo riferimento rilevante: qui Recall@K equivale a Hit@K per singola domanda. Per test avanzati aggiungi domande che richiedano più sezioni. Se il chunking cambia, mappa ogni chunk ai suoi ID di sezione originali prima di confrontare la ground truth.
