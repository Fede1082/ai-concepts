import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import tiktoken

from rag.config import ChunkingConfig, Config, load_config
from rag.chunking import build_chunks, load_documents, run_chunking, split_by_headers


HEADER_PATTERN = r"^((?:CTR|NAR|TEC)-\d{2}) — (.+)$"
ENCODING = tiktoken.get_encoding("cl100k_base")


class ChunkingTests(unittest.TestCase):
    def make_config(self, input_dir: Path, output_file: Path, max_tokens: int = 800):
        return ChunkingConfig(
            input_dir=input_dir,
            output_file=output_file,
            max_tokens=max_tokens,
            header_pattern=HEADER_PATTERN,
            strategy="structural",
        )

    def test_splits_supported_structural_headers_and_keeps_preamble(self):
        text = (
            "Introduzione.\n"
            "CTR-01 — Oggetto\nTesto contratto.\n"
            "NAR-01 — Inizio\nTesto narrativo.\n"
            "TEC-01 — Requisiti\nTesto tecnico.\n"
        )

        sections = split_by_headers(text, HEADER_PATTERN)

        self.assertEqual(len(sections), 4)
        self.assertEqual(sections[0][1], "Introduzione.\n")
        self.assertTrue(sections[1][1].startswith("CTR-01"))
        self.assertTrue(sections[2][1].startswith("NAR-01"))
        self.assertTrue(sections[3][1].startswith("TEC-01"))

    def test_creates_one_based_metadata_and_page_numbers(self):
        text = (
            "Introduzione.\nCTR-01 — Oggetto\nTesto contratto."
            "\fNAR-01 — Inizio\nTesto narrativo.\n"
        )
        chunks = build_chunks(
            [(Path("contratto_servizi.txt"), text)],
            self.make_config(Path("clean"), Path("chunks.jsonl")),
        )

        self.assertEqual([chunk["indice"] for chunk in chunks], [1, 2, 3])
        self.assertEqual(
            [chunk["doc_id"] for chunk in chunks],
            ["contratto_servizi_1", "contratto_servizi_2", "contratto_servizi_3"],
        )
        self.assertEqual([chunk["page"] for chunk in chunks], [1, 1, 2])
        self.assertEqual(chunks[0]["doc_name"], "contratto_servizi")
        self.assertEqual(
            chunks[0]["hash"],
            hashlib.sha256(chunks[0]["raw_text"].encode("utf-8")).hexdigest(),
        )

    def test_respects_token_limit_and_preserves_text(self):
        config = self.make_config(Path("clean"), Path("chunks.jsonl"), max_tokens=128)
        for text in (
            "TEC-01 — Sezione\n" + ("testo lungo " * 300),
            "TEC-01 — Sezione\n" + ("x" * 2000),
        ):
            with self.subTest(text_length=len(text)):
                chunks = build_chunks(
                    [(Path("manuale_tecnico.txt"), text)],
                    config,
                )

                self.assertGreater(len(chunks), 1)
                self.assertEqual("".join(chunk["raw_text"] for chunk in chunks), text)
                self.assertTrue(
                    all(
                        len(ENCODING.encode(chunk["raw_text"], disallowed_special=())) <= 128
                        for chunk in chunks
                    )
                )
                self.assertEqual(
                    [chunk["indice"] for chunk in chunks],
                    list(range(1, len(chunks) + 1)),
                )

    def test_loads_nested_txt_documents_in_sorted_order(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_dir = Path(temporary_directory) / "clean"
            (input_dir / "b").mkdir(parents=True)
            (input_dir / "a").mkdir()
            (input_dir / "b" / "b.txt").write_text("Documento B", encoding="utf-8")
            (input_dir / "a" / "a.txt").write_text("Documento A", encoding="utf-8")

            documents = load_documents(input_dir)

        self.assertEqual([path.stem for path, _ in documents], ["a", "b"])
        self.assertEqual([text for _, text in documents], ["Documento A", "Documento B"])

    def test_run_chunking_writes_jsonl_using_configured_paths(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_dir = root / "clean" / "manuale_tecnico"
            input_dir.mkdir(parents=True)
            (input_dir / "manuale_tecnico.txt").write_text(
                "TEC-01 — Avvio\nAvviare il servizio.", encoding="utf-8"
            )
            output_file = root / "chunks" / "chunks.jsonl"

            stats = run_chunking(Config(chunking=self.make_config(input_dir, output_file)))

            rows = [
                json.loads(line)
                for line in output_file.read_text(encoding="utf-8").splitlines()
            ]

        self.assertEqual(stats["documents"], 1)
        self.assertEqual(stats["chunks"], 1)
        self.assertEqual(rows[0]["indice"], 1)
        self.assertEqual(rows[0]["raw_text"], "TEC-01 — Avvio\nAvviare il servizio.")

    def test_load_config_resolves_paths_from_project_root(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            config_dir = project_root / "configs"
            config_dir.mkdir()
            config_path = config_dir / "pipeline.yaml"
            config_path.write_text(
                "chunk:\n"
                "  max_tokens: 800\n"
                "  strategy: structural\n"
                "  input_dir: data/clean\n"
                "  output_file: data/chunks/chunks.jsonl\n"
                f"  header_pattern: '{HEADER_PATTERN}'\n",
                encoding="utf-8",
            )

            config = load_config(config_path)

        self.assertEqual(
            config.chunking.input_dir,
            (project_root / "data" / "clean").resolve(),
        )
        self.assertEqual(
            config.chunking.output_file,
            (project_root / "data" / "chunks" / "chunks.jsonl").resolve(),
        )


if __name__ == "__main__":
    unittest.main()
