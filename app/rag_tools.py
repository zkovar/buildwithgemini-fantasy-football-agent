"""RAG retrieval tool for ESPN Fantasy Football Draft Kits."""

import vertexai
from vertexai.preview import rag

PROJECT_ID = "qwiklabs-gcp-04-fbbe43b35f44"
RAG_LOCATION = "us-central1"
CORPUS_NAME = "projects/103761399075/locations/us-central1/ragCorpora/5100352966276153344"


def consult_draft_kit(query: str) -> str:
    """Search the ESPN Fantasy Football Draft Kit corpus (PPR rankings, cheat sheets, targets, sleepers) and return matched passages.

    Args:
        query: What to look up in the draft kit (e.g., 'top PPR wide receivers', 'Schefter picks to target', 'Do Not Draft list').

    Returns:
        Matched passages from the draft kit documents, or a message if no relevant passage was found.
    """
    try:
        vertexai.init(project=PROJECT_ID, location=RAG_LOCATION)
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=CORPUS_NAME)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
    except Exception as e:
        return f"Draft kit retrieval failed: {e}"

    contexts = getattr(resp.contexts, "contexts", [])
    passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
    if not passages:
        return "No relevant draft kit information found for your query."

    return "\n\n---\n\n".join(passages)
