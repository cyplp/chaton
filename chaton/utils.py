import argparse
import ConfigParser

import couchdbkit
import bcrypt

from chaton.models.user import User


def addUser():
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf',
                        help='wsgi conf file')

    parser.add_argument('--userid',
                        help='user id')

    parser.add_argument('--password',
                        help='password')

    parser.add_argument('--name',
                        help='name')

    parser.add_argument('--admin',
                        help='admin')

    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config.read(args.conf)

    server = couchdbkit.Server(config.get('app:main', 'couchdb.url'))
    db = server.get_or_create_db(config.get('app:main','couchdb.db'))
    User.set_db(db)

    admin = args.admin.lower() == 'true'
    password = bcrypt.hashpw(args.password.encode('utf-8'),
    bcrypt.gensalt())
    user = User(password=password,
                name=args.name,
                mail=args.userid,
                isAdmin=admin,
                )
    user._id = args.userid
    user.save()

