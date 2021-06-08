class ChatToken(object):
	"""docstring for ChatToken"""

	__slots__ = ['index', 'surface', 'token', 'lemma', 'mor', 'gra', 'pos', 'head']

	def __init__(self, index=0, surface=None, token=None, lemma=None, mor=None, gra=None, pos=None, head=None):
		self.index = index
		self.surface = surface
		self.token = token
		self.lemma = lemma
		self.mor = mor
		self.gra = gra
		self.pos = pos
		self.head = head



class ChatLabel(object):
	"""docstring for ChatLabel"""
	def __init__(self, arg):
		self.arg = arg

	def form(self):
		pass


class ChatSentence(object):
	"""Holds a Chat sentence.
	Attributes:
		items   - tokens and labels in the sentence (ordered)
		tokens   - tokens in the sentence
		# labels   - labels in the sentence
		speaker   - the participant whouttered the sentence
	"""
	__slots__ = ['form', 'items', 'tokens', 'speaker', 'mor', 'gra']

	def __init__(self, form=None, items=[], speaker=None, mor=[], gra=[]):
		self.form = form
		self.items = items
		# self.tokens = tokens
		self.speaker = speaker
		self.mor = mor
		self.gra = gra

	def add_tier_info(self, mor=[], gra=[]):
		self.mor = mor
		self.gra = gra

	def __str__(self):
		return f"speaker:  {self.speaker}\n\
		form:  {self.form}\n\
		items:  {self.items}\n\
		mor:  {self.mor}\n\
		gra:  {self.gra}"

	def __len__(self):
		return len(tokens)


class ChatMeta(object):
	"""docstring for ChatMeta"""
	def __init__(self, arg):
		self.arg = arg
