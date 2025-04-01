import sys

from .cli import app


def main():
    try:
        app(standalone_mode=True)
    except SystemExit as e:
        sys.exit(e.code)


if __name__ == "__main__":
    main()

# Make main() the callable when importing __main__
__call__ = main
