#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author  : Hu Ji
@file    : ATApp.py
@time    : 2019/01/02
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

import colorama
from colorama import Fore, Style, Back

from linktools import utils, logger
from linktools.android import Device, AdbError, AdbArgumentParser, Package, Permission, Component, Activity, Service, \
    Receiver, Provider, IntentFilter


class PrintLevel:
    min = 0
    useless = 100
    normal = 200
    dangerous_normal = 250
    dangerous = 300
    title = 400
    max = 1000


class PrintStream(PrintLevel):

    def __init__(self, max_level=PrintLevel.max, min_level=PrintLevel.min, file=None):
        colorama.init(True)
        self.max = max_level
        self.min = min_level
        self.file = file

    def print(self, text: str = "", indent: int = 0, level=PrintLevel.normal):
        if not self.min <= level <= self.max:
            pass
        elif level == PrintLevel.title:
            logger.info(text, style=Style.BRIGHT, indent=indent)
        elif level == PrintLevel.dangerous:
            logger.info(text, fore=Fore.RED, back=Back.WHITE, style=Style.BRIGHT, indent=indent)
        elif level == PrintLevel.useless:
            logger.info(text, fore=Fore.YELLOW, back=Back.WHITE, style=Style.BRIGHT, indent=indent)
        else:
            logger.info(text, indent=indent)

    def print_line(self):
        logger.info()


class PrintStreamWrapper(PrintLevel):

    def __init__(self, stream: PrintStream, max_level: int = PrintLevel.max, min_level: int = PrintLevel.min):
        self.stream = stream
        self.max_level = max_level
        self.min_level = min_level

    def print(self, text: str = "", indent: int = 0, level=PrintLevel.normal):
        if level > self.max_level:
            level = self.max_level
        elif level < self.min_level:
            level = self.min_level
        self.stream.print(text, indent=indent, level=level)

    def print_line(self):
        self.stream.print_line()

    def create(self, max_level: int = PrintLevel.max, min_level: int = PrintLevel.min):
        if max_level > self.max_level:
            max_level = self.max_level
        elif min_level < self.min_level:
            min_level = self.min_level
        return PrintStreamWrapper(self.stream, max_level=max_level, min_level=min_level)


class PackagePrinter:

    def __init__(self, stream: PrintStream, package: Package):
        self.package = package
        self.max_level = PrintLevel.max if self.package.enabled else PrintLevel.useless
        self.min_level = PrintLevel.min
        self.stream = PrintStreamWrapper(stream, max_level=self.max_level, min_level=self.min_level)

    def print_package(self, indent: int = 0):
        self.stream.print("Package [%s]" % self.package, indent=indent, level=self.stream.title)
        self.stream.print("name=%s" % self.package.appName, indent=indent + 4, level=self.stream.normal)
        self.stream.print("userId=%s" % self.package.userId, indent=indent + 4, level=self.stream.normal)
        self.stream.print("gids=%s" % self.package.gids, indent=indent + 4, level=self.stream.normal)
        self.stream.print("sourceDir=%s" % self.package.sourceDir, indent=indent + 4, level=self.stream.normal)
        self.stream.print("versionCode=%s" % self.package.versionCode, indent=indent + 4, level=self.stream.normal)
        self.stream.print("versionName=%s" % self.package.versionName, indent=indent + 4, level=self.stream.normal)
        self.stream.print("enabled=%s" % self.package.enabled, indent=indent + 4, level=self.stream.normal)
        self.stream.print("system=%s" % self.package.system, indent=indent + 4, level=self.stream.normal)
        self.stream.print("debuggable=%s" % self.package.debuggable, indent=indent + 4,
                          level=self.stream.dangerous if self.package.debuggable else self.stream.normal)
        self.stream.print("allowBackup=%s" % self.package.allowBackup, indent=indent + 4,
                          level=self.stream.dangerous if self.package.allowBackup else self.stream.normal)
        self.stream.print_line()

    def print_requested_permissions(self, indent: int = 4):
        if not utils.is_empty(self.package.requestedPermissions):
            stream = self.stream.create(max_level=PrintLevel.normal)
            self.stream.print("RequestedPermissions:", indent=indent, level=self.stream.title)
            for permission in self.package.requestedPermissions:
                self._print_permission(stream, permission, indent=indent + 4, identity="RequestedPermission")
            self.stream.print_line()

    def print_permissions(self, indent: int = 4):
        if not utils.is_empty(self.package.permissions):
            self.stream.print("Permissions:", indent=indent, level=self.stream.title)
            for permission in self.package.permissions:
                self._print_permission(self.stream, permission, indent=indent + 4, identity="Permission")
            self.stream.print_line()

    def print_activities(self, indent: int = 4):
        if not utils.is_empty(self.package.activities):
            self.stream.print("Activities:", indent=indent, level=self.stream.title)
            for activity in self.package.activities:
                self._print_component(self.stream, activity, indent=indent + 4, identity="Activity")
            self.stream.print_line()

    def print_services(self, indent: int = 4):
        if not utils.is_empty(self.package.services):
            self.stream.print("Services:", indent=indent, level=self.stream.title)
            for service in self.package.services:
                self._print_component(self.stream, service, indent=indent + 4, identity="Service")
            self.stream.print_line()

    def print_receivers(self, indent: int = 4):
        if not utils.is_empty(self.package.receivers):
            self.stream.print("Receivers:", indent=indent, level=self.stream.title)
            for receiver in self.package.receivers:
                self._print_component(self.stream, receiver, indent=indent + 4, identity="Receiver")
            self.stream.print_line()

    def print_providers(self, indent: int = 4):
        if not utils.is_empty(self.package.providers):
            self.stream.print("Providers:", indent=indent, level=self.stream.title)
            for provider in self.package.providers:
                self._print_component(self.stream, provider, indent=indent + 4, identity="Provider")
            self.stream.print_line()

    @staticmethod
    def _print_permission(stream: PrintStreamWrapper, permission: Permission, indent: int = 0, identity: str = None):
        if permission.is_defined():
            stream.print("%s [%s] %s" % (identity, permission, permission.protection), indent=indent,
                         level=stream.dangerous if permission.is_dangerous() else stream.normal)

    @staticmethod
    def _print_component(stream: PrintStreamWrapper, component: Component, indent: int = 0, identity: str = None):
        if not component.enabled:
            description = "disabled"
            level = stream.useless
            stream = stream.create(max_level=stream.useless)
        elif component.is_dangerous():
            description = "exported"
            level = stream.dangerous if component.is_dangerous() else stream.normal
            stream = stream.create(min_level=stream.dangerous_normal)
        else:
            description = "exported" if component.exported else ""
            level = stream.normal
            stream = stream.create(max_level=stream.normal)
        stream.print("%s [%s] %s" % (identity, component, description), indent=indent, level=level)

        if isinstance(component, Activity) or isinstance(component, Service) or isinstance(component, Receiver):
            PackagePrinter._print_permission(stream, component.permission, indent=indent + 4, identity="Permission")
        elif isinstance(component, Provider):
            stream.print("Authority [%s]" % component.authority, indent=indent + 4, level=level)
            PackagePrinter._print_permission(stream, component.readPermission, indent=indent + 4,
                                             identity="ReadPermission")
            PackagePrinter._print_permission(stream, component.writePermission, indent=indent + 4,
                                             identity="writePermission")
            for pattern in component.uriPermissionPatterns:
                stream.print("UriPermissionPattern [%s]" % pattern, indent=indent + 4, level=level)
            for permission in component.pathPermissions:
                stream.print("PathPermission [%s]" % permission, indent=indent + 4,
                             level=stream.dangerous if permission.is_dangerous() else stream.normal)
                PackagePrinter._print_permission(stream, permission.readPermission, indent=indent + 8,
                                                 identity="ReadPermission")
                PackagePrinter._print_permission(stream, permission.writePermission, indent=indent + 8,
                                                 identity="writePermission")

        if not utils.is_empty(component.intents):
            for intent in component.intents:
                PackagePrinter._print_intent(stream, intent, indent=indent + 4, level=level)

    @staticmethod
    def _print_intent(stream: PrintStreamWrapper, intent: IntentFilter, indent: int = 0,
                      level: int = PrintLevel.normal):
        stream.print("IntentFilter:", indent=indent, level=level)
        for action in intent.actions:
            stream.print("Action [%s]" % action, indent=indent + 4, level=level)
        for category in intent.categories:
            stream.print("Category [%s]" % category, indent=indent + 4, level=level)
        for scheme in intent.dataSchemes:
            stream.print("Scheme [%s]" % scheme, indent=indent + 4, level=level)
        for scheme in intent.dataSchemeSpecificParts:
            stream.print("Scheme [%s]" % scheme, indent=indent + 4, level=level)
        for authority in intent.dataAuthorities:
            stream.print("Authority [%s]" % authority, indent=indent + 4, level=level)
        for path in intent.dataPaths:
            stream.print("Path [%s]" % path, indent=indent + 4, level=level)
        for type in intent.dataTypes:
            stream.print("Type [%s]" % type, indent=indent + 4, level=level)


def main():
    parser = AdbArgumentParser(description='fetch application info')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--all', action='store_true', default=False,
                       help='fetch all apps')
    group.add_argument('-t', '--top', action='store_true', default=False,
                       help='fetch top-level app only')
    group.add_argument('-p', '--packages', metavar="pkg", action='store', nargs='+', default=None,
                       help='fetch target apps only')
    group.add_argument('--system', action='store_true', default=False,
                       help='fetch system apps only')
    group.add_argument('--non-system', action='store_true', default=False,
                       help='fetch non-system apps only')

    parser.add_argument('-b', '--basic-info', action='store_true', default=False,
                        help='display basic info only')
    parser.add_argument('-dang', '--dangerous', action='store_true', default=False,
                        help='display dangerous permissions and components only')
    parser.add_argument('-o', '--order-by', metavar="field", action='store', nargs='+', default=['userId', 'name'],
                        choices=['name', 'appName', 'userId', 'sourceDir',
                                 'enabled', 'system', 'debuggable', 'allowBackup'],
                        help='order by target field')

    args = parser.parse_args()
    device = Device(args.parse_adb_serial())

    if args.top:
        packages = device.get_packages(device.get_top_package_name(), basic_info=args.basic_info)
    elif not utils.is_empty(args.packages):
        packages = device.get_packages(*args.packages, basic_info=args.basic_info)
    elif args.system:
        packages = device.get_packages(system=True, basic_info=args.basic_info)
    elif args.non_system:
        packages = device.get_packages(non_system=True, basic_info=args.basic_info)
    else:
        packages = device.get_packages(basic_info=args.basic_info)

    if not utils.is_empty(args.order_by):
        packages = sorted(packages, key=lambda x: [utils.get_item(x, k, default="") for k in args.order_by])

    min_level = PrintLevel.min
    if args.dangerous:
        min_level = PrintLevel.dangerous_normal
    stream = PrintStream(min_level=min_level)

    for package in packages:
        printer = PackagePrinter(stream, package)
        if not args.dangerous:
            printer.print_package()
            printer.print_requested_permissions()
            printer.print_permissions()
            printer.print_activities()
            printer.print_services()
            printer.print_receivers()
            printer.print_providers()
            continue

        if package.is_dangerous():
            printer.print_package()
            if package.has_dangerous_permission():
                printer.print_permissions()
            if package.has_dangerous_activity():
                printer.print_activities()
            if package.has_dangerous_service():
                printer.print_services()
            if package.has_dangerous_receiver():
                printer.print_receivers()
            if package.has_dangerous_provider():
                printer.print_providers()


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError, AdbError) as e:
        logger.error(e)
    except Exception as e:
        logger.error(traceback_error=True)
