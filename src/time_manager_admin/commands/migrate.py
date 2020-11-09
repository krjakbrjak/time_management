import os
from argparse import ArgumentParser, Namespace

import alembic.config

from time_manager_admin.base_command import BaseCommand


class MigrateCommand(BaseCommand):
    """Applies migration to the database."""

    def __init__(self):
        super().__init__(name="migrate")

    def add_arguments_to_parser(self, p: ArgumentParser) -> ArgumentParser:
        parser = super().add_arguments_to_parser(p)
        parser.add_argument(
            "--config",
            type=str,
            help="Path to db config",
        )

        return parser

    def run(self, args: Namespace):
        here = os.path.dirname(os.path.abspath(__file__))
        if args.config is not None:
            os.environ.update({"DB_CONFIG_PATH": args.config})

        alembic_args = ["-c", os.path.join(here, "alembic.ini"), "upgrade", "head"]

        alembic.config.main(argv=alembic_args)
