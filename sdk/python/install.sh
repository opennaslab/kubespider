#! /bin/sh

# Echo logo
cat <<"EOF"
 _          _                     _     _
| | ___   _| |__   ___  ___ _ __ (_) __| | ___ _ __
| |/ / | | | '_ \ / _ \/ __| '_ \| |/ _` |/ _ \ '__|
|   <| |_| | |_) |  __/\__ \ |_) | | (_| |  __/ |
|_|\_\\__,_|_.__/ \___||___/ .__/|_|\__,_|\___|_|
                           |_|  
EOF

python3 setup.py sdist
rm -rf ./kubespider_source_provider_sdk.egg-info
pip install ./dist/kubespider-source-provider-sdk-0.1.0.tar.gz
