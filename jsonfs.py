#!/usr/bin/env python3

import sys
import os
import json
import threading
import errno

from fuse import FUSE, FuseOSError, Operations

class JSONFS(Operations):
    def __init__(self, storage_file_path):
        self.storage_file_path = storage_file_path
        if not os.path.exists(self.storage_file_path):
            storage_file = open(self.storage_file_path, 'w+')
            json.dump([], storage_file)
            storage_file.flush()
        self.fd = 0
        self.rwlock = threading.Lock()

    def create(self, path, mode):
        internal_path = path.split("/")[1:]
        storage_file = open(self.storage_file_path)
        with self.rwlock: 
            json_obj = json.load(storage_file)
            full_json_obj = json_obj
            for component in internal_path[:-1]:
                print("comp: " + component)
                for child in json_obj:
                    if component == child["name"]:
                        json_obj = child["children"]
                    elif component != internal_path[-2]:
                        raise FuseOSError(errno.ENOENT)
            new_obj = dict()
            new_obj["name"] = internal_path[-1]
            new_obj["mode"] = mode
            new_obj["contents"] = ""
            json_obj.append(new_obj)
            storage_file.close()
            storage_file = open(self.storage_file_path, "w")
            json.dump(full_json_obj, storage_file)
            storage_file.close()
        self.fd += 1
        return self.fd

def main(mountpoint, storage_file_path):
    FUSE(JSONFS(storage_file_path), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
