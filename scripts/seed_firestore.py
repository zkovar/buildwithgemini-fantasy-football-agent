"""Seed script for Fantasy Football players Firestore collection."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-fbbe43b35f44"
COLLECTION_NAME = "players"

SEED_PLAYERS = [
    {
        "id": "cmc-23",
        "name": "Christian McCaffrey",
        "position": "RB",
        "team": "SF",
        "adp": 1.2,
        "tier": 1,
        "projected_points": 310.5,
        "status": "Available",
        "notes": "Consensus top-3 overall pick. Premier anchor RB for Hero RB strategy.",
    },
    {
        "id": "lamb-88",
        "name": "CeeDee Lamb",
        "position": "WR",
        "team": "DAL",
        "adp": 2.5,
        "tier": 1,
        "projected_points": 295.0,
        "status": "Available",
        "notes": "Elite target monster. First-round WR priority.",
    },
    {
        "id": "hill-10",
        "name": "Tyreek Hill",
        "position": "WR",
        "team": "MIA",
        "adp": 3.8,
        "tier": 1,
        "projected_points": 288.0,
        "status": "Available",
        "notes": "Explosive ceiling. Core WR1 target.",
    },
    {
        "id": "hall-20",
        "name": "Breece Hall",
        "position": "RB",
        "team": "NYJ",
        "adp": 5.1,
        "tier": 1,
        "projected_points": 270.0,
        "status": "Available",
        "notes": "High dual-threat volume. Ideal Hero RB anchor pick.",
    },
    {
        "id": "kelce-87",
        "name": "Travis Kelce",
        "position": "TE",
        "team": "KC",
        "adp": 18.5,
        "tier": 1,
        "projected_points": 215.0,
        "status": "Available",
        "notes": "Position-advantage TE. Target in Round 2-3.",
    },
]


def seed_database():
    print(f"Connecting to Firestore with project_id={PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    print(f"Seeding {len(SEED_PLAYERS)} players into '{COLLECTION_NAME}' collection...")
    for player in SEED_PLAYERS:
        doc_id = player["id"]
        collection_ref.document(doc_id).set(player)
        print(f"  ✓ Added/Updated player: {player['name']} ({player['position']} - {player['team']})")

    print("Seeding complete!")


if __name__ == "__main__":
    seed_database()
