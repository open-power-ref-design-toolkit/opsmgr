import argparse
import base64
import getpass
import os
import sys

from sqlalchemy import create_engine
from backports import configparser
from pkg_resources import resource_string

import opsmgr.inventory.persistent_mgr as persistent_mgr
import opsmgr.inventory.data_model as data_model

CONF_DIR = "/etc/opsmgr"
CONF_FILE = CONF_DIR + "/opsmgr.conf"
LOGGING_FILE = CONF_DIR + "/logging.yaml"

LOG_DIR = "/var/log/opsmgr"
LOG_FILE = LOG_DIR + "/opsmgr.log"
LOG_ERROR_FILE = LOG_DIR + "/opsmgr_error.log"

def _copy_logging_yaml():
    if os.path.exists(LOGGING_FILE):
        print(LOGGING_FILE + " already exist. Will not modify this file")
    else:
        logging_string = resource_string(__name__, "../../etc/logging.yaml")
        fp = open(LOGGING_FILE, "wb")
        fp.write(logging_string)
        fp.close()

def _write_conf_file(args):
    #Hack to support python2.7
    try:
        input = raw_input
    except NameError:
        pass


    if os.path.exists(CONF_FILE):
        print(CONF_FILE + " exist. To generate a new passphrase delete " \
              "this file and run the command again.")
    else:
        passphrase = str(base64.b64encode(os.urandom(32)))

        print("At this time only a mysql database on localhost is supported. " \
              "Any sqlalchemy supported database can be used by " \
              "modifying the connection property in " + CONF_FILE + " " \
              "and running opsmgr-admin db_sync.")

        if args.db_user:
            userid = args.db_user
        else:
            userid = input("Enter database userid:")

        if args.db_password:
            password = args.db_password
        else:
            password = getpass.getpass(prompt="Enter password for database userid (" +
                                       userid + "):")
        if args.db_name:
            database_name = args.db_name
        else:
            database_name = input("Enter database name [opsmgr]:")
            if database_name == '':
                database_name = "opsmgr"

        connection_string = "mysql+pymysql://" + userid + ":" + password + \
                        "@localhost/" + database_name
        cfgfile = open(CONF_FILE, 'w')
        config = configparser.ConfigParser()
        config.add_section('DATABASE')
        config.set('DATABASE', 'connection', connection_string)
        config.set('DEFAULT', 'passphrase', passphrase)
        config.write(cfgfile)
        cfgfile.close()

        os.chmod(CONF_FILE, 0o600)
        print(CONF_FILE + " has been created with the only the current user having read " \
              "authority. To allow others to use the command line read access to this file " \
              "is required. Be aware that exposes the password for the database user.")
        db_sync()

def _create_log_files():
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
        open(LOG_FILE, 'a').close()
        open(LOG_ERROR_FILE, 'a').close()
        os.chmod(LOG_FILE, 0o666)
        os.chmod(LOG_ERROR_FILE, 0o666)

def post_install_config(args):
    """ Needs to:
        1. Copy /etc/opsmgr/logging.yaml
        2. Generate unique passphrase
        3. Define database connection
        4. Create database tables
        5. Precreate log files with permissions
    """
    if not os.path.exists(CONF_DIR):
        os.mkdir(CONF_DIR)

    _copy_logging_yaml()
    _write_conf_file(args)
    _create_log_files()

def db_sync():
    engine = create_engine(persistent_mgr.read_database_connection())
    data_model.Base.metadata.create_all(engine)
    print("Database tables have been created")

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Operational Manager Admin Commands')
    subparsers = parser.add_subparsers(dest='operation', help='Actions')

    pic = subparsers.add_parser('post_install_config', help='Setup the files in /etc/opsmgr')
    pic.add_argument('--db_user', help='Database userid')
    pic.add_argument('--db_password', help='Password of the database userid')
    pic.add_argument('--db_name', help='Name of the database (default: opsmgr')

    #db_sync
    subparsers.add_parser('db_sync', help='Create the database tables')

    args = parser.parse_args(argv)

    if args.operation == 'post_install_config':
        post_install_config(args)
    elif args.operation == 'db_sync':
        db_sync()
    else:
        parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
