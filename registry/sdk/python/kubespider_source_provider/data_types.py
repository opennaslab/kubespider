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


class ParamType:
    str = str
    list = list
    int = int
    bool = bool
    dict = dict


class ProviderInstanceType:
    single = 'single'
    multi = 'multi'


class HttpApi:
    search = "search"
    schedule = "schedule"
    handler = "handler"
    document = "document"

    @staticmethod
    def get_paths():
        return ["search", "schedule", "handler", "document"]
