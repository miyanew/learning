import fcntl
import os
from contextlib import contextmanager


class LockAcquisitionError(Exception):
    pass


class LockManager:
    def __init__(self):
        self.lock_file = "./hoge.lock"
        self.fd = None

    @property
    def lock_file(self):
        return self.lock_file

    @contextmanager
    def lock(self):
        if not self.acquire_lock():
            raise LockAcquisitionError(f"Failed to acquire lock: {self.lock_file}")
        try:
            yield
        finally:
            self.release_lock()

    def acquire_lock(self):
        try:
            self.fd = open(self.lock_file, "w")
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError:
            self.fd = None
            return False

    def release_lock(self):
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        self.fd.close()
        os.remove(self.lock_file)
