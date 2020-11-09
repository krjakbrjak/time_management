import json
from argparse import ArgumentParser, Namespace

from time_manager.utils.db import Database, Postgres, Sqlite
from time_manager_admin.base_command import BaseCommand


class GenerateConfigCommand(BaseCommand):
    """Generates a db config file."""

    ENGINES = [
        "sqlite",
        "postgres",
    ]

    def __init__(self):
        super().__init__(name="generate_config")

    def add_arguments_to_parser(self, p: ArgumentParser) -> ArgumentParser:
        parser = super().add_arguments_to_parser(p)
        parser.add_argument(
            "--db",
            type=str,
            choices=self.ENGINES,
            default=self.ENGINES[0],
            help="Type of the database",
        )
        parser.add_argument(
            "--name", type=str, required=True, help="Name of the database"
        )
        parser.add_argument(
            "--host",
            type=str,
            help="Host where DBMS is running (for SQLite: path to db file)",
        )
        parser.add_argument("--port", type=int, help="Database's port")
        parser.add_argument("--username", type=str)
        parser.add_argument("--password", type=str)
        parser.add_argument(
            "--output", type=str, required=True, help="A path to save the config"
        )

        return parser

    def run(self, args: Namespace):
        with open(args.output, "w") as f:
            if args.db == "postgres":
                database = Database.parse_obj(
                    {"postgres": Postgres(**vars(args)).dict()}
                )
            else:
                database = Database.parse_obj(
                    {"sqlite": Sqlite(name=args.name, path=args.host).dict()}
                )
            f.write(json.dumps(database.dict(exclude_unset=True)))
