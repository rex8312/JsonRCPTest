#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import gevent

# Fix paths
# rootdir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(rootdir)
# os.chdir(rootdir)

import bottle
import bottle_jsonrpc
# import gevent.monkey

# gevent.monkey.patch_all()


@bottle.route('/')
def index():
    return bottle.static_file('example.html', os.getcwd())


jsonrpc = bottle_jsonrpc.register('/rpc')


@jsonrpc
def add(a, b):
    return a + b


@jsonrpc
def sort(lst):
    return sorted(lst)


@jsonrpc
def power(base, power):
    print base, power
    # gevent.sleep(0)
    return base ** power


@jsonrpc
def echo(msg):
    print msg
    # gevent.sleep(0)
    return msg


bottle.debug(True)

if __name__ == '__main__':
    # Standalone web server
    bottle.run(reloader=True, server="tornado")
else:
    # Running under WSGI (probably apache)
    application = bottle.default_app()
