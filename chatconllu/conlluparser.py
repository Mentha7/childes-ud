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
STANDARD = ['sent_id', 'text', 'chat_sent', 'speaker', 'mor', 'gra', 'text =', 'final']

def construct_tiers(sentence, has_mor, has_gra):
	mor = {}
	gra = []
	token_count = 0
	if has_mor and has_gra:
		for i, word in enumerate(sentence):
			m = ''
			g = ''
			# -------- reconstruct %mor --------
			if 'components' in word.misc.keys():  #compound
				for v in word.misc['components']:
					tmp = '+' + v.replace('@', '|').replace('^', '+')  # reverse to MOR coding
					m = '|'.join([word.xpos, tmp])
			elif word.lemma and word.xpos != 'punct':
				m = '|'.join([word.xpos, word.lemma])
				if 'feats' in word.misc.keys():
					for f in word.misc['feats']:
						tmp = f.replace('^', '')
						m += tmp
				if 'translation' in word.misc.keys():
					for t in word.misc['translation']:
						m += '=' + t
			if word.lemma and re.match(PUNCT, word.lemma) and len(word.lemma)==1:  # punctuations mor is form
				m = word.lemma
			if 'form' in word.misc.keys():
				# print("has key1")
				for f in word.misc['form']:
					# print(f)
					m = f.replace('@', '|')
					# print(m)
			mor[word.id] = m
			# -------- reconstruct %gra --------
			if '-' in word.id:
				continue
			else:
				token_count += 1
				g = f'{token_count}|{word.head}|{word.deprel.upper()}'
				gra.append(g)
		# -------- reconstruct %mor for multi-word tokens--------
		mwt = [sentence[k] for k in mor.keys() if '-' in k]
		for k in mwt:
			if 'type' in k.misc.keys():
				start, _, end = k.id.partition('-')
				type = next(iter(k.misc['type']))
				m = type.join(mor.pop(str(n)) for n in range(int(start), int(end) + 1))
				mor[k.id] = m
	elif has_mor:
		for i, word in enumerate(sentence):
			m = ''
			# -------- reconstruct %mor --------
			if 'components' in word.misc.keys():
				for v in word.misc['components']:
					tmp = '+' + v.replace('@', '|').replace('^', '+')
					m = '|'.join([word.xpos, tmp])
			elif word.lemma and word.xpos != 'punct':
				m = '|'.join([word.xpos, word.lemma])
				if 'feats' in word.misc.keys():
					for f in word.misc['feats']:
						tmp = f.replace('^', '')
						m += tmp
				if 'translation' in word.misc.keys():
					for t in word.misc['translation']:
						m += '=' + t
			if word.lemma and re.match(PUNCT, word.lemma) and len(word.lemma)==1:  # punctuations mor is form
				m = word.lemma
			if 'form' in word.misc.keys():
				# print("has key2")
				for f in word.misc['form']:
					# print(f)
					m += f.replace('@', '|')
					# print(m)
			mor[word.id] = m
		# -------- reconstruct %mor for multi-word tokens--------
		mwt = [sentence[k] for k in mor.keys() if '-' in k]
		for k in mwt:
			if 'type' in k.misc.keys():
				start, _, end = k.id.partition('-')
				type = next(iter(k.misc['type']))
				m = type.join(mor.pop(str(n)) for n in range(int(start), int(end) + 1))
				mor[k.id] = m
		# --------- reconstruct empty %gra --------
	elif has_gra:
		for i, word in enumerate(sentence):
			g = ''
			# -------- reconstruct %gra --------
			if '-' in word.id:
				continue
			else:
				token_count += 1
				g = f'{token_count}|{word.head}|{word.deprel.upper()}'
				gra.append(g)
			# -------- reconstruct empty %mor --------
	return mor, gra



def to_cha(outfile, conll: 'pyconll.Conll'):
	final = []
	for sentence in conll:
		mor = {}
		gra = []
		has_mor = False
		has_gra = False

		if 'chat_sent' in sentence._meta.keys():
			# ---- write headers ----
			for k in sentence._meta.keys():
				if k.startswith('@'):
					outfile.write(f"{k}\n")
			# ---- sentences (utterances) ----
			outfile.write(f"*{sentence.meta_value('speaker')}:\t{sentence.meta_value('chat_sent')}\n")
			# ----- check if mor and gra tier are present ----
			if 'mor' in sentence._meta.keys(): has_mor = True
			if 'gra' in sentence._meta.keys(): has_gra = True

			else:  # sentence is empty?
				logger.warning(f"sent {sentence.id} has no tokens, check if it's well-formed.")  # utterances like `xxx .` are still recoverable.

			mor, gra = construct_tiers(sentence, has_mor, has_gra)
			if mor:
				outfile.write(f"%mor:\t{' '.join(list(mor.values()))}\n")
				# outfile.write(f"%MOR:\t{' '.join(ast.literal_eval(sentence.meta_value('mor')))}\n")  # for easy comparison
				# outfile.write('\n')  # easy on the eye
			if gra:
				outfile.write(f"%gra:\t{' '.join(gra)}\n")
				# outfile.write(f"%GRA:\t{' '.join(ast.literal_eval(sentence.meta_value('gra')))}\n")  # for easy comparison
				# outfile.write('\n')  # easy on the eye
				# logger.debug(list(mor.values()))
			if 'mor' in sentence._meta.keys():
				# logger.info(sc)
				# logger.debug(len(list(mor.values())))
				# logger.debug(len(ast.literal_eval(sentence.meta_value('mor'))))
				# logger.debug(list(mor.values()))
				# logger.debug(ast.literal_eval(sentence.meta_value('mor')))
				assert len(list(mor.values())) == len(ast.literal_eval(sentence.meta_value('mor')))
				assert ' '.join(list(mor.values())) == ' '.join(ast.literal_eval(sentence.meta_value('mor')))
			if 'gra' in sentence._meta.keys():
				# logger.info(sc)
				# logger.debug(len(gra))
				# logger.debug(len(ast.literal_eval(sentence.meta_value('gra'))))
				# logger.debug(gra)
				# logger.debug(ast.literal_eval(sentence.meta_value('gra')))
				assert len(gra) == len(ast.literal_eval(sentence.meta_value('gra')))
				assert ' '.join(gra) == ' '.join(ast.literal_eval(sentence.meta_value('gra')))
		else:  # no utterance '0 .'
			logger.warning(f"sent {sentence.id} has no utterance.")
		for k in sentence._meta.keys():
			if not k.startswith('@') and k not in STANDARD and '\t' not in k:
				val = ' '.join(ast.literal_eval(sentence.meta_value(k)))
				outfile.write(f"%{k}:\t{val}\n")
		if 'final' in sentence._meta.keys():
			final = ast.literal_eval(sentence.meta_value('final'))
	if final:
		for fc in final:
			outfile.write(f"{fc}\n")
	# outfile.write("@End")
	# logger.info(f"{f.stem + f.suffix} has {sc} sentences, {wc} tokens.")
	# fn = f.with_suffix(".cha")
	# quit()


def conllu2chat(files: List['pathlib.PosixPath']):
	for f in files:
		# if f.with_suffix(".cha").is_file():
		#   continue

		# ---- load conllu file ----
		logger.info(f"Loading {f} with pyconll...")
		conll = pyconll.load_from_file(f)

		fn = Path(f.stem + "_pyconll" + ".cha")
		with open(fn, 'w', encoding='utf-8') as ff:
			to_cha(ff, conll)
