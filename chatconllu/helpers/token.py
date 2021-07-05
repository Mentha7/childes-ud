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
		s = ""
		idx = str(self.index)
		if self.multi:
			return self._multi_str()
		s += f"{idx}\t{self.form}\t{self.lemma}\t{self.upos}\t{self.xpos}\t{self.feats}\t{self.head}\t{self.deprel}\t{self.deps}\t{self.misc}"
		s = s.replace('None', '_')
		return s

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

			form=self.lemma[n]
			lemma=self.lemma[n]
			upos=self.upos[n]
			xpos=self.xpos[n]
			feats="|".join(self.feats[n])
			head=self.head[n]
			deprel=self.deprel[n]
			deps=self.deps[n]
			misc=self.misc

			s += f"{str(i)}\t{form}\t{lemma}\t{upos}\t{xpos}\t{feats}\t{head}\t{deprel}\t{deps}\t{misc}"
			s = s.replace('None', '_')

		return s

	def ud_upos():
		pass

	def ud_xpos():
		pass

	def ud_feats():
		pass
