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

PWD=$(cd "$(dirname "$0")";pwd)
APP_PATH=$(dirname $PWD)
SDK_PATH=$APP_PATH/python
PROVIDER_PATH=$APP_PATH/provider
echo "SDK_PATH: $SDK_PATH"
echo "PROVIDER_PATH: $PROVIDER_PATH"

# build & install sdk
cd $SDK_PATH
python setup.py sdist
pip install dist/*.tar.gz
# build provider
cd $PROVIDER_PATH
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi
pyinstaller -F provider.py --distpath=bin --collect-all=kubespider_source_provider_sdk --clean
rm -rf build
rm -rf rm provider.spec