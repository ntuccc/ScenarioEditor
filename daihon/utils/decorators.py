from functools import wraps

class BaseCallback:
	def __init__(self, f):
		self._f = f
		self._callbacks = []
	def __call__(self, *args, **kwargs):
		result = self._call_part(*args, **kwargs) #don't catch exceptions
		#if no exception accured, callback
		self._callback_part(result)
		return result
	def _call_part(self, *args, **kwargs):
		raise NotImplementedError
	def _callback_part(self, result):
		for callback in self._callbacks:
			callback(result)
	def register(self, callback):
		self._callbacks.append(callback)

#store info in function
class CallbackFunction(BaseCallback):
	def _call_part(self, *args, **kwargs):
		return self._f(*args, **kwargs)

#make every obj.f an isolated function
class CallbackMethodWrapper:
	def __init__(self, f):
		self._f = f
		self._cache = {}
	def __get__(self, obj, klass):
		if obj is None:
			#return self._f
			obj = klass

		if id(obj) not in self._cache:
			self._make_func(obj)
		#it is impossible to make other obj have same ID
		#because CallbackMethod stores the obj
		#which makes the obj won't be deleted by GC
		#and that makes the other object won't occupy the same ID

		return self._cache[id(obj)][1]
	def _make_func(self, obj):
		result_func = wraps(self._f)(CallbackMethod(self._f, obj))
		self._cache[id(obj)] = (obj, result_func)

class CallbackMethod(BaseCallback):
	def __init__(self, f, obj):
		super().__init__(f)
		self._obj = obj
	def _call_part(self, *args, **kwargs):
		return self._f(self._obj, *args, **kwargs)

def callbackfunction(f):
	return wraps(f)(CallbackFunction(f))

def callbackmethod(f):
	return CallbackMethodWrapper(f)

if __name__ == '__main__':
	@callbackfunction
	def test():
		print(233)

	def callback(_):
		print(456)

	test.register(callback)
	test()
	#233 456
	print(test.__name__, test.__doc__)

	class T:
		@callbackmethod
		def f(self):
			print(111)
	T.f.register(callback)
	T.f()
	t = T() #111 456
	t.f() #111