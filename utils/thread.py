import settings
import threading
import ctypes
import inspect

# Some code from http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
# CC-BY-SA license

class ExitThread(SystemExit):
    pass

if settings.CLIQUECLIQUE_PROFILE:
    import cProfile
    import marshal
    def runprofile(fn, *arg, **kw):
        func_name = fn.func_name
        if hasattr(fn, 'im_class'):
            func_name = fn.im_class.__name__ + '.' + func_name
        filename = "%(func_name)s_in_%(thread)s.prof" % {'func_name':func_name, 'thread':threading.current_thread().ident}
        cProfile.runctx("fn(*arg, **kw)", globals(), locals(), filename)
else:
    def runprofile(fn, *arg, **kw):
        fn(*arg, **kw)

class Thread(threading.Thread):
    def __init__(self, **kw):
        threading.Thread. __init__(self)
        self.daemon = True
        for key, value in kw.iteritems():
            setattr(self, key, value)

    def run(self, *arg, **kw):
        runprofile(self.main_run, *arg, **kw)

    def raise_exception(self, exctype):
        """Raises the given exception type in the context of this thread.

        If the thread is busy in a system call (time.sleep(), socket.accept(), ...) the exception
        is simply ignored.

        If you are sure that your exception should terminate the thread, one way to ensure that
        it works is:
        t = ThreadWithExc( ... )
        ...
        t.raise_exception( SomeException )
        while t.isAlive():
            time.sleep( 0.1 )
            t.raise_exception( SomeException )

        If the exception is to be caught by the thread, you need a way to check that your
        thread has caught it.

        CAREFUL : this function is executed in the context of the caller thread,
        to raise an excpetion in the context of the thread represented by this instance.
        """

        if not inspect.isclass(exctype):
            raise TypeError("Only types can be raised (not instances)")
        tid = self.ident
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id %s" % (tid,))
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble, 
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def exit(self, wait=True):
        print "Exiting thread %s" % (self,)
        self.raise_exception(ExitThread)
        if wait:
            self.join()
