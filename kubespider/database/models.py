from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from api.values import Task

db = SQLAlchemy()


class DownloadTasks(db.Model):
    __tablename__ = 'download_tasks'
    # task uid
    task_id = db.Column(db.String(80), primary_key=True)
    # download provider task id, used to query/delete download task
    download_provider_task_id = db.Column(db.String(120), nullable=True, default=None)
    title = db.Column(db.String(80), nullable=True)
    desc = db.Column(db.Text(), nullable=True)
    file_size = db.Column(db.Float, nullable=True)  # size GB
    file_type = db.Column(db.String(80), nullable=True)
    download_path = db.Column(db.String(120), nullable=True)
    complete = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    download_provider_id = db.Column(db.Integer, db.ForeignKey("download_providers.id"), nullable=True)
    source_provider_id = db.Column(db.Integer, db.ForeignKey("source_providers.id"), nullable=True)

    @classmethod
    def create_or_update(cls, session, *tasks: [Task]) -> db.Model:
        instances = []
        for task in tasks:
            instance = session.query(cls).filter_by(task_id=task.uid).first()
            if not instance:
                instance = cls()
            ...
            instances.append(instance)
        session.add(instances)
        session.commit()

    def __repr__(self):
        return f"<DownloadTasks {self.title}>"


class SeedingTasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    download_task_id = db.Column(db.Integer, db.ForeignKey("download_tasks.task_id"), nullable=False)
    upload_size = db.Column(db.String(20), default="0")  # size GB
    last_update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class DownloadProviders(db.Model):
    __tablename__ = 'download_providers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(80), nullable=False)
    enable = db.Column(db.Boolean(), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    config = db.Column(db.Text, nullable=False)


class SourceProviders(db.Model):
    __tablename__ = 'source_providers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(80), nullable=False)
    enable = db.Column(db.Boolean(), nullable=False)
    config = db.Column(db.Text, nullable=False)


class NotificationProviders(db.Model):
    __tablename__ = 'notification_providers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(80), nullable=False)
    enable = db.Column(db.Boolean(), nullable=False)
    config = db.Column(db.Text, nullable=False)
