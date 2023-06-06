import argparse
from dataclasses import dataclass
from typing import Optional, Type

import genv.sdk
from genv.sdk import Env


@dataclass
class Field:
    name: str
    type: Optional[Type] = None

    @property
    def human_readable_name(self) -> str:
        """Converts the field name to a human readable one"""

        return self.name.replace("_", "-")


FIELDS = [
    Field("gpu_memory"),
    Field("gpus", type=int),
    Field("name"),
]


def print_field(config: Env.Config, field: Field, *, prefix: bool = False) -> None:
    """Prints a field"""

    value = getattr(config, field.name)

    if value is not None:
        print(f"{field.human_readable_name}: {value}" if prefix else value)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genvctl config" arguments to a parser.
    """

    parser.add_argument("--clear", action="store_true")

    subparsers = parser.add_subparsers(dest="field")

    for field in FIELDS:
        subparser = subparsers.add_parser(field.human_readable_name)
        subparser.add_argument(field.name, type=field.type, nargs="?")
        subparser.add_argument("--clear", action="store_true")


def run(args: argparse.Namespace) -> None:
    """
    Runs the "genvctl config" logic.
    """

    config = genv.sdk.configuration()

    if args.field is None:
        if args.clear:
            config = genv.sdk.Env.Config()
        else:
            for field in FIELDS:
                print_field(config, field, prefix=True)
    else:
        field = next(
            field for field in FIELDS if field.human_readable_name == args.field
        )

        value = getattr(args, field.name)

        if args.clear:
            setattr(config, field.name, None)
        elif value is None:
            print_field(config, field)
        else:
            setattr(config, field.name, value)

    genv.sdk.configure(config)
