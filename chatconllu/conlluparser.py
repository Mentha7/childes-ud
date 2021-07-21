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

PUNCT = re.compile("([,.;?!:”])")

def conllu2chat(files: List['pathlib.PosixPath']):
	for f in files:
		# if f.with_suffix(".cha").is_file():
		#   continue

		# ---- load conllu file ----
		logger.info(f"Loading {f} with pyconll...")
		conll = pyconll.load_from_file(f)

		# ---- test print: sentence and word count, headers, utterances ----
		sc = 0
		wc = 0
		for sentence in conll:
			mor = {}
			gra = []
			has_mor = False
			has_gra = False

			# ---- skip headers ----
			if sentence.id is None:  # skip headers
				# logger.debug(sentence._meta)
				for k, v in sentence._meta.items():
					linenum, _, header = k.partition("\t")  # double check for lines starting with tabs!
					# logger.debug(linenum, header)
			elif 'chat_sent' in sentence._meta.keys():
				# ---- sentences (utterances) ----
				sc += 1  # increment sentence count
				logger.debug(f"* {sentence.meta_value('speaker')}:\t{sentence.meta_value('chat_sent')}")  # put back utterances (main)
				# ----- determine which tiers are present ----
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
					logger.debug(f"sent {sentence.id} has both gra and mor tiers.")
					logger.debug(f"{sentence.meta_value('mor')}")
					for i, word in enumerate(sentence):
						m = ''
						g = ''
						wc += 1
						# logger.debug(word.conll())
						# print(word.misc)
						# quit()
						if 'form' in word.misc.keys():  # form is in word.misc
							# logger.debug(f"word.misc: {word.misc}")
							m = next(iter(word.misc['form']))
						elif word.lemma and re.match(PUNCT, word.lemma):  # punctuations mor is form
							m = word.lemma
						elif word.lemma and word.xpos:
							m = '|'.join([word.xpos, word.lemma])
						mor[word.id] = m
					mwt = [k for k in mor.keys() if '-' in k]
					for k in mwt:
						start, _, end = k.partition('-')
						m = "~".join(mor.pop(str(n)) for n in range(int(start), int(end) + 1))
						mor[k] = m


					logger.debug(list(mor.values()))
					logger.debug(len(list(mor.values())))
					logger.debug(len(ast.literal_eval(sentence.meta_value('mor'))))
					assert len(list(mor.values())) == len(ast.literal_eval(sentence.meta_value('mor')))
					# assert list(mor.values()) == ast.literal_eval(sentence.meta_value('mor'))  # TO-DO: add back FEATs
					# quit()
#
			else:  # no utterance '0 .'
				sc += 1
				logger.warning(f"sent {sentence.id} has no utterance.")

		# logger.info(f"{f.stem + f.suffix} has {sc} sentences, {wc} tokens.")
		# fn = f.with_suffix(".cha")
		# quit()
