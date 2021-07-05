class Sentence(object):
	"""docstring for Sentence"""

	__slots__ = ['speaker',
				 'tiers',
				 'gra',
				 'mor',
				 'tokens',
				 'clean',
				 'comments',
				 'sent_id',
				]

	def __init__(self,
				 speaker=None,
				 tiers=None,
				 gra=None,
				 mor=None,
				 tokens=None,
				 clean=None,
				 comments=None,
				 sent_id=None,
				 ):
		self.speaker=speaker
		self.tiers=tiers
		self.gra=gra
		self.mor=mor
		self.tokens=tokens
		self.clean=clean
		self.comments=comments
		self.sent_id=sent_id

	def __str__(self):

		fields = [str(getattr(self, x)) for x in self.__slots__[:]]
		return ("\n".join(fields))

	def text(self):
		return " ".join(self.clean)

	def get_sent_id(self):
		return self.sent_id

