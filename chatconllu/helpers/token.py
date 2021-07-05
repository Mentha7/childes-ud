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
			return self._multi_str()
		fields = [str(getattr(self, x)) for x in self.__slots__[1:10]]
		return ("\t".join([idx] + fields).replace('None', '_'))

	def _multi_str(self):

		s = ""

		idx = "-".join((str(self.index), str(self.multi)))
		form = self.form
		fields = ['None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
		s += "\t".join([idx, form] + fields).replace('None', '_')

		for n, i in enumerate(range(int(self.index), int(self.multi)+1)):

			s += "\n"

			# form = self.lemma[n]
			# fields = [str(getattr(self, x)[n]) if x is not None else 'None' for x in self.__slots__[2:9]]
			# s += "\t".join([str(i), form] + fields).replace('None', '_')

			form=None if not self.lemma[n] else self.lemma[n]
			lemma=None if not self.lemma[n] else self.lemma[n]
			upos=None if not self.upos[n] else self.upos[n]
			xpos=None if not self.xpos[n] else self.xpos[n]
			feats=None if not self.feats[n] else "|".join(self.feats[n])
			head=None if not self.head[n] else self.head[n]
			deprel=None if not self.deprel[n] else self.deprel[n]
			deps=None if not self.deps[n] else self.deps[n]
			misc=self.misc
			s += f"{str(i)}\t{form}\t{lemma}\t{upos}\t{xpos}\t{feats}\t{head}\t{deprel}\t{deps}\t{misc}"
			s = s.replace('None', '_')

		return s

	def ud_upos():
		pass

	def ud_xpos():
		pass

