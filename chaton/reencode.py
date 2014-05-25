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

        subprocess.call(['avconv', '-i', vinput.name, '-strict', 'experimental', '-y', '-s', '720x720', output.name])

        mime = magic.from_file(output.name, mime=True)
        with open(output.name, 'rb') as tmp:
            video.put_attachment(tmp, 'thumb/mp4', content_type=mime)

        os.remove(output.name)

        output = NamedTemporaryFile(mode='wb', delete=False, suffix='.ogv')
        output.close()

        subprocess.call(['ffmpeg2theora',  vinput.name,  '-x', '720', '-o', output.name])

        mime = magic.from_file(output.name, mime=True)
        with open(output.name, 'rb') as tmp:
            video.put_attachment(tmp, 'thumb/ogm', content_type=mime)

        os.remove(output.name)

        output = NamedTemporaryFile(mode='wb', delete=False, suffix='.jpg')
        output.close()

        subprocess.call(['avconv', '-ss', '3', '-i', vinput.name, '-strict', 'experimental',
                         '-y', '-vframes',  '1', '-s', '640x480', '-f', 'image2', output.name])

        mime = magic.from_file(output.name, mime=True)
        with open(output.name, 'rb') as tmp:
            video.put_attachment(tmp, 'capture', content_type=mime)

        os.remove(output.name)
        os.remove(vinput.name)

        message.ack()

    with Connection(config.get('app:main', 'rabbitmq.url')) as conn:
        with conn.Consumer(queueMeta, callbacks=[todo]) as consumer:
            # Process messages and handle events on all channels
            while True:
                conn.drain_events()

