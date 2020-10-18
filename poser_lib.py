"""
Project Name: Trigger
File name: poser_lib.py
Licence: MIT LICENCE
Author : altnoi
Last update: 2020_09_24
INFORMATION:
This code is PoC. It is subject to change from the production version specifications.
"""

import maya.cmds as cmds

import os
import json
import copy
import re

DEFAULT_DIR = cmds.workspace(q=True, active=True)
DIRECTORY = os.path.join(DEFAULT_DIR, 'pose_lib')

APP_SETTINGS = {"name": "alt-poser", "version": "1.0.5"}
NG_ATTRS = {"visibility"}


def create_directory(directory=DIRECTORY):
    if not os.path.exists(directory):
        os.makedirs(directory)


class PoserLibrary(dict):
    def save(self, directory=DIRECTORY, name="untitled", **info):
        create_directory(directory)
        infoFile = os.path.join(directory, '%s.json' % name)

        # get content
        items = cmds.ls(selection=True)
        DONE_LIST = []
        NOW = cmds.currentTime(q=True)
        ELEMENT = {}
        ATTR_VALUE = {}

        for item in items:
            keyitems = cmds.keyframe(item, q=True, name=True)
            ATTR_VALUE.clear()
            if keyitems is not None:
                for keyitem in keyitems:
                    if keyitem not in DONE_LIST:
                        if '|' in item:
                            true_item = item.rsplit('|', 1)[1]
                            attr_name = keyitem.replace('%s_' % true_item, '')
                        else:
                            attr_name = keyitem.replace('%s_' % item, '')

                        # bug-fix: 1-Avoid last number, 2-block "1." when it placed on after "_"
                        t2 = re.search(r'(?<![_\d])\d+$', attr_name)
                        if t2 is not None:
                            attr_name = attr_name.rstrip(t2.group())

                        DONE_LIST.append(keyitem)
                        value = cmds.keyframe(keyitem, time=(NOW, NOW), vc=True, q=True)
                        ATTR_VALUE[attr_name] = value
            ELEMENT[item] = copy.copy(ATTR_VALUE)

        JSON_BASE = {"imagepath": "testdir", "value": ELEMENT, "appsettings": APP_SETTINGS}

        with open(infoFile, 'w') as f:
            json.dump(JSON_BASE, f, indent=4)

    def find(self, directory=DIRECTORY):
        self.clear()
        if not os.path.exists(directory):
            return

        files = os.listdir(directory)
        jsonfiles = [f for f in files if f.endswith('.json')]

        for jsonfile in jsonfiles:
            name, ext = os.path.splitext(jsonfile)
            fullpath = os.path.join(directory, jsonfile)

            with open(fullpath, 'r') as f:
                info = json.load(f)

            info['name'] = name
            info['path'] = fullpath

            self[name] = info

    def load(self, fpath=""):
        if os.path.exists(fpath):
            with open(fpath, 'r') as f:
                content = json.load(f)
                if content['appsettings']['name'] == "alt-poser":
                    for key in content['value']:
                        for attr in content['value'][key]:
                            for value in content['value'][key][attr]:
                                if value is not None:
                                    cmds.select(clear=True)
                                    cmds.select(key)
                                    c = cmds.setKeyframe(v=value, at=attr)
                                    if c == 0:
                                        print key
                                        print value
                                        print attr
                                        print "fail"
                                        print "\n"

                else:
                    print("This is not alt-poser file!!!")

    def rename(self, old_name="", new_name="", directory=DIRECTORY):
        status = 0
        if not (old_name == "" or new_name == ""):
            o_fullpath = os.path.join(directory, '%s.json' % old_name)
            n_fullpath = os.path.join(directory, '%s.json' % new_name)
            if not os.path.exists(n_fullpath):
                os.rename(o_fullpath, n_fullpath)
            else:
                status = 1
            return status

    def change_image(self, fpath="", ipath=""):
        if not (fpath == "" or ipath == ""):
            content = {}
            with open(fpath, 'r') as f:
                content.update(json.load(f))
                content['imagepath'] = ipath

            with open(fpath, 'w') as f:
                json.dump(content, f, indent=4)
