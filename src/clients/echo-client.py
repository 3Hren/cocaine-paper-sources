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

from cocaine.futures import chain
from cocaine.services import Service

from tornado.ioloop import IOLoop

# Alias for more readability.
asynchronous = chain.source

__author__ = 'Evgeny Safronov <division494@gmail.com>'

if __name__ == '__main__':
    io_loop = IOLoop.current()
    service = Service('echo')

    @asynchronous
    def invoke(message):
        result = yield service.enqueue('ping', message)
        print(result)

    invoke('Hello World!')
    invoke('Hello again!')
    io_loop.start()