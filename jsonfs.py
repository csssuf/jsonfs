#!/usr/bin/env python3

import sys
import os
import io
import json

from fuse import FUSE, FuseOSError, Operations

class JSONFS(Operations):
    def __init__(self, storage_file_path):
        self.storage_file_path = storage_file_path
        if not os.path.exists(self.storage_file_path):
            self.storage_file = open(self.storage_file_path, 'w')
            json.dump([], self.storage_file)
        else:
            self.storage_file = open(self.storage_file_path, 'w')
        self.fd = 0

    def create(self, path, mode):
        jsonpath = path.split("/")[1:]
        self.fd += 1
        return self.fd

def main(mountpoint, storage_file_path):
    FUSE(JSONFS(storage_file_path), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
