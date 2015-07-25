from Queue import Queue
from threading import Thread
from time import sleep
import gevent,gevent.monkey
import gevent.queue
class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            c_task=self.tasks.get()
            if not c_task:
                self.tasks.task_done()
                break
            func, args, kargs = c_task
            try:
                func(*args, **kargs)
            except:
                raise
            finally:
                self.tasks.task_done()


class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    thread_count=0
    def __init__(self, num_threads,engine='threading'):
        self.thread_count = num_threads
        self.tasks = None
        if engine == 'threading':
            self.tasks = Queue(num_threads)
        elif engine == 'greenlet':
            gevent.monkey.patch_dns()
            gevent.monkey.patch_os()
            gevent.monkey.patch_select(True)
            gevent.monkey.patch_socket(True)
            gevent.monkey.patch_time()
            gevent.monkey.patch_ssl()
            gevent.monkey.patch_thread()
            self.tasks = gevent.queue.JoinableQueue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)
    def finalize(self): #add None objects to terminate thread
        for i in range(0, self.thread_count):
            self.tasks.put(None)
    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()
