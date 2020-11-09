from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import ClassVar, Optional, Tuple


@dataclass
class BaseCommand:
    """Base class for time_manager_admin subcommands."""

    name: str
    description: Optional[str] = None

    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseCommand.subclasses = BaseCommand.subclasses + (cls,)

    def add_arguments_to_parser(self, parser: ArgumentParser) -> ArgumentParser:
        """Defines all arguments for commands' parser."""
        return parser

    def run(self, args: Namespace):
        """Implements the logic of a command."""
