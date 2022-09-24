"""SQL database init."""

import sys

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from gdrive import DATABASE_URL, LOGGER


def start() -> scoped_session:
    try:
        engine = create_engine(DATABASE_URL)
        BASE.metadata.bind = engine
        BASE.metadata.create_all(engine)
        return scoped_session(sessionmaker(bind=engine, autoflush=False))
    except ValueError:
        LOGGER.error("Invalid DATABASE_URL : Exiting now.")
        sys.exit(1)


BASE = declarative_base()
try:
    SESSION: scoped_session = start()
except Exception as e:
    LOGGER.error(f"Failed to connect to DATABASE_URL: {e}")
    sys.exit()
