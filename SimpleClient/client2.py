from __future__ import print_function
import requests
import json
from gevent.threadpool import ThreadPool
import gevent
import functools
import time
import random
from utils import *


class Worker(object):
    def __init__(self, url):
        self.url = url
        self.headers = {'content-type': 'application/json'}
        self.id = 0
        self.post = functools.partial(requests.post, self.url, headers=self.headers)
        self.pool = ThreadPool(1000)

    def _call(self, method, *args):
        payload = dict(method=method, params=args, jsonrpc="2.0", id=self.id)
        self.id += 1
        response = self.post(json.dumps(payload)).json()
        return response

    def _async_call(self, method, *args):
        payload = dict(method=method, params=args, jsonrpc="2.0", id=self.id)
        self.id += 1

        def _delayed_call(pl):
            return self.post(json.dumps(pl)).json()

        return Future(self.pool.spawn(_delayed_call, payload))

    def tell(self, method, *args):
        self._async_call(method, *args)

    def ask(self, method, *args):
        return self._async_call(method, *args)

    def join(self):
        self.pool.join()


class Future:
    def __init__(self, result):
        self.result = result

    def __repr__(self):
        return str(self.get())

    def get(self):
        # return self.result.get()
        return self.result.get().get('result', self.result.get().get('error'))

    def complete(self):
        return self.result.ready()

    def on_complete(self, func):
        def _func(arg):
            print(arg)
            print(arg.get())
            func(arg.get().get('result', arg.get().get('error')))

        self.result.rawlink(_func)
        return self

        # while True:
        #     if self.result.ready():
        #         break
        #     else:
        #         gevent.sleep(0)
        #
        # func(self.result.get().get('result', self.result.get().get('error')))


class FutureManager:
    __metaclass__ = Singleton
    futures = list()

    def process(self):
        future = self.futures.pop(0)
        future.get()
        if future.ready():
            future.callback(future.get().get('result'))
        else:
            self.futures.append(future)
        # print(future.ready(), callback)
        print(len(self.futures))

    def join(self):
        while True:
            if len(self.futures) == 0:
                return
            else:
                self.process()




if __name__ == "__main__":
    worker = Worker('http://127.0.0.1:8080/rpc')

    def func1():
        print("blocking")
        stime = time.clock()
        print(worker.ask("power", 2, 6).get())
        print(worker.ask("echo", "echome!").get())
        print(time.clock() - stime)
        print()

    def func2():
        print("non-blocking")
        stime = time.clock()
        for idx in range(1000):
            #worker.ask("power", random.randint(0, 10), random.randint(0, 10)).on_complete(print)
            worker.ask("echo", idx).on_complete(print)
        # r2 = worker.ask("echo", random.randint(0, 10)).on_complete(print)
        # r3 = worker.ask("echo", random.randint(0, 10)).on_complete(print)
        print(time.clock() - stime)
        worker.join()

    #func1()
    func2()

