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

_OUT_DIR = Path('tests', 'out')
_OUT_DIR.mkdir(parents=True, exist_ok=True)
PUNCT = re.compile("([,.;?!:”])")
STANDARD = [
	'sent_id',
	'text',
	'chat_sent',
	'speaker',
	'mor',
	'gra',
	'text =',
	'final',
	'empty_speaker',
	'empty_chat_sent',
	'final_sents',
	'final_comments'
	]

def construct_mwe(sentence, tier):
	# -------- construct tier for multi-word tokens--------
	mwt = [sentence[k] for k in tier.keys() if '-' in k]
	for k in mwt:
		if 'type' in k.misc.keys():
			start, _, end = k.id.partition('-')
			type = next(iter(k.misc['type']))
			p = type.join(tier.pop(str(n)) for n in range(int(start), int(end) + 1))
		else:  # use arbitrary symbol '~'
			p = '~'.join(tier.pop(str(n)) for n in range(int(start), int(end) + 1))
		tier[k.id] = p
	return tier

def construct_gra_cnl(sentence, is_cnl=False):
	token_count = 0
	gra = []
	for i, word in enumerate(sentence):
		g = ''
		if '-' in word.id:
			continue
		elif not is_cnl:
			deprel = 'None'
			token_count += 1
			head = 'None'
			g = f'{token_count}|{head}|{deprel}'
			g = g.replace('None', '_')
		else:
			deprel = word.deprel if word.deprel else 'None'
			token_count += 1
			head = word.head if word.head else 'None'
			g = f'{token_count}|{head}|{deprel}'
		gra.append(g)
	return gra

def construct_mor_pos(sentence, is_pos=False):
	mor = {}
	for i, word in enumerate(sentence):
		m = ''
		if not '-' in word.id:
			if not is_pos:
				if word.lemma and re.match(PUNCT, word.lemma) and len(word.lemma)==1:  # punctuation's mor is form
					m = word.lemma
				else:
					upos = 'None'
					lemma = 'None'
					m = f'{upos}|{lemma}'
					m = m.replace('None', '_')
			else:
				upos = word.upos.lower() if word.upos else 'None'
				lemma = word.lemma if word.lemma else 'None'
				m = f'{upos}|{lemma}'
		mor[word.id] = m
	return mor

def construct_tiers(sentence, has_mor, has_gra, generate_mor=False, generate_gra=False, generate_cnl=False, generate_pos=False):
	mor = {}
	gra = []
	cnl = []
	pos = {}
	token_count = 0
	cnl_count = 0
	if has_mor and has_gra:
		for i, word in enumerate(sentence):
			m = ''
			g = ''
			# -------- reconstruct %mor --------
			if 'components' in word.misc.keys():  #compound
				for v in word.misc['components']:
					tmp = '+' + v.replace('@', '|').replace('^', '+')  # reverse to MOR coding
					m = '|'.join([word.xpos, tmp])
			elif word.lemma and word.xpos and word.xpos != 'punct':
				m = '|'.join([word.xpos, word.lemma])
				if 'feats' in word.misc.keys():
					for f in word.misc['feats']:
						tmp = f.replace('^', '')
						m += tmp
				if 'translation' in word.misc.keys():
					for t in word.misc['translation']:
						m += '=' + t
			if word.lemma and re.match(PUNCT, word.lemma) and len(word.lemma)==1:  # punctuation's mor is form
				m = word.lemma
			if 'form' in word.misc.keys():
				# print("has key1")
				for f in word.misc['form']:
					# print(f)
					m = f.replace('@', '|')
					# print(m)
			if 'prefix' in word.misc.keys():
				for p in word.misc['prefix']:
					m  = p + "#" + m
			mor[word.id] = m
			# -------- reconstruct %gra --------
			if '-' in word.id:
				continue
			else:
				if 'gr' in word.misc.keys():
					deprel = word.misc['gr'].pop()
				else:
					deprel = 'None'
				token_count += 1
				if 'head' in word.misc.keys():
					for h in word.misc['head']:
						head = h
				else:
					head = word.head if word.head else 'None'
				g = f'{token_count}|{head}|{deprel.upper()}'
				g = g.replace('None', '_')
				gra.append(g)
		# -------- reconstruct %mor for multi-word tokens--------
		construct_mwe(sentence, mor)
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
			if 'prefix' in word.misc.keys():
				for p in word.misc['prefix']:
					m  = p + "#" + m
				# m = f"{word.misc['prefix'][0]}#{m}"
			mor[word.id] = m
		# -------- reconstruct %mor for multi-word tokens--------
		construct_mwe(sentence, mor)
	elif has_gra:
		for i, word in enumerate(sentence):
			g = ''
			# -------- reconstruct %gra --------
			if '-' in word.id:
				continue
			else:
				if 'gr' in word.misc.keys():
					deprel = word.misc['gr'].pop()
				else:
					deprel = 'None'
				token_count += 1
				if 'head' in word.misc.keys():
					for h in word.misc['head']:
						head = h
				else:
					head = word.head
				g = f'{token_count}|{head}|{deprel.upper()}'
				gra.append(g)
	if generate_cnl:
		cnl = construct_gra_cnl(sentence, generate_cnl)
	if generate_gra:  # construct empty %gra
		gra = construct_gra_cnl(sentence)
	if generate_pos:
		pos = construct_mor_pos(sentence, generate_pos)
		# -------- construct %pos for multi-word tokens--------
		construct_mwe(sentence, pos)
	if generate_mor:  # construct empty %mor
		mor = construct_mor_pos(sentence)
		# -------- reconstruct %mor for multi-word tokens--------
		construct_mwe(sentence, mor)

	return mor, gra, cnl, pos

def process_final_sents(meta_key: str, sentence):
	if meta_key.startswith("final_") and meta_key not in STANDARD:
		name = meta_key.replace("final_", '')[:-2]
		print(name)
		if len(name)==3 and name.islower():
			val = ' '.join(ast.literal_eval(sentence.meta_value(meta_key)))
			return f"%{name}:\t{val}\n"
		elif name.isupper():
			return f"*{name}:\t{sentence.meta_value(meta_key)}\n"
	if meta_key.endswith("comments"):
		return f"{sentence.meta_value(meta_key)}\n"

def to_cha(outfile, conll: 'pyconll.Conll', generate_mor=False, generate_gra=False, generate_cnl=False, generate_pos=False):
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
			# ---- empty sentences (utterances) ----
			if 'empty_chat_sent' in sentence._meta.keys():
				outfile.write(f"*{sentence.meta_value('empty_speaker')}:\t{sentence.meta_value('empty_chat_sent')}\n")
				for k in sentence._meta.keys():
					if k.startswith('empty_') and k not in STANDARD and '\t' not in k:
						_, _, tier = k.partition('_')
						val = ' '.join(ast.literal_eval(sentence.meta_value(k)))
						outfile.write(f"%{tier}:\t{val}\n")
			# ---- sentences (utterances) ----
			outfile.write(f"*{sentence.meta_value('speaker')}:\t{sentence.meta_value('chat_sent')}\n")
			# ----- check if mor and gra tier are present ----
			if 'mor' in sentence._meta.keys(): has_mor = True
			if 'gra' in sentence._meta.keys(): has_gra = True
			# check the first token for each sentence (or the second for multiword tokens)
			if sentence._tokens:
				t = sentence._tokens[0]
				if t.is_multiword():
					# logger.debug(f"{t.form} is a multi-word token.")
					t = sentence._tokens[1]
				if t.lemma is not None:
					has_mor = True
				else: has_mor = False
				if t.head is not None: has_gra = True
				else: has_gra = False
			else:  # sentence is empty?
				logger.warning(f"sent {sentence.id} has no tokens, check if it's well-formed.")  # utterances like `xxx .` are still recoverable.

			mor, gra, cnl, pos = construct_tiers(sentence, has_mor, has_gra, generate_mor, generate_gra, generate_cnl, generate_pos)
			if mor:
				outfile.write(f"%mor:\t{' '.join(list(mor.values()))}\n")
				# outfile.write(f"%MOR:\t{' '.join(ast.literal_eval(sentence.meta_value('mor')))}\n")  # for easy comparison
				# outfile.write('\n')  # easy on the eye
			if gra:
				outfile.write(f"%gra:\t{' '.join(gra)}\n")
				# outfile.write(f"%GRA:\t{' '.join(ast.literal_eval(sentence.meta_value('gra')))}\n")  # for easy comparison
				# outfile.write('\n')  # easy on the eye
				# logger.debug(list(mor.values()))
			# if 'mor' in sentence._meta.keys():
				# logger.info(sc)
				# logger.debug(len(list(mor.values())))
				# logger.debug(len(ast.literal_eval(sentence.meta_value('mor'))))
				# logger.debug(list(mor.values()))
				# logger.debug(ast.literal_eval(sentence.meta_value('mor')))
				# assert len(list(mor.values())) == len(ast.literal_eval(sentence.meta_value('mor')))
				# assert ' '.join(list(mor.values())) == ' '.join(ast.literal_eval(sentence.meta_value('mor')))
			# if 'gra' in sentence._meta.keys():
				# logger.info(sc)
				# logger.debug(len(gra))
				# logger.debug(len(ast.literal_eval(sentence.meta_value('gra'))))
				# logger.debug(gra)
				# logger.debug(ast.literal_eval(sentence.meta_value('gra')))
				# assert len(gra) == len(ast.literal_eval(sentence.meta_value('gra')))
				# assert ' '.join(gra) == ' '.join(ast.literal_eval(sentence.meta_value('gra')))
			if cnl:
				outfile.write(f"%cnl:\t{' '.join(cnl)}\n")
			if pos:
				outfile.write(f"%pos:\t{' '.join(list(pos.values()))}\n")
		else:  # no utterance '0 .'
			logger.warning(f"sent {sentence.id} has no utterance.")
		for k in sentence._meta.keys():
			if not k.startswith('@') and not k.startswith('empty_') and not k.startswith('final_') and k not in STANDARD and '\t' not in k:
				try:
					val = ' '.join(ast.literal_eval(sentence.meta_value(k)))
					outfile.write(f"%{k}:\t{val}\n")
				except SyntaxError:
					continue
				except ValueError:
					continue
		for k in sentence._meta.keys():
			s = process_final_sents(k, sentence)
			if s:
				outfile.write(s)
		if 'final' in sentence._meta.keys():
			final = ast.literal_eval(sentence.meta_value('final'))
	if final:
		for fc in final:
			outfile.write(f"{fc}\n")
	# outfile.write("@End")
	# logger.info(f"{f.stem + f.suffix} has {sc} sentences, {wc} tokens.")
	# fn = f.with_suffix(".cha")
	# quit()


def conllu2chat(files: List['pathlib.PosixPath'], generate_mor=False, generate_gra=False, generate_cnl=False, generate_pos=False):
	for f in files:
		# if f.with_suffix(".cha").is_file():
		#   continue

		# ---- load conllu file ----
		logger.info(f"Loading {f} with pyconll...")
		conll = pyconll.iter_from_file(f)
		print(f.stem, _OUT_DIR)
		fn = Path(_OUT_DIR, f.stem + "_pyconll" + ".cha")
		print(fn)
		with open(fn, 'w', encoding='utf-8') as ff:
			to_cha(ff, conll, generate_mor, generate_gra, generate_cnl, generate_pos)
