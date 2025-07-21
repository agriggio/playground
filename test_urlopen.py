import os, sys
import shutil
import subprocess
import argparse
from urllib.request import urlopen, Request
import tarfile
import tempfile
import io
import glob
import json
import time
import platform
from urllib.error import HTTPError


def get_imageio_releases(auth=None):
    headers = None
    req = Request('https://api.github.com/repos/artpixls/ART-imageio/releases')
    if auth is not None:
        req.add_header('authorization', 'Bearer ' + auth)
        print(f'AUTH IS: {auth}')
    else:
        print('NO AUTH GIVEN')
    with urlopen(req) as f:
        headers = f.headers
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
                        res = Request(asset['browser_download_url'])
                        if auth is not None:
                            res.add_header('authorization', 'Bearer ' + auth)
                        return res
            return None

    print(f'GOT HEADERS:\n{headers}')
    sys.stdout.flush()
    return RelInfo(rel)


def main():
    try:
        imageio = get_imageio_releases(os.getenv('GITHUB_AUTH'))
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
    except HTTPError as e:
        print(f'HTTP ERROR: {e.reason}')
        print(f'HEDERS:\n{e.headers}')
        raise


if __name__ == '__main__':
    print('RUNNING ON PYTHON: ' + sys.executable)
    main()
