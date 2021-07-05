class Token(object):
	"""docstring for Token"""

	__slots__ = ['index',
				 'form',
				 'lemma',
				 'upos',
				 'xpos',
				 'feats',
				 'head',
				 'deprel',
				 'deps',
				 'misc',
				 'multi'
				 ]

	def __init__(self,
				 index=0,
				 form=None,
				 lemma=None,
				 upos=None,
				 xpos=None,
				 feats=None,
				 head=None,
				 deprel=None,
				 deps=None,
				 misc=None,
				 multi=0,
				 ):

		self.index = int(index)
		self.form = form
		self.lemma = None if not lemma else lemma
		self.upos = None if not upos else upos
		self.xpos = None if not xpos else xpos
		self.feats = None if not feats else feats
		self.head = None if not head else head
		self.deprel = None if not deprel else deprel
		self.deps = None if not deps else deps
		self.misc = None if not misc else misc
		self.multi = multi

	def __str__(self):
		fields = [str(getattr(self, x)) for x in self.__slots__[:]]
		return ("\n".join(fields))

	def conllu_str(self):
		"""Writes token as one line in conllu file. If Token is multi, write span.
		   Adopted from conllu.py.
		"""
		idx = str(self.index)
		if self.multi:
			idx = "-".join((str(self.index), str(self.multi)))
		fields = [str(getattr(self, x)) for x in self.__slots__[1:10]]
		return ("\t".join([idx] + fields).replace('None', '_'))

	def ud_upos():
		pass

	def ud_xpos():
		pass

