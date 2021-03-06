#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author  : Hu Ji
@file    : ATTopApp.py
@time    : 2018/11/25
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

import datetime
import sys

from linktools import utils, logger
from linktools.android import Device, AdbError, AdbArgumentParser


def main():
    parser = AdbArgumentParser(description='show top-level app\'s basic information')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-p', '--package', action='store_const', const=True, default=False,
                       help='show top-level package name')
    group.add_argument('-a', '--activity', action='store_const', const=True, default=False,
                       help='show top-level activity name')
    group.add_argument('--path', action='store_const', const=True, default=False,
                       help='show top-level package path')
    group.add_argument('--kill', action='store_const', const=True, default=False,
                       help='kill top-level package')
    group.add_argument('--apk', metavar='DEST', action='store', type=str, nargs='?', default=".",
                       help='pull top-level apk file')
    group.add_argument('--screen', metavar='DEST', action='store', type=str, nargs='?', default=".",
                       help='capture screen and pull file')

    args = parser.parse_args()
    device = Device(args.parse_adb_serial())

    if args.package:
        logger.info(device.get_top_package_name())
    elif args.activity:
        logger.info(device.get_top_activity_name())
    elif args.path:
        logger.info(device.get_apk_path(device.get_top_package_name()))
    elif args.kill:
        device.shell("am", "force-stop", device.get_top_package_name(), capture_output=False)
    elif "--apk" in sys.argv:
        package_name = device.get_top_package_name()
        logger.info("get top-level package: {}".format(package_name))
        package = utils.get_item(device.get_packages(package_name, basic_info=True), 0)
        if package is not None:
            logger.info("get top-level package path: {}".format(package.sourceDir))
            path = device.get_storage_path("{}_{}.apk".format(package.name, package.versionName))
            dest = args.apk if not utils.is_empty(args.apk) else "."
            device.shell("mkdir", "-p", device.get_storage_path(), capture_output=False)
            device.shell("cp", package.sourceDir, path, capture_output=False)
            device.exec("pull", path, dest, capture_output=False)
            device.shell("rm", path)
    elif "--screen" in sys.argv:
        now = datetime.datetime.now()
        path = device.get_storage_path("screenshot-" + now.strftime("%Y-%m-%d-%H-%M-%S") + ".png")
        dest = args.screen if not utils.is_empty(args.screen) else "."
        device.shell("mkdir", "-p", device.get_storage_path(), capture_output=False)
        device.shell("screencap", "-p", path, capture_output=False)
        device.exec("pull", path, dest, capture_output=False)
        device.shell("rm", path)
    else:
        package = device.get_top_package_name()
        logger.info("package:  ", package)
        logger.info("activity: ", device.get_top_activity_name())
        logger.info("path:     ", device.get_apk_path(package))


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError, AdbError) as e:
        logger.error(e)
    except Exception as e:
        logger.error(traceback_error=True)
