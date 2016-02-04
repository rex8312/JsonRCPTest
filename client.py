from __future__ import print_function
import requests
import json
from gevent.threadpool import ThreadPool
import functools
import time
import random


class Worker(object):
    def __init__(self, url):
        self.url = url
        self.headers = {'content-type': 'application/json'}
        self.id = 0
        self.post = functools.partial(requests.post, self.url, headers=self.headers)
        self.pool = ThreadPool(100)

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
        self.true_result = None

    def __repr__(self):
        return str(self.get())

    def get(self):
        return self.true_result or self.result.get().get('result', self.result.get().get('error'))

    def complete(self):
        return self.result.ready()

    def on_complete(self, func):
        def _func(arg):
            self.true_result = arg.get().get('result', arg.get().get('error'))
            func(self.true_result)

        self.result.rawlink(_func)
        return self


if __name__ == "__main__":
    worker = Worker('http://127.0.0.1:8080/rpc')

    def blocking():
        print("** blocking **")
        stime = time.clock()
        print(worker.ask("power", 2, 6).get())
        print(worker.ask("echo", "echome!").get())
        print(time.clock() - stime)

    def non_blocking():
        print("** non-blocking **")
        stime = time.clock()
        worker.tell("power", random.randint(0, 10), random.randint(0, 10))
        worker.tell("echo", "echome!")
        print("elapsed time: (tell message): {}".format(time.clock() - stime))
        
        stime = time.clock()
        r1 = worker.ask("power", random.randint(0, 10), random.randint(0, 10)).on_complete(print)
        r2 = worker.ask("echo", "echome!").on_complete(print)
        ttime = time.clock() - stime
        print("elapsed time (send messages): {}".format(time.clock() - stime))
        
        print("do other jobs")
        time.sleep(15)        
        
        stime = time.clock()
        print("get", r1.get())
        print("get", r2.get())
        ttime += time.clock() - stime
        print("elapsed time (get respond): {}".format(time.clock() - stime))

        print("total elapsed time: {}".format(ttime))

    blocking()
    print()
    non_blocking()

