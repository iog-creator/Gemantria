import numpy as np
from agentpm.adapters.lm_studio import embed


def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def run_experiment():
    query = "Always use DMS first"

    # Case 1: Exact short match
    short_doc = "Rule 069: Always use DMS first for planning queries."

    # Case 2: Diluted long match (simulating a full file)
    noise = " This is unrelated text about python functions and database schemas. " * 500
    long_doc = short_doc + noise

    print(f"Query: '{query}'")
    print("-" * 50)

    # Generate embeddings
    print("Generating embeddings...")
    vec_query = embed(query)[0]
    vec_short = embed(short_doc)[0]
    vec_long = embed(long_doc)[0]

    # Calculate similarities
    sim_short = cosine_similarity(vec_query, vec_short)
    sim_long = cosine_similarity(vec_query, vec_long)

    print(f"Similarity (Short Doc): {sim_short:.4f}")
    print(f"Similarity (Long Doc):  {sim_long:.4f}")

    if sim_short > 0.5 and sim_long < 0.3:
        print("\nCONCLUSION: Document dilution is the culprit. Chunking is required.")
    else:
        print("\nCONCLUSION: Dilution might not be the only factor. Investigate further.")


if __name__ == "__main__":
    run_experiment()
