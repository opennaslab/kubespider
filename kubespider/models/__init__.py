from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.global_config import APPConfig
from .models import Base, Download, Notification


@contextmanager
def session_context():
    session = sessionmaker(bind=engine)()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


engine = create_engine(APPConfig.SQLALCHEMY_DATABASE_URI)
