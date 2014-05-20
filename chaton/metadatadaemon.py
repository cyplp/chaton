# -*- coding: utf-8 -*-
import argparse
import ConfigParser
import datetime

from tempfile import NamedTemporaryFile

from kombu import Connection, Exchange, Queue

import couchdbkit

from hachoir_parser import createParser
from hachoir_metadata import extractMetadata

from chaton.models import Video


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf',
                        help='wsgi conf file')

    print 1
    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config.read(args.conf)

    server = couchdbkit.Server(config.get('app:main', 'couchdb.url'))
    db = server.get_or_create_db(config.get('app:main','couchdb.db'))
    Video.set_db(db)

    print 2

    exchange = Exchange(config.get('app:main', 'rabbitmq.exchange.video'), 'direct', durable=True)
    queueMeta = Queue(config.get('app:main', 'rabbitmq.queue.meta'), exchange=exchange, routing_key='video')

    print 3
    def todo(body, message):
        print 1.1
        video = Video.get(body['id'])

        temp = NamedTemporaryFile(mode='wb', delete=False)

        temp.write(video.fetch_attachment('video', stream=True).read())

        temp.close()
        # import pdb
        # pdb.set_trace()
        print 1.2
        parser = createParser(unicode(temp.name))
        print 1.3
        metadata = extractMetadata(parser)

        tmp = [[i.description, [j.value for j in i.values]] for i in metadata if i.values]

        metas = {}

        for meta in tmp:
            print meta[0]
            if type(meta[1]) not in [int, datetime.datetime, datetime.date, float, datetime.time, long, unicode, str, set, list, dict, bool]:
                metas[meta[0]] = str(meta[1])
            else:
                metas[meta[0]] = meta[1]

        video.metadata = metas

        video.save()

        #message.ack()

    print 4
    with Connection(config.get('app:main', 'rabbitmq.url')) as conn:
        print 5
        with conn.Consumer(queueMeta, callbacks=[todo]) as consumer:
            # Process messages and handle events on all channels
            print 6
            while True:
                conn.drain_events()

