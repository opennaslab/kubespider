# Used to define the general values used in the project

import os
from enum import Enum

from api import types


FILE_TYPE_TO_PATH = {
    types.FILE_TYPE_COMMON: "Common",
    types.FILE_TYPE_VIDEO_TV: "TV",
    types.FILE_TYPE_VIDEO_MOVIE: "Movie",
    types.FILE_TYPE_VIDEO_MIXED: "VideoMixed",
    types.FILE_TYPE_MUSIC: "Music",
    types.FILE_TYPE_PICTIRE: "Picture",
    types.FILE_TYPE_PT: "PT"
}

CFG_BASE_PATH = os.path.join(os.getenv('HOME'), '.config/')
CFG_TEMPLATE_PATH = os.path.join(os.getenv('HOME'), '.config_template/')

class Config(str, Enum):
    SOURCE_PROVIDER = 'source_provider.yaml'
    DOWNLOAD_PROVIDER = 'download_provider.yaml'
    PT_PROVIDER = 'pt_provider.yaml'
    KUBESPIDER_CONFIG = 'kubespider.yaml'
    STATE = 'state.yaml'

    def __str__(self) -> str:
        return str(self.value)

    def config_path(self) -> str:
        return os.path.join(CFG_BASE_PATH, self)
