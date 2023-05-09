import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as dec

from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm import Session
from typing import Union, Callable

__factory: Union[Callable, None] = None
SqlAlchemyBase = dec.declarative_base()


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("no db file name")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"connecting to {conn_str}")

    engine = create_async_engine(conn_str, echo=False, pool_size=30, max_overflow=0)
    __factory = async_sessionmaker(engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
