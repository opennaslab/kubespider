#!/bin/sh
pyinstaller -F alist_provider.py --distpath=bin --collect-all=kubespider_source_provider --add-data "./provider.yaml:." --clean
rm -rf ./build alist_provider.spec

echo 'build success, start test'
./bin/alist_provider --host=xxx --cache_path=xxx  --watch_dirs=xxx
