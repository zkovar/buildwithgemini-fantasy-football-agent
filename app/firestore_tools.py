"""Firestore tools for Fantasy Football player catalog management."""

from typing import Any
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-fbbe43b35f44"
COLLECTION_NAME = "players"

_db_client: firestore.Client | None = None


def _get_db() -> firestore.Client:
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def get_players(position: str = "", status: str = "") -> list[dict[str, Any]]:
    """Retrieve players from the Firestore database, optionally filtered by position or status.

    Args:
        position: Optional position filter (e.g., 'RB', 'WR', 'QB', 'TE'). Pass empty string for all positions.
        status: Optional status filter (e.g., 'Available', 'Drafted'). Pass empty string for all statuses.

    Returns:
        A list of player dictionaries containing player details.
    """
    db = _get_db()
    query = db.collection(COLLECTION_NAME)

    if position:
        query = query.where("position", "==", position.upper())
    if status:
        query = query.where("status", "==", status.capitalize())

    docs = query.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)

    return results


def get_player_by_id(player_id: str) -> dict[str, Any]:
    """Get details for a specific player by ID from Firestore.

    Args:
        player_id: Unique identifier for the player (e.g., 'cmc-23', 'lamb-88').

    Returns:
        Dictionary containing player details or an error message if not found.
    """
    db = _get_db()
    doc_ref = db.collection(COLLECTION_NAME).document(player_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Player with ID '{player_id}' not found."}

    data = doc.to_dict()
    data["id"] = doc.id
    return data


def update_player_status(
    player_id: str, status: str, notes: str = ""
) -> dict[str, Any]:
    """Update a player's draft status (e.g. 'Drafted' or 'Available') and optional notes in Firestore.

    Args:
        player_id: The ID of the player (e.g., 'cmc-23').
        status: The new status (e.g., 'Drafted', 'Available', 'Target').
        notes: Optional updated notes or strategy commentary for the player.

    Returns:
        Status result dictionary indicating success or failure.
    """
    db = _get_db()
    doc_ref = db.collection(COLLECTION_NAME).document(player_id)

    if not doc_ref.get().exists:
        return {"error": f"Player with ID '{player_id}' does not exist."}

    update_data: dict[str, Any] = {"status": status}
    if notes:
        update_data["notes"] = notes

    doc_ref.update(update_data)
    return {
        "status": "success",
        "message": f"Updated player '{player_id}' status to '{status}'.",
        "player_id": player_id,
    }


def add_player(
    name: str,
    position: str,
    team: str,
    adp: float = 0.0,
    tier: int = 1,
    projected_points: float = 0.0,
    status: str = "Available",
    notes: str = "",
) -> dict[str, Any]:
    """Add a new player document to the Firestore database.

    Args:
        name: Full name of the player (e.g., 'Justin Jefferson').
        position: Player position ('QB', 'RB', 'WR', 'TE').
        team: NFL team abbreviation (e.g., 'MIN').
        adp: Average Draft Position float.
        tier: Ranking tier integer.
        projected_points: Season projected fantasy points float.
        status: Initial status (default 'Available').
        notes: Initial strategy notes.

    Returns:
        Dictionary with creation result and player ID.
    """
    db = _get_db()
    slug = name.lower().replace(" ", "-")
    doc_id = f"{slug}"

    player_doc = {
        "id": doc_id,
        "name": name,
        "position": position.upper(),
        "team": team.upper(),
        "adp": adp,
        "tier": tier,
        "projected_points": projected_points,
        "status": status,
        "notes": notes,
    }

    db.collection(COLLECTION_NAME).document(doc_id).set(player_doc)
    return {
        "status": "success",
        "message": f"Player '{name}' added successfully.",
        "player": player_doc,
    }


def get_player_injury_and_news(player_name: str) -> dict[str, Any]:
    """Fetch injury status, practice participation, and latest news update for an NFL player.

    Args:
        player_name: Full name or last name of the player (e.g., 'Christian McCaffrey', 'CeeDee Lamb', 'Breece Hall').

    Returns:
        Dictionary containing injury status, practice report, recent news, and fantasy impact summary.
    """
    db = _get_db()
    name_clean = player_name.strip().lower()

    # Query matching player from Firestore
    docs = db.collection(COLLECTION_NAME).stream()
    matched_player = None
    for doc in docs:
        p = doc.to_dict()
        p["id"] = doc.id
        if name_clean in p.get("name", "").lower():
            matched_player = p
            break

    # Simulated injury/news database with realistic NFL player reports
    injury_reports = {
        "mccaffrey": {
            "status": "Healthy / Active",
            "injury": "Calf / Achilles (Recovered)",
            "practice_status": "Full Participant",
            "news": "McCaffrey logged full practice reps and is set for full workload as SF's focal point.",
            "fantasy_impact": "High-confidence RB1 start. Elite volume expected.",
        },
        "lamb": {
            "status": "Active",
            "injury": "None",
            "practice_status": "Full Participant",
            "news": "CeeDee Lamb logged full practice reps with Dak Prescott, showing elite chemistry.",
            "fantasy_impact": "Must-start WR1 with top-3 positional ceiling.",
        },
        "hill": {
            "status": "Active",
            "injury": "Thumb (Minor)",
            "practice_status": "Full Participant",
            "news": "Tyreek Hill cleared all medical checks and is fully expected to start without limitations.",
            "fantasy_impact": "Elite WR1 start; game-breaking upside.",
        },
        "hall": {
            "status": "Active",
            "injury": "Knee (Maintenance)",
            "practice_status": "Full Participant",
            "news": "Breece Hall is 100% healthy leading the Jets backfield with heavy target share.",
            "fantasy_impact": "Strong RB1 anchor option.",
        },
        "kelce": {
            "status": "Active",
            "injury": "Knee",
            "practice_status": "Full Participant",
            "news": "Travis Kelce remains Mahomes' top target on third down and red zone packages.",
            "fantasy_impact": "Top-tier TE1 start.",
        },
    }

    report = None
    for key, data in injury_reports.items():
        if key in name_clean:
            report = data
            break

    if not report:
        report = {
            "status": "Active",
            "injury": "None Reported",
            "practice_status": "Full Participant",
            "news": f"No active injury concerns reported for {player_name}. Player is practicing normally.",
            "fantasy_impact": "Expected to play full snap share.",
        }

    response = {
        "player_name": player_name,
        "injury_status": report["status"],
        "injury_details": report["injury"],
        "practice_status": report["practice_status"],
        "latest_news": report["news"],
        "fantasy_impact": report["fantasy_impact"],
    }

    if matched_player:
        response["firestore_id"] = matched_player["id"]
        response["team"] = matched_player.get("team")
        response["position"] = matched_player.get("position")
        doc_ref = db.collection(COLLECTION_NAME).document(matched_player["id"])
        doc_ref.update({
            "injury_status": report["status"],
            "latest_news": report["news"],
        })

    return response

