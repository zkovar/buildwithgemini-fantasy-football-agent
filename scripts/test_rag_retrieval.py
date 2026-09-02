"""Standalone test script for Vertex AI RAG Corpus retrieval."""

import vertexai
from vertexai.preview import rag

PROJECT_ID = "qwiklabs-gcp-04-fbbe43b35f44"
LOCATION = "us-central1"
CORPUS_NAME = "projects/103761399075/locations/us-central1/ragCorpora/5100352966276153344"


def test_retrieval(query: str = "Who is the top PPR wide receiver in the draft kit?"):
    print(f"Testing retrieval query: '{query}'...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    resp = rag.retrieval_query(
        text=query,
        rag_resources=[rag.RagResource(rag_corpus=CORPUS_NAME)],
        rag_retrieval_config=rag.RagRetrievalConfig(top_k=3),
    )

    contexts = getattr(resp.contexts, "contexts", [])
    print(f"Found {len(contexts)} matched passages:")
    for idx, c in enumerate(contexts, 1):
        score = getattr(c, "score", 0.0)
        text = getattr(c, "text", "").strip()
        print(f"\n--- Passage {idx} (Score: {score:.3f}) ---")
        print(text[:300] + ("..." if len(text) > 300 else ""))


if __name__ == "__main__":
    test_retrieval()
