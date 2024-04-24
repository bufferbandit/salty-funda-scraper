from contextlib import contextmanager
from multiprocessing import Queue
from time import sleep
import threading


from driver import create_driver


class MaxPool:
	def __init__(self, pool_size=5):
		self.pool_size = pool_size
		self.available_objects = []
		self.lock = threading.Lock()
		self.intialize_objects()

	def intialize_objects(self):
		raise NotImplementedError("No method to initialize objects overridden")

	@contextmanager
	def acquire(self):
		obj = self.acquire_object()
		try:
			yield obj
		finally:
			self.release(obj)

	def acquire_object(self):
		with self.lock:
			while not self.available_objects:
				self.lock.release()
				self.lock.acquire()
			return self.available_objects.pop()

	def release(self, obj):
		with self.lock:
			self.available_objects.append(obj)


class SeleniumPool(MaxPool):
	def __init__(self, pool_size=5, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def intialize_objects(self):
		self.available_objects = []
		for _ in range(self.pool_size):
			# sleep(1)
			self.available_objects.append(create_driver())
	    # return create_driver()
