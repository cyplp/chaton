# -*- coding: utf-8 -*-
import argparse
import ConfigParser
import subprocess
import os

from tempfile import NamedTemporaryFile

from kombu import Connection, Exchange, Queue

import couchdbkit
import magic

from chaton.models import Video


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf',
                        help='wsgi conf file')


    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config.read(args.conf)

    server = couchdbkit.Server(config.get('app:main', 'couchdb.url'))
    db = server.get_or_create_db(config.get('app:main','couchdb.db'))
    Video.set_db(db)


    exchange = Exchange(config.get('app:main', 'rabbitmq.exchange.video'), 'direct', durable=True)
    queueMeta = Queue(config.get('app:main', 'rabbitmq.queue.video'), exchange=exchange, routing_key='video')

    def todo(body, message):
        video = Video.get(body['id'])

        vinput = NamedTemporaryFile(mode='wb', delete=False)

        vinput.write(video.fetch_attachment('video', stream=True).read())
        vinput.close()

        output = NamedTemporaryFile(mode='wb', delete=False, suffix='.mp4')
        output.close()

        subprocess.call(['avconv', '-i', vinput.name, '-strict', 'experimental',  output.name])

        mime = magic.from_file(output.name, mime=True)
        with open(output.name, 'rb') as tmp:
            video.put_attachment(tmp, 'thumb', content_type=mime)

        os.remove(vinput.name)
        os.remove(output.name)

        #message.ack()

    print 4
    with Connection(config.get('app:main', 'rabbitmq.url')) as conn:
        print 5
        with conn.Consumer(queueMeta, callbacks=[todo]) as consumer:
            # Process messages and handle events on all channels
            print 6
            while True:
                conn.drain_events()

