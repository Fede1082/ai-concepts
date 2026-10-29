from pydantic import BaseModel
import yaml
from enum import Enum
from pydantic import Field
from pathlib import Path 

max_tokens: int = Field(
    default=800,
    gt=127,      # greater than 127
    lt=2049,     # less than 2049
)

class ChunkingStrategy(str, Enum):
    STRUCTURAL = "structural"
    # SEMANTIC = "semantic"  # quando aggiungi in futuro

class ChunkingConfig(BaseModel):
    input_dir: Path
    output_file: Path
    max_tokens: int = Field(default=800, gt=127, lt=2049)
    overlap_tokens: int = 0
    header_pattern: str
    strategy: ChunkingStrategy

class Config(BaseModel):
    chunking: ChunkingConfig

def load_config(path: str | Path) -> Config:
    with Path(path).expanduser().open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # The pipeline YAML names this stage "chunk".
    if "chunking" not in data and "chunk" in data:
        data = {**data, "chunking": data["chunk"]}
    config = Config(**data)
    base_dir = Path(__file__).resolve().parent
    config.chunking.input_dir = (base_dir / config.chunking.input_dir.expanduser()).resolve()
    config.chunking.output_file = (base_dir / config.chunking.output_file.expanduser()).resolve()
    return config
