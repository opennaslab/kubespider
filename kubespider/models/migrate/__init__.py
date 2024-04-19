from models import Base, engine, get_session
from models.migrate.init import init_download_table, init_notification_table


def init(session):
    Base.metadata.create_all(engine)
    init_download_table(session)
    init_notification_table(session)


def migrate():
    session = get_session()
    init(session)
