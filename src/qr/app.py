#!/usr/bin/env python
#
#    Copyright (c) 2013-2014 Evgeny Safronov <division494@gmail.com>
#    Copyright (c) 2011-2014 Other contributors as noted in the AUTHORS file.
#
#    This file is part of Cocaine.
#
#    Cocaine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    Cocaine is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import StringIO
import msgpack

import qrcode

from cocaine.exceptions import ServiceError
from cocaine.decorators import http
from cocaine.logging import Logger
from cocaine.services import Service
from cocaine.worker import Worker

__author__ = 'Evgeny Safronov <division494@gmail.com>'

storage = Service('storage')
log = Logger()


def generate_qr(message, size=10):
    if size <= 0 or size >= 20:
        raise ValueError('size argument must fit in [0; 20]')

    out = StringIO.StringIO()
    img = qrcode.make(message, box_size=size)
    img.save(out, 'png')
    return out.getvalue()


def generate(request, response):
    rq = yield request.read()
    message, size = msgpack.loads(rq)

    try:
        if size < 10:
            data = generate_qr(message, size)
        else:
            key = '{0}size={1}'.format(message, size)
            try:
                data = yield storage.read('qr-codes', key)
            except ServiceError:
                data = generate_qr(message, size)
                yield storage.write('qr-codes', key, data)
        response.write(data)
    except Exception as err:
        response.error(1, str(err))
    finally:
        response.close()


@http
def generate_http(request, response):
    request = yield request.read()
    try:
        message = request.request['message']
        size = int(request.request.get('size', 10))

        if size < 10:
            data = generate_qr(message, size)
        else:
            key = '{0}size={1}'.format(message, size)
            try:
                data = yield storage.read('qr-codes', key)
            except ServiceError:
                data = generate_qr(message, size)
                yield storage.write('qr-codes', key, data)

        response.write_head(200, [('Content-type', 'image/png')])
        response.write(data)
    except KeyError:
        response.write_head(400, [('Content-type', 'text/plain')])
        response.write('Query field "message" is required')
    except Exception as err:
        response.write_head(400, [('Content-type', 'text/plain')])
        response.write(str(err))
    finally:
        response.close()


w = Worker()
w.run({
    'generate': generate,
    'generate-http': generate_http
})
