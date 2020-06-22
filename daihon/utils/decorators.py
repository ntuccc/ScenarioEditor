from functools import wraps

#store info in function
class CallbackFunction:
	def __init__(self, f):
		self._f = f
		self._callbacks = []
	def __call__(self, *args, **kwargs):
		result = self._f(*args, **kwargs) #don't catch exceptions
		#if no exception accured, callback
		for callback in self._callbacks:
			callback(result)
		return result
	def register(self, callback):
		self._callbacks.append(callback)

#store info in obj
class CallbackMethodWrapper:
	def __init__(self, f):
		self._f = f
		self._cache = {}
	def __get__(self, obj, klass):
		if obj is None:
			#return self._f
			obj = klass

		info = f'_callback{id(self)}'
		#here not use hasattr
		#to ensure the callbacks of klass do not interfere the one of the obj
		if info not in obj.__dict__:
			setattr(obj, info, [])

		if id(obj) not in self._cache:
			self._make_func(obj, info)
		#it is impossible to make other obj have same ID
		#because CallbackMethod stores the obj
		#which makes the obj won't be deleted by GC
		#and that makes the other object won't occupy the same ID

		return self._cache[id(obj)][1]
	def _make_func(self, obj, info):
		result_func = wraps(self._f)(CallbackMethod(self._f, obj, info))
		self._cache[id(obj)] = (obj, result_func)

class CallbackMethod:
	def __init__(self, f, obj, info):
		self._f = f
		self._obj = obj
		self._info = info
	def __call__(self, *args, **kwargs):
		result = self._f(self._obj, *args, **kwargs) #don't catch exceptions
		#if no exception accured, callback
		for callback in getattr(self._obj, self._info):
			callback(result)
		return result
	def register(self, callback):
		getattr(self._obj, self._info).append(callback)

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