"""
Utilities to parse .cha files.
"""
import sys
import re
import fileinput
from pathlib import Path

from collections import OrderedDict

from logger import logger
from helpers.sentence import Sentence

BROWN = "/home/jingwen/Desktop/thesis/Brown/"
FILE = "test.cha"
TMP_DIR = 'tmp'

old = re.compile('^\\*')
square_brackets = ['^\\[', '.*\\]$']
sqr = re.compile('|'.join(e for e in square_brackets))


def list_files(dir):
	return (x for x in Path(dir).glob("**/*.cha") if not x.name.startswith("._"))

def read_file(filename):
	""" Writes a new .cha file for easier parsing.
	"""
	fn = filename.split('.')[0]
	with open(Path(TMP_DIR, f'{fn}_new.cha'), 'w', encoding='utf-8') as f:
		for line in fileinput.input(Path(BROWN, filename), inplace=False):  # need to change path
			match = old.match(line)
			print('\n'+ line.strip('\n').replace('    ', '\t') if match or line == '@End\n' else line.strip('\n').replace('    ', '\t'), file=f)

def parse_chat(filename):
	""" Read file line by line, if line:
		- starts with @: metadata
		- starts with *: utterance (1)
		- starts with %: tiers (n)
		note:
		- field and value are separated by tabs
		- labels are in square brackets
	"""
	meta, utterances = [], []
	fn = filename.split('.')[0]
	with open(Path(TMP_DIR, f'{fn}_new.cha'), 'r', encoding='utf-8') as f:
		lines = []
		for l in f:
			l = l.strip('\n')
			if l.startswith('@'):
				meta.append(l)
				# print(f'{l} --> meta')
			elif l:
				if l.startswith('\t'):  # continue on next line
					# print(lines[-1])
					lines[-1] += ' ' + l.replace('\t', '')  # remove initial tab
					# print(lines[-1])
				else:
					lines.append(l)
			elif lines:
				# print(lines)
				utterances.append(lines)
				lines = []
	# print(len(meta))
	# print(utterances)
	# print(len(utterances))
	return meta, utterances

def check_token(surface):
	clean=''
	if surface.startswith('&'):   # phonological forms
		pass
	clean = surface.replace('(', '').replace(')', '').replace('@q', '') # @q ismeta-lingustic use
		# skip all other special forms (@c @s etc.)
	if '@' in surface or 'xxx' in surface:  # skip unintelligible words too
		pass
	return surface, clean


def create_sentence(idx, lines):
	"""Given lines, create a Sentence object.
		__slots__ = ['speaker',
					 'tiers',
					 'gra',
					 'mor',
					 'tokens',
					 'clean',
					 'comments',
					 'sent_id',
					 ]
	"""
	speaker = lines[0][1:4]
	# print(speaker)

	# tiers = [x.split('\t')[0][:-1] for x in lines[1:]]
	# print(tiers)

	tokens = lines[0].split('\t')[-1].split(' ')
	labels = list(filter(sqr.match, tokens))
	tmp = [t for t in tokens if t not in labels]
	clean = []
	for t in tmp:
		# check t is clean form
		_, t = check_token(t)
		clean.append(t)

	tiers_dict = OrderedDict()
	comments = []
	for t in lines[1:]:
		tl = t.split('\t')
		tier_name = tl[0][1:-1]
		tiers_dict[tier_name] = tl[-1].replace('~', ' ').split(' ')
		if tier_name != 'mor' and tier_name != 'xmor' and tier_name != 'gra':
			comments.append(t)
	print(comments)

	# print(tiers_dict.keys())
	gra, mor = None, None
	if ('mor' or 'xmor') and 'gra' in tiers_dict:
		mor = tiers_dict.get('mor') if 'mor' in tiers_dict else tiers_dict.get('xmor')
		gra = tiers_dict.get('gra')
	# print(len(clean), len(mor), len(gra))
	# if len(gra)!=len(mor):
	# 	print(f'======== sent_id:{idx+1} ========')
	# 	print(clean)
	# 	print(len(clean), len(mor), len(gra))
	# 	print(mor)
	# 	print(gra)


	return Sentence(speaker=speaker,
				 	tiers=tiers_dict.keys(),
				 	gra=gra,
				 	mor=mor,
				 	tokens=tokens,
				 	clean=clean,
				 	comments=comments,
				 	sent_id=(idx+1),
				 	)


if __name__ == "__main__":
	# logger.info(f"listing all .cha files in {BROWN}...")
	# files = list_files(BROWN)
	# try:
	# 	while True:
	# 		i = next(files)
	# 		print(i)
	# except StopIteration:
	# 	pass

	# # read file
	# logger.info(f"reading {FILE}...")
	# read_file(FILE)
	logger.info(f"parsing {FILE}...")
	meta, utterances = parse_chat(FILE)
	# n = -2
	# create_sentence(n, utterances[n])
	for idx, utterance in enumerate(utterances):
		create_sentence(idx, utterance)
