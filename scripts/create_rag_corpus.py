"""Script to create a serverless Vertex AI RAG corpus and import ESPN Draft Kits."""

import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-04-fbbe43b35f44"
LOCATION = "us-central1"  # Serverless RAG corpus must be in us-central1
GCS_PATH = "gs://fantasy-football-assets-qwiklabs-gcp-04/rag/"

PARSING_PROMPT = (
    "Extract all fantasy football rankings, player tiers, projections, PPR data, "
    "and cheat sheet information from this draft kit document. "
    "Maintain player names, positions, teams, and ranking order accurately."
)


def main():
    print(f"Initializing Vertex AI for project={PROJECT_ID}, location={LOCATION}...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print("Setting RAG Engine config to serverless mode...")
    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    try:
        rag.update_rag_engine_config(
            rag_engine_config=rag.RagEngineConfig(
                name=cfg,
                rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
            )
        )
        print("✓ Serverless RAG Engine mode configured.")
    except Exception as e:
        print(f"Notice during update_rag_engine_config: {e}")

    print("Creating serverless RAG corpus 'fantasy-draft-kit-corpus'...")
    corpus = rag.create_corpus(
        display_name="fantasy-draft-kit-corpus",
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    print(f"✓ Created RAG Corpus: {corpus.name}")

    print(f"Importing and indexing files from {GCS_PATH}...")
    resp = rag.import_files(
        corpus_name=corpus.name,
        paths=[GCS_PATH],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-2.5-flash",
            custom_parsing_prompt=PARSING_PROMPT,
        ),
    )
    print(f"✓ Imported {resp.imported_rag_files_count} files into corpus {corpus.name}.")

    # Save corpus name to a text file for the agent to reference
    with open("rag_corpus_name.txt", "w") as f:
        f.write(corpus.name)
    print(f"Saved corpus resource name to 'rag_corpus_name.txt': {corpus.name}")


if __name__ == "__main__":
    main()
