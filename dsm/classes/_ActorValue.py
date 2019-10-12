class Stat(float):
	def __new__(cls, value, **kwargs):
		self = super(cls, cls).__new__(cls, value)
		for key, value in kwargs.items():
			self.__dict__[key] = value

		self.d = kwargs
		return self

	def __add__(self, other):
		res = super(Stat, self).__add__(other)
		return self.__class__( min(self.max, max(res, 0)), **self.d )

	def __sub__(self, other):
		res = super(Stat, self).__sub__(other)
		return self.__class__( min(self.max, max(res, 0)), **self.d )

	def __mul__(self, other):
		res = super(Stat, self).__mul__(other)
		return self.__class__( min(self.max, max(res, 0)), **self.d )

	def __div__(self, other):
		res = super(Stat, self).__div__(other)
		return self.__class__( min(self.max, max(res, 0)), **self.d )

	def __str__(self):
		return ("%d/%d" % (int(self), int(self.max)) )

	def __repr__(self):
		return ("Stat(%d/%d)" % (int(self), int(self.max)) )