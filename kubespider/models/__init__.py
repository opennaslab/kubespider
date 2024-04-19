from utils.global_config import APPConfig
from .models import Base, Download, Notification
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_session():
    return sessionmaker(bind=engine)()


engine = create_engine(APPConfig.SQLALCHEMY_DATABASE_URI)
