import sqlalchemy.ext.declarative as dec

from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm import Session
from typing import Union, Callable

__factory: Union[Callable, None] = None
SqlAlchemyBase = dec.declarative_base()


async def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("no db file name")

    conn_str = f'sqlite+aiosqlite:///{db_file.strip()}?check_same_thread=False'

    engine = create_async_engine(conn_str, echo=False)
    __factory = async_sessionmaker(engine)

    from . import __all_models

    async with engine.begin() as conn:
        await conn.run_sync(SqlAlchemyBase.metadata.drop_all)
        await conn.run_sync(SqlAlchemyBase.metadata.create_all)


def create_session() -> Session:
    global __factory
    return __factory()
