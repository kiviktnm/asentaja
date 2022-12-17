import argparse
import sys
import os

import asentaja.main


def is_root():
    return os.geteuid() == 0


def run(repopath):
    if not os.path.isdir(repopath):
        print("Invalid configuration repository path.")
        exit(2)

    # Change the current working directory to the configuration repository.
    # The modules in the config repo can now refer to files within that repo relatively.
    os.chdir(repopath)

    # Allow importing modules from the current working directory (which is the config repo)
    sys.path.append(".")

    if not os.path.isfile("config.py"):
        print("Could not find config.py")
        exit(2)

    # Import the config file, it's existance should've been verified prevously.
    # This imported module will edit variables from asentaja modules.
    import config

    asentaja.main.apply_config()


def main():
    parser = argparse.ArgumentParser(
            prog="asentaja",
            description="A tool for declaratively managing Arch Linux.")

    parser.add_argument("repopath", help="configuration repository path")
    parser.add_argument("--no-root", action="store_true", help="allow running this program as a normal user, used mainly for testing")

    args = parser.parse_args()

    if not args.no_root:
        if not is_root():
            print("Please run this program as a super user.")
            exit(1)

    run(args.repopath)


if __name__ == "__main__":
    main()

