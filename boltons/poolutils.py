# -*- coding: utf-8 -*-
"""The ``poolutils`` module currently provides one pool
implementation: :class:`ThreadQueue`.

```py
# Function to be executed.
def printer(x, y, testx=None, testy=None):
    print x, y, testx, testy
    print "Done"

t = SimplePool.ThreadPool()

# Adding the same function 100 times
for i in range(100):
    args = ('formalx', 'formaly')
    kwargs = {'testx': 'keywordx', 'testy': 'keywordy'}
    # Create a thread_job object.
    j = SimplePool.ThreadJob(printer, args, kwargs)
    t.add_job(j)
t.start()
t.finish()
```
"""


import threading
try:
    import Queue
except ImportError:
    import queue as Queue

__all__ = ['ThreadPool', 'ThreadJob']


class ThreadJob(object):

    def __init__(self, exec_function, args=None, kwds=None):
        self.exception = False
        self.callback = None  # Yet to be done
        self.args = []
        self.kwargs = {}
        self.return_value = None
        self.exec_function = exec_function
        if type(args) == str or args == 0:
            self.args = (args,)
        else:
            self.args = (args) or []
        self.kwargs = kwds or {}

    def execute(self):
        try:
            self.return_value = self.exec_function(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e


class ThreadPool(object):

    def __init__(self, nthreads=10):
        self.nthreads = 0
        self._q_size = 0
        self._job_q = Queue.Queue()
        self._result_q = Queue.Queue()
        self._total_jobs = 0
        self._threads = []
        self.is_active = 0
        self.nthreads = nthreads

    def start(self):
        for i in range(self.nthreads):
            t = WorkerThread(self._job_q, self._result_q)
            self.is_active = True
            self._threads.append(t)
            t.start()
        return True

    def add_job(self, job):
        self._job_q.put(job)
        self._total_jobs += 1
        return True

    def finish(self):
        self._job_q.join()
        self.is_active = False
        return True

    def unfinished_tasks(self):
        return self._job_q.qsize()

    def finished_tasks(self):
        return self._total_jobs - self._job_q.qsize()


class WorkerThread(threading.Thread):

    def __init__(self, job_q, result_q):
        super(WorkerThread, self).__init__()
        self._job_q = job_q
        self._result_q = result_q

    def run(self):
        while True:
            try:
                job = self._job_q.get(None)
            except Queue.Empty:  # Exit the worker if Q empty
                return True
            job.execute()
            self._result_q.put(job)
            self._job_q.task_done()
        return True
