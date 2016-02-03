from tornadorpc.json import JSONRPCHandler
from tornadorpc import private, start_server
import time
import gevent


class Tree(object):
    def power(self, base, power, modulo=None):
        result = pow(base, power, modulo)
        gevent.sleep(5)
        print "{} = tree.power({}, {})".format(result, base, power)
        return result

    def _private(self):
        # Won't be callable
        return False


class Handler(JSONRPCHandler):
    tree = Tree()

    def add(self, x, y):
        return x + y

    def ping(self, obj):
        return obj

    def echo(self, msg):
        print '{} = echo({})'.format(msg, msg)
        gevent.sleep(2)
        return msg


if __name__ == "__main__":
    start_server(Handler, port=8080)