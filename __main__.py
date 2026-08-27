from __future__ import annotations

from argparse import ArgumentParser, Namespace

from chatty.entrypoint.client import launch_client
from chatty.entrypoint.server import launch_server


def main() -> None:
    parser = ArgumentParser(prog="chatty")
    parser.add_argument("mode", choices=("client", "server"))
    args: Namespace = parser.parse_args()

    if args.mode == "client":
        launch_client()
    else:
        launch_server()


if __name__ == "__main__":
    main()
