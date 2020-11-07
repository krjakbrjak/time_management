import argparse
import importlib
import pkgutil
from typing import List

import time_manager_admin.commands
from time_manager_admin.base_command import BaseCommand


def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def main():
    """Main entry point for time_manager_admin package.
    See help for more info.
    """

    parser = argparse.ArgumentParser()

    for _, name, _ in iter_namespace(time_manager_admin.commands):
        importlib.import_module(name)

    commands: List[BaseCommand] = []
    subparsers = parser.add_subparsers()
    for command_cls in BaseCommand.subclasses:
        command = command_cls()
        subparser = subparsers.add_parser(command.name, description=command.description)
        command.add_arguments_to_parser(subparser)
        # Setting default value make it possible to distinguish between
        # commands (subparsers).
        subparser.set_defaults(which=command.name)
        commands.append(command)

    args = parser.parse_args()
    if hasattr(args, "which"):
        for i in filter(lambda command: command.name == args.which, commands):
            i.run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
