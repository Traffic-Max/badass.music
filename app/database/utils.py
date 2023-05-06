from .models import db


async def get_db_session(database_url: str):
    await db.set_bind(database_url)


async def drop_tables(database_url: str):
    await db.set_bind(database_url)
    await db.gino.drop_all() # type: ignore
    


async def create_tables(database_url: str):
    await db.set_bind(database_url)
    await db.gino.create_all() # type: ignore
    
    