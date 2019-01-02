#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author  : Hu Ji
@file    : at_grep.py 
@time    : 2018/12/25
@site    :  
@software: PyCharm 

              ,----------------,              ,---------,
         ,-----------------------,          ,"        ,"|
       ,"                      ,"|        ,"        ,"  |
      +-----------------------+  |      ,"        ,"    |
      |  .-----------------.  |  |     +---------+      |
      |  |                 |  |  |     | -==----'|      |
      |  | $ sudo rm -rf / |  |  |     |         |      |
      |  |                 |  |  |/----|`---=    |      |
      |  |                 |  |  |   ,/|==== ooo |      ;
      |  |                 |  |  |  // |(((( [33]|    ,"
      |  `-----------------'  |," .;'| |((((     |  ,"
      +-----------------------+  ;;  | |         |,"
         /_)______________(_/  //'   | +---------+
    ___________________________/___  `,
   /  oooooooooooooooo  .o.  oooo /,   \,"-----------
  / ==ooooooooooooooo==.o.  ooo= //   ,`\--{)B     ,"
 /_==__==========__==_ooo__ooo=_/'   /___________,"
"""

# !/usr/bin/python

# -*- coding: utf-8 -*-
import argparse
import os
import re
import shutil
import zipfile

import magic
from colorama import Fore

import android_tools
from android_tools import utils, file_matcher


class grep_matcher(file_matcher):

    def __init__(self, filename: str, pattern):
        super().__init__(filename)
        self.pattern = pattern
        self.handler = {
            "application/zip": self.on_zip,
            "application/x-gzip": self.on_zip,
            "application/java-archive": self.on_zip,
            "text/plain": self.on_text,
        }

    def on_file(self, filename: str):
        try:
            mime = magic.from_file(filename, mime=True)
            handler = utils.item(self.handler, mime)
            if handler is not None:
                handler(filename)
                return
        except:
            pass
        try:
            self.on_binary(filename)
        except Exception as e:
            # print(filename, e)
            pass

    def on_zip(self, filename: str):
        dirname = filename + ":"
        while os.path.exists(dirname):
            dirname = dirname + " "
        try:
            zip_file = zipfile.ZipFile(filename, "r")
            zip_file.extractall(dirname)
            self.on_dir(dirname)
        finally:
            shutil.rmtree(dirname, ignore_errors=True)

    def on_text(self, filename: str):
        with open(filename, "rb") as fd:
            lines = fd.readlines()
            for i in range(0, len(lines)):
                out, last, line = "", 0, lines[i].rstrip(b"\n")
                for match in self.pattern.finditer(line):
                    out = out + Fore.RESET + str(line[last:match.span()[0]], encoding = "utf-8")
                    out = out + Fore.RED + str(line[match.span()[0]:match.span()[1]], encoding = "utf-8")
                    last = match.span()[1]
                if not utils.empty(out):
                    print(Fore.BLUE + filename +
                          Fore.RESET + ":" + Fore.GREEN + str(i + 1) +
                          Fore.RESET + ": " + out +
                          Fore.RESET + str(line[last:], encoding = "utf-8"))

    def on_binary(self, filename: str):
        with open(filename, "rb") as fd:
            for line in fd.readlines():
                if self.pattern.search(line) is not None:
                    print(Fore.BLUE + filename + Fore.RESET + ": binary file match")
                    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='match files with regular expression')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + android_tools.__version__)

    parser.add_argument('pattern', action='store', default=None,
                        help='regular expression')
    parser.add_argument('files', metavar="file", action='store', nargs='*', default=None,
                        help='target files path')
    parser.add_argument('-i', '--ignore-case', action='store_true', default=False,
                        help='ignore case')

    args = parser.parse_args()

    flags = 0
    if args.ignore_case:
        flags = flags | re.I
    pattern = re.compile(bytes(args.pattern, encoding="utf8"), flags=flags)

    if utils.empty(args.files):
        args.files = ["."]

    for file in args.files:
        grep_matcher(file, pattern).match()
