# !/usr/bin/env python
# encoding: utf-8
import urllib2
from threading import Thread, Lock
from Queue import Queue
import time


class Fetcher:
    def __init__(self, threads):
        self.opener = urllib2.build_opener(urllib2.HTTPHandler)
        self.lock = Lock()
        self.q_req = Queue()
        self.q_ans = Queue()
        self.threads = threads
        for i in range(threads):
            t = Thread(target=self.get_thread)
            t.setDaemon(True)
            t.start()
        self.running = 0

    def __del__(self):
        time.sleep(0.5)
        self.q_req.join()
        self.q_ans.join()

    def get_task(self):
        return self.q_req.qsize()+self.q_ans.qsize()+self.running

    def push(self, req):
        self.q_req.put(req)

    def pop(self):
        return self.q_ans.get()

    def get_thread(self):
        while True:
            req = self.q_req.get()
            with self.lock:
                self.running += 1
            try:
                ans = self.opener.open(req).read()
            except Exception, what:
                ans = ''
                print what
            self.q_ans.put((req, ans))
            with self.lock:
                self.running -= 1
            self.q_req.task_done()
            time.sleep(0.1)

if __name__ == "__main__":
    links = ['http://www.verycd.com/topics/%d/' % i for i in range(5420, 5430)]
    f = Fetcher(threads=10)
    for url in links:
        f.push(url)
    while f.get_task():
        url, content = f.pop()
        print url, len(content)