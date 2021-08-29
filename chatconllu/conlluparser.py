"""Utilities for parsing files in CoNLL-U format.
"""
import sys, os
import re
import ast
from typing import List, Tuple, Dict, Union
from pathlib import Path

from logger import logger
from helpers.sentence import Sentence
from helpers.token import Token

import pyconll

_TMP_DIR = 'tmp'
_OUT_DIR = 'out'
PUNCT = re.compile("([,.;?!:”])")
def construct_tiers():
	pass


def to_cha(outfile, conll: 'pyconll.Conll'):
	# ---- test print: sentence and word count, headers, utterances ----
	sc = 0  # sentence count
	wc = 0  # word count
	for sentence in conll:
		mor = {}
		gra = []
		has_mor = False
		has_gra = False

		# ---- write headers ----
		if sentence.id is None:  # headers don't have sentence.id
			# logger.debug(sentence._meta)  # dictionary:sentence._meta
			for k, v in list(sentence._meta.items())[:-1]:
				linenum, _, header = k.lstrip().partition("\t")  # strip initial tabs
				#   # logger.debug(linenum, header)
				outfile.write(header+"\n")
		elif 'chat_sent' in sentence._meta.keys():
			# ---- sentences (utterances) ----
			sc += 1  # increment sentence count
			# logger.debug(f"* {sentence.meta_value('speaker')}:\t{sentence.meta_value('chat_sent')}")  # put back utterances (main)
			outfile.write(f"*{sentence.meta_value('speaker')}:\t{sentence.meta_value('chat_sent')}\n")
			# ----- check if mor and gra tier are present ----
			#   > check the first token for each sentence (or the second for multiword tokens)
			if sentence._tokens:
				t = sentence._tokens[0]
				if t.is_multiword():
					logger.debug(f"{t.form} is a multi-word token.")
					t = sentence._tokens[1]
				if t.lemma is not None: has_mor = True
				if t.head is not None: has_gra = True

			else:  # sentence is empty?
				logger.warning(f"sent {sentence.id} has no tokens, check if it's well-formed.")  # utterances like `xxx .` are still recoverable.

			if has_gra and has_mor:
				# logger.debug(f"sent {sentence.id} has both gra and mor tiers.")
				logger.debug(f"%\mor:{sentence.meta_value('mor')}")
				for i, word in enumerate(sentence):
					m = ''
					g = ''
					wc += 1
					# logger.debug(word.conll())
					# logger.info(f"word.misc:{word.misc}")
					# quit()
					# if 'form' in word.misc.keys():  # form is in word.misc
					#   # logger.debug(f"word.misc: {word.misc}")
					#   m = next(iter(word.misc['form']))

					if 'components' in word.misc.keys():
						for v in word.misc['components']:
							tmp = '+' + v.replace('@', '|').replace('#', '+')
							# logger.info(tmp)
							m = '|'.join([word.xpos, tmp])
						# logger.info(f"compound MOR: {m}")
					elif word.lemma and re.match(PUNCT, word.lemma):  # punctuations mor is form
						m = word.lemma
					elif word.lemma and word.xpos:
						m = '|'.join([word.xpos, word.lemma])
						if 'feats' in word.misc.keys():
							for f in word.misc['feats']:
								tmp = f.replace('#', '')
								m += tmp
							# logger.warn(f"added feats: {m}")
						if 'translation' in word.misc.keys():
							for t in word.misc['translation']:
								m += '=' + t
								# logger.warn(f"added translation: {m}")
					mor[word.id] = m
				mwt = [sentence[k] for k in mor.keys() if '-' in k]
				for k in mwt:
					if 'type' in k.misc.keys():
						start, _, end = k.id.partition('-')
						type = next(iter(k.misc['type']))
						m = type.join(mor.pop(str(n)) for n in range(int(start), int(end) + 1))
						logger.warn(m)
						mor[k.id] = m
				outfile.write(f"%mor:\t{' '.join(list(mor.values()))}\n")
				outfile.write(f"%MOR:\t{' '.join(list(mor.values()))}\n")

				# logger.debug(list(mor.values()))
				# logger.debug(len(list(mor.values())))
				# logger.debug(len(ast.literal_eval(sentence.meta_value('mor'))))
				assert len(list(mor.values())) == len(ast.literal_eval(sentence.meta_value('mor')))
				# assert list(mor.values()) == ast.literal_eval(sentence.meta_value('mor'))  # TO-DO: add back FEATs
				# quit()
		else:  # no utterance '0 .'
			sc += 1
			# logger.warning(f"sent {sentence.id} has no utterance.")
	outfile.write("@End")
	# logger.info(f"{f.stem + f.suffix} has {sc} sentences, {wc} tokens.")
	# fn = f.with_suffix(".cha")
	# quit()


def conllu2chat(files: List['pathlib.PosixPath'], remove=True):
	for f in files:
		# if f.with_suffix(".cha").is_file():
		#   continue

		# ---- load conllu file ----
		logger.info(f"Loading {f} with pyconll...")
		conll = pyconll.load_from_file(f)

		fn = Path(f.stem + "_pyconll" + ".cha")
		with open(fn, 'w', encoding='utf-8') as ff:
			to_cha(ff, conll)

		if remove:
			tmp_file = Path(_TMP_DIR, f"{f.stem}_new").with_suffix(".cha")
			if tmp_file.is_file():
				os.remove(tmp_file)
