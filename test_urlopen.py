import os, sys
import shutil
import subprocess
import argparse
from urllib.request import urlopen
import tarfile
import tempfile
import io
import glob
import json
import time
import platform


def get_imageio_releases():
    with urlopen(
            'https://api.github.com/repos/artpixls/ART-imageio/releases') as f:
        data = f.read().decode('utf-8')
    rel = json.loads(data)
    def key(r):
        return (r['draft'], r['prerelease'],
                time.strptime(r['published_at'], '%Y-%m-%dT%H:%M:%SZ'))
    class RelInfo:
        def __init__(self, rel):
            self.rels = sorted(rel, key=key, reverse=True)
            
        def asset(self, name):
            for rel in self.rels:
                for asset in rel['assets']:
                    if asset['name'] == name:
                        return asset['browser_download_url']
            return None

    return RelInfo(rel)


def main():
    imageio = get_imageio_releases()
    with urlopen(imageio.asset('ART-imageio.tar.gz')) as f:
        print('downloading ART-imageio.tar.gz from GitHub ...')
        tf = tarfile.open(fileobj=io.BytesIO(f.read()))
        print('unpacking ART-imageio.tar.gz ...')
        tf.extractall('.')
    arch = 'arm64' if platform.machine() == 'x86_64' else 'arm64'
    name = f'ART-imageio-bin-macOS-' + arch
    with urlopen(imageio.asset(f'{name}.tar.gz')) as f:
        print(f'downloading {name}.tar.gz from GitHub ...')
        tf = tarfile.open(fileobj=io.BytesIO(f.read()))
        print(f'unpacking {name} ...')
        tf.extractall('.')


if __name__ == '__main__':
    main()
