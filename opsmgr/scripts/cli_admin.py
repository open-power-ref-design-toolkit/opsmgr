import argparse
import sys

from sqlalchemy import create_engine

import opsmgr.inventory.persistent_mgr as persistent_mgr
import opsmgr.inventory.data_model as data_model

def db_sync():
    engine = create_engine(persistent_mgr.read_database_connection())
    data_model.Base.metadata.create_all(engine)
    return 0, "Database tables have been created"

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Operational Manager Admin Commands')
    subparsers = parser.add_subparsers(dest='operation', help='Actions')

    #db_sync
    subparsers.add_parser('db_sync', help='Create the database tables')

    message = ''
    rc = -1
    args = parser.parse_args(argv)

    if args.operation == 'db_sync':
        (rc, message) = db_sync()
    else:
        parser.print_help()

    if message:
        print(message)
    return rc

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
