import asyncio
from gino import Gino
import os

from dotenv import load_dotenv

from models import DJ, Playlist, AudioTrack, PostTemplate, PostCover

load_dotenv()

database_url = str(os.environ.get('DATABASE_URL'))

db = Gino()

async def init_db():
    await db.set_bind(database_url)
    # await db.gino.drop_all() # type: ignore
    # print("Database dropped")
    await db.gino.create_all() # type: ignore
    print("Database created")

if __name__ == "__main__":
    asyncio.run(init_db())
