# Used to define the api types in the project

SOURCE_PROVIDER_PERIOD_TYPE = "period"
SOURCE_PROVIDER_DISPOSABLE_TYPE = "disposable"

LINK_TYPE_GENERAL = "general"
LINK_TYPE_MAGNET = "magnet"
LINK_TYPE_TORRENT = "torrent"

FILE_TYPE_COMMON = "general"
FILE_TYPE_VIDEO_TV = "tv"
FILE_TYPE_VIDEO_MOVIE = "movie"
FILE_TYPE_VIDEO_MIXED = "video_mixed"
FILE_TYPE_MUSIC = "music"
FILE_TYPE_PICTIRE = "picture"
FILE_TYPE_PT = "pt"


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
