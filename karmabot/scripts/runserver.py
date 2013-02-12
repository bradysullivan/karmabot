# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
import sys

from twisted.internet import reactor, ssl
from twisted.python import log

from karmabot.core.client import KarmaBotFactory


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="A very extensible IRC bot written in Python.")

    # IRC connection options
    parser.add_argument("-s", "--server",
                      action="store", dest="server",
                      default="irc.freenode.net",
                      help="IRC server to connect to")
    parser.add_argument("-p", "--port",
                      action="store", type=int, dest="port", default=None,
                      help="IRC server to connect to")
    parser.add_argument("--ssl",
                      action="store_true", dest="ssl", default=False,
                      help="use SSL")
    parser.add_argument("--password",
                      action="store", dest="password", default=None,
                      help="server password")
    parser.add_argument("-n", "--nick",
                      action="store", dest="nick", default="karmabot",
                      help="nickname to use")
    # Bot options
    parser.add_argument("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="enable verbose output")
    parser.add_argument("-d", "--data",
                      action="store", dest="filename", default="karma.json",
                      help="karma data file name")
    parser.add_argument("-t", "--trust",
                      action="append", dest="trusted", default=[],
                      help="trusted hostmasks")
    parser.add_argument("-f", "--facets",
                      action="append", dest="facets", default=[],
                      help="additional facets to load")

    (options, channels) = parser.parse_known_args()

    if not channels:
        parser.error("You must supply some channels to join.")
    else:
        log.msg("Channels to join: %s" % channels)

    if options.verbose:
        log.startLogging(sys.stdout)

    if not options.port:
        options.port = 6667 if not options.ssl else 9999

    factory = KarmaBotFactory(options.filename, options.nick,
                              channels, options.trusted, options.password,
                              options.facets)
    if not options.ssl:
        reactor.connectTCP(options.server, options.port, factory)
    else:
        reactor.connectSSL(options.server, options.port,
                           factory, ssl.ClientContextFactory())
    reactor.run()

if __name__ == "__main__":
    main()
