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
from helpers.token import Token

BROWN = "/home/jingwen/Desktop/thesis/Brown/"
# BROWN = "/home/jingwen/Desktop/thesis/"
# FILE = "test.cha"
FILE = "test_angle.cha"
# FILE = "019JC.cha"
TMP_DIR = 'tmp'

utterance = re.compile('^\\*')
# square_brackets = ['^\\[', '.*\\]$']
# sqr = re.compile('|'.join(e for e in square_brackets))


def list_files(dir):
	return (x for x in Path(dir).glob("**/*.cha") if not x.name.startswith("._"))


def read_file(filename):
	""" Writes a new .cha file for easier parsing.
	"""
	fn = filename.split('.')[0]
	with open(Path(TMP_DIR, f'{fn}_new.cha'), 'w', encoding='utf-8') as f:
		for line in fileinput.input(Path(BROWN, filename), inplace=False):  # need to change path
			match = utterance.match(line)
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

	meta = {}
	utterances = []
	fn = filename.split('.')[0]

	with open(Path(TMP_DIR, f'{fn}_new.cha'), 'r', encoding='utf-8') as f:

		lines = []

		for i, l in enumerate(f.readlines()):
			l = l.strip('\n')
			if l.startswith('@'):
				meta[i] = l
			elif l:
				while l.startswith('\t'):  # tab marks continuation of last line
					lines[-1] += l.replace('\t', ' ')  # replace initial tab with a space
					break
				else:
					lines.append(l)
			elif lines:
				utterances.append(lines)
				lines = []

	return meta, utterances


def normalise_utterance(line: str):
	"""Adopted and modified from coltekin/childes-tr/misc/parse-chat.py
	"""

	until_rangleb = re.compile("([^>]+)>")
	until_rbracket = re.compile("([^]]+)]")
	until_eow = re.compile(r"[^,.;?!”<> ]+")
	punct_re = re.compile("([,.;?!:”])")

	# ---- define patterns to omit ----
	pause = r"^\(\.+\)"  # (.), (..), (...)
	timed_pause = r"^\((\d+?:)?(\d+?)?\.(\d+?)?\)"  # ((min:)(sec).(decimals))
	retracing = r"^<.*?> \[/[/?]\]"  # <xx xx> [//] or [/?]
	repetitions = r"^\[x \d+\]"  # [x (number)]
	best_guess = r"^\[\?\]"  # [?]
	error = r"^\[\^ e.*?]"  # [^ exxxx]
	error_star = r"^\[\* .*?\]"  # [* xxx]
	comment_on_main = r"^\[% .*?\]"  # [% xxx]
	complex_local_event = r"^\[\^ .*?\]"  # [^ xxx]
	postcodes = r"^\[\+ .*?\]"  # [+ xxx]
	trailing_off = r"\+..."  # +...



	omission = [pause,
				 timed_pause,
				 retracing,
				 repetitions,
				 best_guess,
				 error,
				 error_star,
				 comment_on_main,
				 complex_local_event,
				 postcodes,
				 ]
	# ---- compile regex patterns ----
	to_omit = re.compile('|'.join(o for o in omission))  # <whatever> [/?] or <whatever> [//]
	to_expand = re.compile(r"^<.*?> \[\?\]")
	to_replace = re.compile(r"^\[::? ")


	tokens = []
	prev_tokens = []
	positions = {}

	i = 0
	while i < len(line):
		if line[i] == " ":
			i += 1
		elif re.match(to_omit, line[i:]):
			s = re.match(to_omit, line[i:])
			tokens.extend(prev_tokens)
			i += len(s.group(0))
			prev_tokens = []
		elif re.match(to_expand, line[i:]):  # expand contents in <>
			s = re.match(to_expand, line[i:])
			tokens.extend(prev_tokens)
			i += len(s.group(0))
			prev_tokens = s.group(0)[1:-5].strip().split()  # remove '<' and '> [?]'
		elif re.match(to_replace, line[i:]):
			s = re.match(to_replace, line[i:])
			i += len(s.group(0))
			m = re.match(until_rbracket, line[i:])
			tokens.extend(m.group(1).strip().split())
			i += len(m.group(0))
			prev_tokens = []
		elif re.match(trailing_off, line[i:]):  # above punctuation block
			tokens.extend(prev_tokens)
			s = re.match(trailing_off, line[i:])
			i += len(s.group(0))
			prev_tokens = [s.group(0).strip()[1:]]  # remove '+'
		elif re.match(punct_re, line[i:]):  # punctuations
			tokens.extend(prev_tokens)
			prev_tokens = [line[i]]
			i += 1
		else:  # normal tokens
			tokens.extend(prev_tokens)
			m = re.match(until_eow, line[i:])
			prev_tokens = [m.group(0)]
			i += len(m.group(0))

	tokens.extend(prev_tokens)

	return tokens, positions


def check_token(surface):
	"""Adopted and modified from coltekin/childes-tr/misc/parse-chat.py
	"""

	# ---- define unidentifiable patterns ----
	unintelligible = r"(.*?)?xxx(.*?)?"
	phono_coding = "yyy"
	untranscribed = "www"
	phono_fragments = r"^&"
	unidentifiable = [unintelligible,
						phono_coding,
						untranscribed,
						phono_fragments,
						]
	to_omit = re.compile("|".join(unidentifiable))


	clean=''
	if re.match(to_omit, surface):   # phonological forms
		return surface, clean

	# define special symbols translation dict
	clean = surface.replace('(', '').replace(')', '')
	clean = clean.replace('@q', '')  # @q is meta-lingustic use
	clean = clean.replace('@o', '')  # @o is onomatopoeia
	clean = clean.replace('0', '')  # 0token is omitted token
	clean = clean.replace('‡', ',')  # prefixed interactional marker
	clean = clean.replace('„', ',')  # suffixed interactional marker
	clean = clean.replace('_', ' ')  # compound

	return surface, clean

def extract_token_info(clean: list, gra: list, mor: list):

	tokens = []

	if len(gra) == len(mor):
		assert len(clean) == len(mor)

		print('*: ', ' '.join(clean), '\n')
		print("gra: ", gra, '\n')
		print("mor: ", mor, '\n')

		for i, t in enumerate(clean):

			index = None
			form = ''
			lemma = None
			upos = None
			xpos = None
			feats = None
			head = None
			deprel = None
			deps = None
			misc = None
			multi = None

			index = gra[i].split('|')[0]
			form = t
			lemma = mor[i].split('|')[-1].split('&')[0]
			# use a mapping for upos and xpos, naively store the values for now
			upos = mor[i].split('|')[0].split(':')[0]
			xpos = mor[i].split('|')[0]

			feats = mor[i].split('|')[-1].split('&')[1:]
			head = gra[i].split('|')[1]
			deprel = gra[i].split('|')[-1].lower()
			deps = f"{head}:{deprel}"


			print(f"index:\t{index}")
			print(f"token:\t{form}")
			print(f"lemma:\t{lemma}")
			print(f"upos:\t{upos}")
			print(f"xpos:\t{xpos}")
			print(f"feats:\t{feats}")
			print(f"head:\t{head}")
			print(f"deprel:\t{deprel}")
			print(f"deps:\t{deps}")
			print(f"misc:\t{misc}")
			print()

			tok = Token(index=index,
						form=form,
						lemma=lemma,
						upos=upos,
						xpos=xpos,
						feats=feats,
						head=head,
						deprel=deprel,
						deps=deps,
						misc=misc,
						multi=multi)
			tokens.append(tok)

	else:  # dealing with multi-word tokens
		assert len(clean) == len(mor)
		# ---- finds '~' in mor tier, take care of token indices ----
		idx = [i for i, g in enumerate(mor) if '~' in g]
		i =  0
		gra_index = 0
		while i < len(clean):
			index = None
			form = ''
			lemma = None
			upos = None
			xpos = None
			feats = None
			head = None
			deprel = None
			deps = None
			misc = None
			multi = None
			if i in idx:  # multi-word
				j = idx.index(i)
				index = int(gra[i+j].split('|')[0])
				num = len(mor[i].split('~'))-1
				print(mor[i].split('~'))
				end_index = index + num
				print(clean[i], i, j, num, index, end_index)

				# ---- create multi-word token ----
				index = index
				form = clean[i]
				lemma = [l.split('|')[-1].split('&')[0] for l in mor[i].split('~')]
				upos = [l.split('|')[0].split(':')[0] for l in mor[i].split('~')]
				xpos = [l.split('|')[0] for l in mor[i].split('~')]

				feats = [l.split('|')[-1].split('&')[1:] for l in mor[i].split('~')]
				head = [gra[x].split('|')[1] for x in range(index, end_index+1)]
				deprel = [gra[x].split('|')[-1].lower() for x in range(index, end_index+1)]
				deps = f"{head}:{deprel}"
				multi = end_index

				# ---- increment indices ----
				i += 1
				gra_index = index
				gra_index += 1

				print(f"index:\t{index}")
				print(f"token:\t{form}")
				print(f"lemma:\t{lemma}")
				print(f"upos:\t{upos}")
				print(f"xpos:\t{xpos}")
				print(f"feats:\t{feats}")
				print(f"head:\t{head}")
				print(f"deprel:\t{deprel}")
				print(f"deps:\t{deps}")
				print(f"misc:\t{misc}")
				print(f"multi:\t{multi}")
				print()

			else:
				# ---- create token ----
				index = int(gra[gra_index].split('|')[0])
				form = clean[i]
				lemma = mor[i].split('|')[-1].split('&')[0]
				upos = mor[i].split('|')[0].split(':')[0]
				xpos = mor[i].split('|')[0]

				feats = mor[i].split('|')[-1].split('&')[1:]
				head = gra[gra_index].split('|')[1]
				deprel = gra[gra_index].split('|')[-1].lower()
				deps = f"{head}:{deprel}"

				# ---- increment indices ----
				i += 1
				gra_index += 1

				print(f"index:\t{index}")
				print(f"token:\t{form}")
				print(f"lemma:\t{lemma}")
				print(f"upos:\t{upos}")
				print(f"xpos:\t{xpos}")
				print(f"feats:\t{feats}")
				print(f"head:\t{head}")
				print(f"deprel:\t{deprel}")
				print(f"deps:\t{deps}")
				print(f"misc:\t{misc}")
				print(f"multi:\t{multi}")
				print()


			tok = Token(index=index,
						form=form,
						lemma=lemma,
						upos=upos,
						xpos=xpos,
						feats=feats,
						head=head,
						deprel=deprel,
						deps=deps,
						misc=misc,
						multi=multi)
			tokens.append(tok)

		# ---- test prints ----
		print(f"* utterance: {' '.join(clean)}\n")
		# print(f"clean:{len(clean)}, mor:{len(mor)}, gra:{len(gra)}")
		print(mor, '\n')
		print(gra, '\n')

	return tokens


def create_sentence(idx, lines):
	"""Given lines, create a Sentence object.

	"""
	# ---- speaker ----
	speaker = lines[0][1:4]
	# print(f"speaker: {speaker}")

	# ---- tiers ----
	tiers = [x.split('\t')[0] for x in lines[1:]]
	# print(tiers)

	# ---- tokens ----
	tokens, meta = normalise_utterance(lines[0].split('\t')[-1])  # normalise line (speaker removed)

	# labels = list(filter(sqr.match, tokens))
	# tmp = [t for t in tokens if t not in labels]

	# ---- clean form ----
	clean = [check_token(t)[1] for t in tokens]
	clean = list(filter(None, clean))  # remove empty strings
	# print(f"normalised utterance: {' '.join(clean)}")

	# ---- tiers dict ----
	tiers_dict = OrderedDict()
	comments = []
	for t in lines[1:]:
		tl = t.split('\t')
		tier_name = tl[0][1:-1]
		tiers_dict[tier_name] = tl[-1].split(' ')  # don't replace '~' just yet
		comments.append(f"# {tier_name}:\t{tl[-1]}")
		# if tier_name != 'mor' and tier_name != 'xmor' and tier_name != 'gra':
		# 	comments.append(t)
	# print(comments)
	# print(tiers_dict.keys())
	# print(tiers_dict.items())

	# ---- gra, mor ----
	gra, mor = None, None
	if ('mor' or 'xmor') and 'gra' in tiers_dict:
		mor = tiers_dict.get('mor') if 'mor' in tiers_dict else tiers_dict.get('xmor')
		gra = tiers_dict.get('gra')
	toks = extract_token_info(clean, gra, mor)
	for tok in toks:
		# print(tok)
		print(tok.conllu_str())



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
	#   while True:
	#       i = next(files)
	#       print(i)
	# except StopIteration:
	#   pass

	# ---- read file ----
	logger.info(f"reading {FILE}...")
	read_file(FILE)


	# ---- parse chat ----
	logger.info(f"parsing {FILE}...")
	meta, utterances = parse_chat(FILE)

	# ---- test print meta ----
	# for i, x in enumerate(meta.items()):
	# 	print(i, x)
	# print(len(meta))
	# ---- test print utterances----
	# for i, l in enumerate(utterances[-2]):
	# 	print(i, l)
	# print(len(utterances))


	# ---- test single utterance ----
	n = -1
	sent = create_sentence(n, utterances[n])
	print(sent.get_sent_id(), sent.text())



	# ---- test file ----
	# for idx, utterance in enumerate(utterances):
	# 	sent = create_sentence(idx, utterance)
		# if sent.text() == ".": pass
		# else: print(sent.get_sent_id(), sent.text())


	# ---- test regex ----
