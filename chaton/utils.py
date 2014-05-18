# -*- coding: utf-8 -*-
import argparse
import ConfigParser
import smtplib
from email.mime.text import MIMEText

import couchdbkit
import bcrypt

from chaton.models.user import User

template = u"""
Bonjour %s,

Bienvenu sur %s notre plateforme secrète d'échange de vidéos.

Ton login est «%s».
Ton mot de passe est «%s».

Tu peux changer ton mot de passe ici : %s/myaccount

Tu peux uploadé tes vidéos (ça prends plombe.) ou voir celle des autres (ça mets aussi une plombe).


--
cyplp@free.fr
"""

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
                name=args.name.decode('utf-8'),
                mail=args.userid,
                isAdmin=admin,
                )
    user._id = args.userid

    user.save()

    msg = MIMEText(template % (args.name.decode('utf-8'), config.get('app:main', 'public_url'),
                               args.userid.decode('utf-8'), args.password, config.get('app:main', 'public_url')), 'plain', 'utf-8')

    msg['Subject'] = 'échange de vidéo pour le mariage de Julien et Isabelle'.decode('utf-8')
    msg['From'] = 'cyplp@free.fr'
    msg['To'] = args.userid

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    print msg
    s = smtplib.SMTP('smtp.free.fr')
    s.sendmail('cyplp@free.fr', [args.userid], msg.as_string().encode('ascii'))
    s.quit()
