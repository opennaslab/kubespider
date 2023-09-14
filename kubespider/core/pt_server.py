# -*- coding: utf-8 -*-

import time
import os
import _thread

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from core import download_trigger, notification_server
from database.models import DownloadTasks, db, SourceProviders
from pt_provider import provider
from pt_provider.provider import Torrent
from utils.config_reader import YamlFileConfigReader
from api.values import Config, FILE_TYPE_TO_PATH, Task, CFG_BASE_PATH
from api.types import FILE_TYPE_PT, LINK_TYPE_TORRENT
from api.values import Resource, Downloader


class PTServer:
    def __init__(self, pt_providers: list) -> None:
        self.pt_providers: list[provider.PTProvider] = pt_providers
        self.state_config = YamlFileConfigReader(Config.STATE.config_path())
        self.session = self.get_db_session()

    @staticmethod
    def get_db_session() -> Session:
        db_uri = f"sqlite:///{os.path.join(CFG_BASE_PATH, 'kubespider.db')}"
        engine = create_engine(db_uri)
        session = sessionmaker(bind=engine)()
        return session

    def run_single_pt(self, current_provider: provider.PTProvider):
        while True:
            provider_name = current_provider.get_provider_name()
            provider_ins = self.session.query(SourceProviders).filter_by(name=provider_name).first()
            download_tasks = self.session.query(DownloadTasks).filter_by(
                source_provider_id=provider_ins.id, is_deleted=False).all()
            download_sum_size = sum([task.file_size for task in download_tasks])
            max_sum_size = current_provider.get_max_sum_size()

            logging.info("PT provider(%s) downloading size is:%f/%s",
                         provider_name, download_sum_size, max_sum_size)

            pt_user = current_provider.get_pt_user()
            passkey = pt_user.passkey
            current_provider.go_attendance(pt_user)

            notification_server.kubespider_notification_server.send_message(
                title=f"[{provider_name}] pt user", **pt_user.data
            )
            if current_provider.need_delete_torrents(max_sum_size=max_sum_size, download_sum_size=download_sum_size):
                delete_torrents = current_provider.filter_torrents_for_deletion(
                    pt_user, max_sum_size, download_sum_size)
                self.trigger_remove_tasks(current_provider, delete_torrents)
            download_torrents = current_provider.filter_torrents_for_download(pt_user)
            logging.info("Filter %d tasks for download", len(download_torrents))
            for torrent in download_torrents:
                if torrent.size + download_sum_size < max_sum_size:
                    torrent.torrent_content = current_provider.download_torrent_file(pt_user, torrent)
                    error = self.trigger_download_tasks(current_provider, torrent)
                    if not error:
                        download_sum_size += torrent.size
                        logging.info('Add one task(%fGB), now is %fGB', torrent.size,
                                     download_sum_size)
            time.sleep(3600)

    def run(self):
        for iter_provider in self.pt_providers:
            _thread.start_new_thread(self.run_single_pt, (iter_provider,))
        while True:
            time.sleep(3600)

    @staticmethod
    def trigger_download_tasks(pt_provider: provider.PTProvider, torrent: Torrent) -> Exception:
        logging.info("Start downloading: %s", torrent)
        download_provider_name = pt_provider.get_download_provider()
        download_path = os.path.join(FILE_TYPE_TO_PATH[FILE_TYPE_PT], download_provider_name)
        resource = torrent.to_download_resource(torrent_content=torrent.torrent_content, download_path=download_path)
        err = download_trigger.kubespider_downloader.download_file(
            resource, Downloader(download_provider_names=[download_provider_name])
        )
        if isinstance(err, Exception):
            logging.error('Download error: %s', err)
        return err

    @staticmethod
    def trigger_remove_tasks(pt_provider: provider.PTProvider, torrents: list) -> list:
        tasks = [t.to_download_task() for t in torrents]
        download_provider_name = pt_provider.get_download_provider()
        return download_trigger.kubespider_downloader.handle_download_remove(
            Downloader(download_provider_names=[download_provider_name]),
            tasks
        )

    def save_state(self, provider_name: str, provider_state: dict):
        all_pt_state = self.state_config.read().get('pt_state', {})
        if all_pt_state is None:
            all_pt_state = {}
        all_pt_state[provider_name] = provider_state
        self.state_config.parcial_update(lambda all_state: all_state.update({'pt_state': all_pt_state}))

    def load_state(self, provider_name: str) -> dict:
        empty_state = {
            'last_start_time': 0,
            'download_sum_size': 0,
            'costs_sum_size': 0,
            'torrent_list': []
        }
        all_pt_state = self.state_config.read().get('pt_state', {})
        if all_pt_state is None:
            return empty_state

        state = all_pt_state.get(provider_name, {})
        if len(state) == 0:
            return empty_state
        return state

    def __del__(self):
        if isinstance(self.session, Session):
            self.session.close()


kubespider_pt_server: PTServer = None
