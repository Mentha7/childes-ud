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
		self.speaker=None,
		self.tiers=None,
		self.gra=None,
		self.mor=None,
		self.tokens=None,
		self.clean=None,
		self.comments=None,
		self.sent_id=None

