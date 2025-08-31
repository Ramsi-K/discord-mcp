import os
import sys
import argparse

from .db import DatabaseConnection
from .db.init_db import init_db


def main():
    """
    Main entry point for the server registry.
    """
    parser = argparse.ArgumentParser(description="Server Registry")
    parser.add_argument(
        "--init-db", action="store_true", help="Initialize the database"
    )

    args = parser.parse_args()

    if args.init_db:
        print("Initializing database...")
        init_db()
        print("Database initialization complete.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
