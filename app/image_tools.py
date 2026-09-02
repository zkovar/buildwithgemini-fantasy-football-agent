"""Image generation tools for Fantasy Football agent using gemini-3.1-flash-lite-image."""

import uuid
from typing import Any
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-04-fbbe43b35f44"
BUCKET_NAME = "fantasy-football-assets-qwiklabs-gcp-04"


async def generate_player_welcome_banner(
    player_name: str,
    team_name: str = "My Squad",
    tool_context: ToolContext = None,
) -> dict[str, Any]:
    """Generate a custom 'WELCOME TO THE SQUAD' welcome banner image for a newly drafted fantasy football player using gemini-3.1-flash-lite-image in the global region.

    Args:
        player_name: Name of the drafted player (e.g., 'Christian McCaffrey', 'CeeDee Lamb').
        team_name: Name of the fantasy team welcoming the player (e.g., 'My Squad').
        tool_context: Optional ADK tool context for artifact saving in Playground.

    Returns:
        Dictionary containing the public Cloud Storage image URL, welcome message, and metadata.
    """
    prompt = (
        f"A dramatic, high-energy fantasy football welcome banner graphic celebrating player '{player_name}'. "
        f"Includes dynamic stadium lighting, team colors, and prominent bold stylized header text that says 'WELCOME TO THE SQUAD'."
    )

    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )

    part = response.candidates[0].content.parts[0]
    image_bytes = part.inline_data.data
    mime_type = part.inline_data.mime_type or "image/jpeg"

    # 1. Save artifact in Playground's Artifacts panel if tool_context is present
    filename = f"welcome_banner_{player_name.lower().replace(' ', '_')}.jpg"
    if tool_context is not None:
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            await tool_context.save_artifact(filename=filename, artifact=artifact_part)
        except Exception as e:
            print(f"Notice during save_artifact: {e}")

    # 2. Upload image bytes to public Cloud Storage bucket and return public https URL
    object_name = f"welcome_banners/{uuid.uuid4().hex[:8]}_{filename}"
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"

    return {
        "status": "success",
        "player_name": player_name,
        "team_name": team_name,
        "welcome_message": f"WELCOME TO THE SQUAD, {player_name}!",
        "image_url": public_url,
        "gcs_bucket": BUCKET_NAME,
        "filename": filename,
    }
