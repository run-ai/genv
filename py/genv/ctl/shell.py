import argparse

import genv.sdk


def do_init() -> None:
    """Prints the init shell script"""

    print(
        """\
genvctl()
{
  local command="${1:-}"
  if [ "$#" -gt 0 ]; then
    shift
  fi

  case "$command" in
  config)
    command genvctl config $@
    eval "$(command genvctl shell --reconfigure)"
    ;;
  shell)
    if [ "$#" -eq 0 ]; then
      command genvctl shell --ok
    else
      command genvctl shell $@
    fi
    ;;
  *)
    command genvctl $command $@
    ;;
  esac
}
"""
    )


def do_error() -> None:
    """Prints an error message"""

    print(
        """\
Your shell is not properly initialized at the moment.
Run the following command to initialize it.
You should also add it to your ~/.bashrc or any equivalent file.

    eval "$(genvctl shell --init)"
"""
    )


def do_ok() -> None:
    """Prints an ok message"""

    print(
        """\
Your shell is initialized properly and you are all set.
Run the following command to check the status of your environment:

    genvctl status

If you are not sure how to continue from here, check out the quick start tutorial at https://docs.genv.dev/overview/quickstart.html.
"""
    )


def do_reconfigure() -> None:
    """Reconfigures environment variables in the shell"""

    config = genv.sdk.refresh_configuration()

    for name, value in [
        ("GENV_ENVIRONMENT_NAME", config.name),
        ("GENV_GPU_MEMORY", config.gpu_memory),
        ("GENV_GPUS", config.gpus),
    ]:
        if value is not None:
            print(f"export {name}={value}")
        else:
            print(f"unset {name}")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genvctl shell" arguments to a parser.
    """

    parser.add_argument(
        "--init",
        action="store_const",
        dest="action",
        const="init",
        help=argparse.SUPPRESS,
    )

    parser.add_argument(
        "--ok",
        action="store_const",
        dest="action",
        const="ok",
        help=argparse.SUPPRESS,
    )

    parser.add_argument(
        "--reconfigure",
        action="store_const",
        dest="action",
        const="reconfigure",
        help=argparse.SUPPRESS,
    )


def run(args: argparse.Namespace) -> None:
    """
    Runs the "genvctl shell" logic.
    """

    if args.action == "init":
        do_init()
    elif args.action == "ok":
        do_ok()
    elif args.action == "reconfigure":
        do_reconfigure()
    else:
        do_error()