from models import Base, engine, session_context
from models.migrate.init import init_download_table, init_notification_table


def init(session):
    Base.metadata.create_all(engine)
    init_download_table(session)
    init_notification_table(session)


def migrate():
    with session_context() as session:
        init(session)
