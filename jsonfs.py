#!/usr/bin/env python3

import sys
import os
import json
import threading
import errno
import time, datetime

from fuse import FUSE, FuseOSError, Operations

class JSONFS(Operations):
    def _get_time():
        return time.mktime(datetime.datetime.now().timetuple())

    def __init__(self, storage_file_path):
        self.storage_file_path = storage_file_path
        if not os.path.exists(self.storage_file_path):
            storage_file = open(self.storage_file_path, 'w+')
            json.dump({"attrs" : { "st_size" : 4096, "st_mode" : 16877,
                "st_uid" : os.getuid(), "st_gid" : os.getgid(), "st_atime" :
                0, "st_ctime" : JSONFS._get_time(),
                "st_mtime" : JSONFS._get_time() },
                "children" : []}, storage_file)
            storage_file.flush()
        self.fd = 0
        self.rwlock = threading.Lock()

    def readdir(self, path, fh):
        dir_contents = [".", ".."]
        with self.rwlock:
            storage_file = open(self.storage_file_path)
            json_obj = json.load(storage_file)
            internal_path = path.split("/")
            for component in internal_path:
                for child in json_obj["children"]:
                    if component == child["name"]:
                        json_obj = child["children"]
            for i in json_obj["children"]:
                dir_contents.append(i["name"])
            storage_file.close()
        print(dir_contents)
        for i in dir_contents:
            yield i

    def getattr(self, path, fh):
        with self.rwlock:
            storage_file = open(self.storage_file_path)
            json_obj = json.load(storage_file)
            internal_path = path.split("/")
            for component in internal_path:
                for child in json_obj["children"]:
                    if component == child["name"]:
                        json_obj = child["children"]
            out = dict((key, json_obj["attrs"][key])
                    for key in json_obj["attrs"])
            print(out)
            for key in json_obj["attrs"]:
                print(key)
            print(json_obj)
            return dict((key, json_obj["attrs"][key]) for key in
                    json_obj["attrs"])

    def create(self, path, mode):
        internal_path = path.split("/")[1:]
        storage_file = open(self.storage_file_path)
        with self.rwlock: 
            json_obj = json.load(storage_file)
            full_json_obj = json_obj
            for component in internal_path[:-1]:
                print("comp: " + component)
                for child in json_obj["children"]:
                    if component == child["name"]:
                        json_obj = child["children"]
                    elif component != internal_path[-2]:
                        raise FuseOSError(errno.ENOENT)
            new_obj = dict()
            new_obj["name"] = internal_path[-1]
            new_obj["type"] = "f"
            new_obj["contents"] = ""
            new_obj["attrs"] = {}
            new_obj["attrs"]["st_mode"] = mode
            new_obj["attrs"]["st_nlink"] = 0
            new_obj["attrs"]["st_uid"] = os.getuid()
            new_obj["attrs"]["st_gid"] = os.getgid()
            new_obj["attrs"]["st_size"] = 0
            new_obj["attrs"]["st_atime"] = 0
            new_obj["attrs"]["st_ctime"] = JSONFS._get_time() 
            new_obj["attrs"]["st_mtime"] = JSONFS._get_time() 
            json_obj.append(new_obj)
            storage_file.close()
            storage_file = open(self.storage_file_path, "w")
            json.dump(full_json_obj, storage_file)
            storage_file.close()
        self.fd += 1
        return self.fd

    def read(self, path, length, offset, fh):
        with self.rwlock:
            storage_file = open(self.storage_file_path)
            json_obj = json.load(storage_file)
            internal_path = path.split("/")[1:]
            print(internal_path)
            for component in internal_path:
                for child in json_obj["children"]:
                    if component == child["name"]:
                        json_obj = child["children"]
                    elif component != internal_path[-2]:
                        raise FuseOSError(errno.ENOENT)
            print(json_obj)
            return json_obj["contents"][offset:offset + length]

def main(mountpoint, storage_file_path):
    FUSE(JSONFS(storage_file_path), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    import logging
    logger = logging.getLogger('fuse.log-mixin')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    main(sys.argv[2], sys.argv[1])
