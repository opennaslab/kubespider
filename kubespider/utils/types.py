# Used to define the api types in the project


class LinkType:
    general = "general"
    magnet = "magnet"
    torrent = "torrent"


class FileType:
    common = "common"
    general = "general"
    tv = "tv"
    movie = "movie"
    video_mixed = "video_mixed"
    music = "music"
    picture = "picture"
    pt = "pt"
    document = "document"
    text = "text"

    @classmethod
    def types(cls) -> list:
        return [
            cls.common, cls.general, cls.tv, cls.movie, cls.video_mixed, cls.music, cls.picture, cls.pt,
            cls.document, cls.text
        ]


class ProviderType:
    download_provider = "DownloadProvider"
    source_provider = "SourceProvider"
    notification_provider = "NotificationProvider"

    @classmethod
    def provider_types(cls):
        return [cls.download_provider, cls.notification_provider, cls.source_provider]


class SignalsType:
    reload_download_provider = "reload_download_provider"
    reload_notification_provider = "reload_notification_provider"
    reload_source_manager = "reload_source_provider"
    update_provider_instance_conf = "update_provider_instance_conf"


class ParamsType:
    str = str
    list = list
    int = int
    bool = bool
    dict = dict

    @classmethod
    def type_to_string(cls, _type):
        return _type.__name__

    @classmethod
    def sting_to_type(cls, string):
        return getattr(cls, string)


class States:
    initial = 'initial'
    download = 'download'
    archive = 'archive'
    final = 'final'


class DownloadStates:
    progress = "progress"
    paused = "paused"
    cancel = "cancel"
    complete = "complete"
    fail = "fail"

    @classmethod
    @property
    def download_states(cls):
        return [cls.progress, cls.paused, cls.cancel, cls.complete, cls.fail]


class FinalStates:
    finish = 'finish'
    error = 'error'

    @classmethod
    @property
    def final_states(cls):
        return [cls.finish, cls.error]


class StateMachineEvent:
    # start state machine
    start = 'start'
    # stop state machine
    stop = 'stop'
    # download resource
    download = 'download'
    # pause download task
    pause = 'pause'
    # cancel download task
    cancel = 'cancel'
    # download fail
    fail = 'fail'
    # download complete
    complete = 'complete'
    # download provider disconnect
    disconnect = 'disconnect'
    # state machine finish
    finish = 'finish'
    # state machine exit with exception
    error = 'error'

    @classmethod
    @property
    def allow_user_trigger_event(cls):
        return [cls.stop, cls.pause, cls.cancel]


class WSActionType:
    init__connect = "init_connect"

