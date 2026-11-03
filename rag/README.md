# RAG

## Chunking

The structural chunking phase reads `.txt` files recursively from `data/clean`,
recognizes `CTR-`, `NAR-`, and `TEC-` headings, and writes JSONL records to the
`output_file` configured in `configs/pipeline.yaml`.

Run it from this project with:

```bash
rag chunk
```

Chunk size is measured with the `cl100k_base` encoding from `tiktoken` and the
`max_tokens` value in the pipeline configuration. Chunk indices start at 1 for
each document. Page numbers are derived from form-feed (`\f`) separators; when
the cleaned text has no page separators, chunks are assigned to page 1.