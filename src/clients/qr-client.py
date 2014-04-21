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

from PIL import Image

from tornado.ioloop import IOLoop

from cocaine.futures import chain
from cocaine.services import Service

# Alias for more readability.
asynchronous = chain.source

__author__ = 'Evgeny Safronov <division494@gmail.com>'

if __name__ == '__main__':
    io_loop = IOLoop.current()
    service = Service('qr')

    @asynchronous
    def invoke(message):
        try:
            result = yield service.enqueue('generate', msgpack.dumps([message, 10]))
            print('Result:', result)
            out = StringIO.StringIO()
            out.write(result)
            out.seek(0)
            img = Image.open(out)
            img.save('qr.png', 'png')
        except Exception as err:
            print('Error: ', err)
        finally:
            io_loop.stop()

    invoke('What is best in life? To crush your enemies, see them driven before you, and to hear the lamentation of '
           'their women.')
    io_loop.start()