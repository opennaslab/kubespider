#! /bin/sh
python3 setup.py sdist
rm -rf ./kubespider_source_provider_manager.egg-info
pip install ./dist/kubespider-source-provider-manager-0.1.0.tar.gz