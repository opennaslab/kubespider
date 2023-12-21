#!/bin/sh
pyinstaller -F mikanani_provider.py --distpath=bin --collect-all=kubespider_source_provider --add-data "./provider.yaml:." --clean
rm -rf ./build mikanani_provider.spec


echo 'build success, start test'
./bin/mikanani_provider --name=mikan --auto_download=false --rss_link=xxx
