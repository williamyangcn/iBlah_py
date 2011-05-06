import errno
import time
import threading

from PyQt4 import QtCore


def kill_qthread(t):
    if t is None:
        return

    t.terminate()
    while not t.isFinished():
        time.sleep(0.1)


class PeriodicExecutor(threading.Thread):
    """Call a function in a specified number of seconds interval:

    t = PeriodicExecutor(30.0, f, args=[], kwargs={})
    t.start()
    t.cancel() # stop the timer's action if it's still waiting
    """

    def __init__(self, interval, function, *args, **kwargs):
        threading.Thread.__init__(self, name = "PeriodicExecutor")
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = threading.Event()
        self.setDaemon(True)

    def cancel(self):
        """Stop the timer if it hasn't finished yet"""
        self.finished.set()

    def run(self):
        self.finished.wait(self.interval)
        while not self.finished.is_set():
            try:
                self.function(*self.args, **self.kwargs)
            except Exception as (err_no, err_msg):
                if err_no == errno.EPIPE:
                    self.finished.set()
                return
            self.finished.wait(self.interval)
        self.finished.set()


class IThread(QtCore.QThread):
    def __init__(self, func, **kwargs):
        QtCore.QThread.__init__(self)
        self.func = func
        self.kwargs = kwargs
        self.ret = None

    def run(self):
        self.ret = self.func(**self.kwargs)
        self.emit(QtCore.SIGNAL('thread_finished()'))

    def get_return(self):
        return self.ret


class IThreadKiller(QtCore.QThread):
    def __init__(self, target_t, timeout = 10):
        QtCore.QThread.__init__(self)
        self.target_t = target_t
        self.timeout = timeout

    def run(self):
        i = 0
        while i < self.timeout:
            time.sleep(1)
            self.emit(QtCore.SIGNAL('thread_running()'))
            i += 1
        self.emit(QtCore.SIGNAL('kill_qthread()'))
        while not self.target_t.isFinished():
            time.sleep(0.1)