"""
Seed script — loads the same mock data used by the API into real MongoDB
collections, so you can point routers at Mongo instead of mock_data.py
without changing what the frontend sees.

Run it with:  python -m scripts.seed
(requires MONGODB_URI to be set in backend/.env, pointing at a real cluster
 or a local `mongod` instance)
"""

import asyncio

from app.db import get_db
from app.mock_data import AGENT_ACTIVITY, RESOURCES


async def seed():
    db = get_db()

    await db.resources.delete_many({})
    await db.resources.insert_many([r.model_dump() for r in RESOURCES])
    print(f"Seeded {len(RESOURCES)} resources")

    await db.agent_activity.delete_many({})
    await db.agent_activity.insert_many([a.model_dump() for a in AGENT_ACTIVITY])
    print(f"Seeded {len(AGENT_ACTIVITY)} agent activity entries")

    print("Done. Point your routers at these collections instead of mock_data.py when you're ready.")


if __name__ == "__main__":
    asyncio.run(seed())
