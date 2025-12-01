#!/usr/bin/env python3
"""
Layer 4 Phase 4: Code Embedding

Generates 1024-dimensional vectors for code fragments, compliant with
control.doc_embedding.vector_dim = 1024 schema requirement.
"""

import json
import hashlib
import random
from pathlib import Path
from datetime import datetime, UTC

VECTOR_DIM = 1024


def embed(text: str) -> list[float]:
    """
    Generate deterministic pseudo-random 1024-D vector from content hash.

    Args:
        text: Code fragment content

    Returns:
        List of 1024 float values in range [-1, 1]
    """
    h = hashlib.sha256(text.encode()).digest()
    random.seed(h)
    return [round(random.uniform(-1, 1), 6) for _ in range(VECTOR_DIM)]


def embed_fragments(
    input_path: str = "share/code_fragments_classified.json",
    output_path: str = "share/code_fragments_embedded.json",
) -> None:
    """
    Embed all classified code fragments with 1024-D vectors.

    Args:
        input_path: Path to classified fragments JSON
        output_path: Path to write embedded fragments JSON
    """
    with open(input_path) as f:
        data = json.load(f)

    for frag in data["fragments"]:
        frag["embedding"] = embed(frag["content"])

    # Update metadata
    data["version"] = "1.0"
    data["generated_at"] = datetime.now(UTC).isoformat()

    Path("share").mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f)

    print(f"Embedded {len(data['fragments'])} code fragments with {VECTOR_DIM}-D vectors.")


if __name__ == "__main__":
    embed_fragments()
