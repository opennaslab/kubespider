# Used to define the api types in the project


class FileType:
    common = "common"
    general = "general"
    tv = "tv"
    movie = "movie"
    video_mixed = "video_mixed"
    video_9kg = "video_9kg"
    music = "music"
    picture = "picture"
    document = "document"

    @classmethod
    def types(cls) -> list:
        return [
            cls.common, cls.general, cls.tv, cls.movie, cls.video_mixed,
            cls.video_9kg, cls.music, cls.picture, cls.document
        ]


class LinkType:
    general = "general"
    magnet = "magnet"
    torrent = "torrent"

    @classmethod
    def types(cls) -> list:
        return [cls.general, cls.magnet, cls.torrent]


class ProviderTypes:
    parser = "parser"
    search = "search"
    scheduler = "scheduler"

    @classmethod
    def types(cls) -> list:
        return [cls.parser, cls.search, cls.scheduler]


class PluginTypes:
    parser = "parser"
    search = "search"
    scheduler = "scheduler"

    @classmethod
    def types(cls) -> list:
        return [cls.parser, cls.search, cls.scheduler]
