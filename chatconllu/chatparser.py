"""
Utilities to parse .cha files.
"""
import sys, os
import re
import fileinput
from pathlib import Path

from collections import OrderedDict

from logger import logger
from helpers.sentence import Sentence
from helpers.token import Token


_TMP_DIR = 'tmp'
_OUT_DIR = 'out'

utterance = re.compile('^\\*')

def list_files(directory, format="cha"):
	"""Recursively lists all files ending with .cha in the given directory.
	"""
	return [x for x in Path(directory).glob(f"**/*.{format}") if not x.name.startswith("._")]


def read_file(filepath):
	""" Writes a new .cha file for easier parsing.
	"""
	Path(_TMP_DIR).mkdir(parents=True, exist_ok=True)
	fn = filepath.stem
	with open(Path(_TMP_DIR, f'{fn}_new.cha'), 'w', encoding='utf-8') as f:
		for line in fileinput.input(filepath, inplace=False):  # need to change path
			match = utterance.match(line)
			print('\n'+ line.strip('\n').replace('    ', '\t') if match or line == '@End\n' else line.strip('\n').replace('    ', '\t'), file=f)


def parse_chat(filepath):
	""" Read file line by line, if line:
		- starts with @: is header
		- starts with *: is main line (utterance)
		- starts with %: one of n dependent tiers
		Note:
		- field and value are separated by tabs
		- lines starting with tab character is a continuation of the last line
	"""

	meta = {}
	utterances = []
	fn = filepath.stem

	with open(Path(_TMP_DIR, f'{fn}_new.cha'), 'r', encoding='utf-8') as f:

		lines = []
		file_lines = f.readlines()

		for i, l in enumerate(file_lines):
			l = l.strip('\n')
			if l.startswith('@'):
				j = i + 1
				while j < len(file_lines):
					if file_lines[j].startswith('\t'):
						meta[j] = file_lines[j].strip()  # replace initial tab with a space
						break
					else:
						break
				meta[i] = l  # needs to remember line number for positioning back the headers
				continue

			elif l:
				while l.startswith('\t'):  # tab marks continuation of last line
					if lines:
						lines[-1] += l.replace('\t', ' ')  # replace initial tab with a space
					break
				else:
					lines.append(l)
			elif lines:  # if empty line, store the utterance, clear the list
				utterances.append(lines)
				lines = []

		meta = OrderedDict(sorted(meta.items()))

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
	retracing = r"^(<.*?>){1}( )?\[/(?:[/?])?\]"  # <xx xx> [//] or [/?] or [/]
	repetitions = r"^\[x \d+\]"  # [x (number)]
	alternative_transcriptions = r'^\[=\? [()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\]'  # [=? some text include's]
	explanations = r'^\[= [ ()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\]'  # [= some text]
	best_guess = r"^\[\?\]"  # [?]
	error = r"^\[\^ e.*?]"  # [^ exxxx]
	error_star = r"^\[\*.*?\]"  # [* xxx]
	comment_on_main = r"^\[% .*?\]"  # [% xxx]
	complex_local_event = r"^\[\^.*?\]"  # [^ xxx] [^c]
	postcodes = r"^\[\+ .*?\]"  # [+ xxx]
	trailing_off = r"\+..."  # +...
	self_completion = r"^\+, "
	other_completion = r"^\+\+"
	stressing = r"^\[!!?\]"
	quoted_utterance = r"^\+\""
	quotation_follows = r"^\+\"/\."
	quick_uptake = r"^\+\^"
	paralinguistics_prosodics = r'^\[=! [()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\]'
	# sign_without_speech = "0"

	omission = [pause,
				 timed_pause,
				 retracing,
				 repetitions,
				 alternative_transcriptions,
				 explanations,
				 best_guess,
				 error,
				 error_star,
				 comment_on_main,
				 complex_local_event,
				 postcodes,
				 self_completion,
				 other_completion,
				 stressing,
				 quotation_follows,
				 quoted_utterance,
				 quick_uptake,
				 paralinguistics_prosodics,
				 ]

	best_guess_n = r"^<.*?> \[\?\]"  # best guess
	over = r"^<.*?> \[?[<>]?\]"
	expansion = [best_guess_n,
				 over,
				]

	# ---- compile regex patterns ----
	to_omit = re.compile('|'.join(o for o in omission))  # <whatever> [/?] or <whatever> [//]
	to_expand = re.compile('|'.join(e for e in expansion))

	to_replace = re.compile(r"^\[::?( )?")
	# to_replace_token = re.compile(r"^\[::? [()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\] \[/(?:[/?])?\]")

	retracing_no_angle_brackets = r"^\[/(?:[/?])?\]"  # [//] or [/?] or [/]
	# best_guess_followed_by_retrace = r"^\[\?\] \[/(?:[/?])?\]"
	# explanations_retrace = r"^\[= [()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\] \[/(?:[/?])?\]"
	x_retrace = r"^\[[=%?] [()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\] \[/(?:[/?])?\]"

	delete_previous = [retracing_no_angle_brackets,
						x_retrace,
						]
	delete_prev = re.compile('|'.join(d for d in delete_previous))

	overlap = re.compile(r"^\[?[<>]\]")

	special_terminators = re.compile(r'^\+(?:/(?:/\.|[.?])|"/\.)')

	strip_quotation = re.compile(r"^“.*( )??”")

	tokens = []
	prev_tokens = []
	positions = {}

	if line is None:
		return None, None

	if line == "0 .":
		return tokens, positions

	i = 0
	while i < len(line):
		if line[i] == " ":
			i += 1
		elif re.match(delete_prev, line[i:]):
			s = re.match(delete_prev, line[i:])
			i += len(s.group(0))
			prev_tokens = []
			# print(s.group(0))
		elif re.match(special_terminators, line[i:]):
			tokens.extend(prev_tokens)
			s = re.match(special_terminators, line[i:])
			i += len(s.group(0))
			prev_tokens = [s.group(0).strip()[-1]]
			# print(s.group(0))
		elif re.match(to_omit, line[i:]):
			s = re.match(to_omit, line[i:])
			tokens.extend(prev_tokens)
			i += len(s.group(0))
			prev_tokens = []
			# print(s.group(0))
		elif re.match(to_expand, line[i:]):  # expand contents in <>
			s = re.match(to_expand, line[i:])
			tokens.extend(prev_tokens)
			i += len(s.group(0))
			# print(s.group(0))
			prev_tokens = s.group(0)[1:-5].strip().split()  # remove '<' and '> [?]'
		elif re.match(overlap, line[i:]):
			s = re.match(overlap, line[i:])
			tokens.extend(prev_tokens)
			i += len(s.group(0))
			# print(s.group(0))
			prev_tokens = s.group(0)[1:-5].strip().split()
		elif re.match(to_replace, line[i:]):
			s = re.match(to_replace, line[i:])
			i += len(s.group(0))
			m = re.match(until_rbracket, line[i:])
			tokens.extend(m.group(1).strip().split())
			i += len(m.group(0))
			prev_tokens = []
			# print(s.group(0))
		elif re.match(strip_quotation, line[i:]):
			tokens.extend(prev_tokens)
			s = re.match(strip_quotation, line[i:])
			i += len(s.group(0))
			prev_tokens = s.group(0).strip()[1:-1].split()  # remove '+'
			# print(s.group(0))
		elif re.match(trailing_off, line[i:]):  # above punctuation block
			tokens.extend(prev_tokens)
			s = re.match(trailing_off, line[i:])
			i += len(s.group(0))
			prev_tokens = [s.group(0).strip()[1:]]  # remove '+'
			# print(s.group(0))
		elif re.match(punct_re, line[i:]):  # punctuations
			tokens.extend(prev_tokens)
			prev_tokens = [line[i]]
			i += 1
		else:  # normal tokens
			tokens.extend(prev_tokens)
			m = re.match(until_eow, line[i:])
			prev_tokens = [m.group(0)] if m else []
			i += len(m.group(0)) if m else 1
		for m, pt in enumerate(prev_tokens):
			# print(pt)
			if re.match(delete_prev, pt):
				prev_tokens.pop(m-1)
			if re.match(to_replace, pt):
				ind = m+1
				while ind < len(prev_tokens):
					if prev_tokens[ind].endswith(']'):
						new = ''.join(x for x in prev_tokens[m+1] if x.isalpha())
						break
					else:
						ind += 1
				# print(f"new:{new}")
				prev_tokens[ind] = new
				prev_tokens.pop(m)
				prev_tokens.pop(m-1)
			# print(prev_tokens)
			if re.match(to_omit, pt):
				prev_tokens.remove(pt)

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

	if surface is None:
		return None, None

	clean=''
	if re.match(to_omit, surface):   # phonological forms are omitted
		return surface, clean


	# define special symbols translation dict
	clean = surface.replace(' ', '')
	clean = clean.replace('(', '').replace(')', '')
	# clean = clean.replace('@q', '')  # @q is meta-lingustic use
	# clean = clean.replace('@o', '')  # @o is onomatopoeia
	clean = clean.replace('0', '')  # 0token is omitted token
	clean = clean.replace('‡', ',')  # prefixed interactional marker
	clean = clean.replace('„', ',')  # suffixed interactional marker
	clean = clean.replace('_', ' ')  # compound

	if "@" in clean:
		clean = clean[:clean.index("@")]  # drops any @endings

	return surface, clean


def to_upos(mor_code):
	# define a mapping between UPOS tags and MOR codes.
	mor2upos = {
		"adj":"ADJ",
		"adj:pred":"ADJ",
		"post":"ADP",
		"prep":"ADP",
		"adv":"ADV",
		"adv:tem":"ADV",
		"aux":"AUX",
		"coord":"CCONJ",
		"qn":"DET",
		"det:poss":"DET",
		"det:art":"DET",
		"det:dem":"DET",
		"det:int":"DET",
		"det:num":"DET",
		"co":"INTJ",
		"n":"NOUN",
		"n:let":"NOUN",
		"n:pt":"NOUN",
		"on":"NOUN",
		"part":"PART",
		"pro:dem":"PRON",
		"pro:exist":"PRON",
		"pro:indef":"PRON",
		"pro:int":"PRON",
		"pro:obj":"PRON",
		"pro:per":"PRON",
		"pro:poss":"PRON",
		"pro:refl":"PRON",
		"pro:rel":"PRON",
		"pro:sub":"PRON",
		"pro:per":"PRON",
		"pro":"PRON",
		"n:prop":"PROPN",
		"conj":"SCONJ",
		"comp":"SCONJ",
		"num":"NUM",
		"v":"VERB",
		"inf":"PART",
		"cop":"VERB",
		"mod":"VERB",
		"fil":"INTJ",  # ?
		"neg":"ADV"  # ?
	}

	return mor2upos[mor_code] if mor_code in mor2upos else mor_code


def extract_token_info(checked_tokens: list, gra: list, mor: list):

	punctuations = re.compile("([,.;?!:”])")

	all_tokens = []
	tokens = []

	if not checked_tokens:
		return all_tokens, tokens

	surface, clean = zip(*checked_tokens)
	clean = list(filter(None, clean))  # remove empty strings

	## ---- test prints ----
	# print(f"\n* utterance: {' '.join(clean)}\n")
	# print(mor)

	j = 0  # j keeps track of clean tokens
	gra_index = 0

	for i, (s, c) in enumerate(checked_tokens):
		index = j
		form = c.split('-')[0].replace('+', '')
		lemma = None
		upos = None
		xpos = None
		feats = None
		head = None
		deprel = None
		deps = None
		misc = None
		multi = None
		surface = s
		# print(index, form, surface)

		if form != surface:
			misc = f"{surface}"
		# print(mor)
		if form == "":
			index = None
		elif gra and mor:
			try:
				assert len(clean) == len(mor)
			except AssertionError:
				logger.debug(f"utterance: {' '.join(clean)}\n")
				logger.debug(f"mor:\t{mor}\n")
				logger.debug(f"clean:\t{clean}\n")
				break

			if len(gra) != len(mor):
				# ---- finds '~' in mor tier, take care of token indices ----
				idx = [x for x, g in enumerate(mor) if '~' in g]
				# print(idx)
				if j in idx:  # multi-word
					m = idx.index(j)
					index = int(gra[j+m].split('|')[0])
					num = len(mor[j].split('~'))-1  # length of parts - 1
					# print(mor[i].split('~'))
					end_index = index + num
					# logger.info(f"multi:{clean[j]}, i:{i}, j:{j}, num:{num}, index:{index}, end_index:{end_index}")

					# ---- create multi-word token ----
					lemma = [l.split('|')[-1].split('&')[0].split('-')[0].replace('+', '') for l in mor[j].split('~')]
					upos = [to_upos(l.split('|')[0].replace('+', '')) for l in mor[j].split('~')]
					upos = [to_upos(u.split(':')[0]) for u in upos]

					xpos = [l.split('|')[0].replace('+', '') for l in mor[j].split('~')]

					feats = [l.split('|')[-1].split('&')[1:] if l else 'None' for l in mor[j].split('~')]
					head = [gra[x].split('|')[1] for x in range(index, end_index+1)]
					deprel = [gra[x].split('|')[-1].lower() for x in range(index, end_index+1)]
					deps = [f"{h}:{deprel[x]}" for x, h in enumerate(head)]
					multi = end_index

					# ---- increment indices ----
					gra_index = index
					gra_index += 1

					# # ---- test print ----
					# print(f"index:\t{index}")
					# print(f"token:\t{form}")
					# print(f"lemma:\t{lemma}")
					# print(f"upos:\t{upos}")
					# print(f"xpos:\t{xpos}")
					# print(f"feats:\t{feats}")
					# print(f"head:\t{head}")
					# print(f"deprel:\t{deprel}")
					# print(f"deps:\t{deps}")
					# print(f"misc:\t{misc}")
					# print(f"multi:\t{multi}")
					# print()

				else:
					# ---- create token ----
					index = int(gra[gra_index].split('|')[0])
					lemma = mor[j].split('|')[-1].split('&')[0].split('-')[0].replace('+', '')
					upos = to_upos(mor[j].split('|')[0].replace('+', ''))
					upos = to_upos(upos.split(':')[0]) if ':' in upos else upos
					xpos = mor[j].split('|')[0]

					feats = mor[j].split('|')[-1].split('&')[1:]
					head = gra[gra_index].split('|')[1]
					deprel = gra[gra_index].split('|')[-1].lower()
					deps = f"{head}:{deprel}"

					# ---- increment indices ----
					gra_index += 1

			else:
				index = gra[j].split('|')[0]
				lemma = mor[j].split('|')[-1].split('&')[0].split('-')[0].replace('+', '')
				# use a mapping for upos and xpos, naively store the values for now
				upos = to_upos(mor[j].split('|')[0].replace('+', ''))
				upos = to_upos(upos.split(':')[0]) if ':' in upos else upos
				xpos = mor[j].split('|')[0].replace('+', '')

				feats = mor[j].split('|')[-1].split('&')[1:]
				head = gra[j].split('|')[1]
				deprel = gra[j].split('|')[-1].lower()
				deps = f"{head}:{deprel}"

			j += 1

		elif mor:
			# print(mor)
			# print(index, form, surface)
			index = j + 1
			lemma = mor[j].split('|')[-1].split('&')[0].split('-')[0].replace('+', '')
			# use a mapping for upos and xpos, naively store the values for now
			upos = to_upos(mor[j].split('|')[0].replace('+', ''))
			upos = to_upos(upos.split(':')[0]) if ':' in upos else upos
			xpos = mor[j].split('|')[0].replace('+', '')

			feats = mor[j].split('|')[-1].split('&')[1:]

			j += 1

			# # ---- test print ----
			# print(f"index:\t{index}")
			# (f"token:\t{form}")
			# print(f"lemma:\t{lemma}")
			# print(f"upos:\t{upos}")
			# print(f"xpos:\t{xpos}")
			# print(f"feats:\t{feats}")
			# print(f"head:\t{head}")
			# print(f"deprel:\t{deprel}")
			# print(f"deps:\t{deps}")
			# print(f"misc:\t{misc}")
			# print(f"multi:\t{multi}")
			# print()

		elif gra:
			assert len(gra) == len(clean)
			index = gra[j].split('|')[0]
			head = gra[j].split('|')[1]
			deprel = gra[j].split('|')[-1].lower()
			deps = f"{head}:{deprel}"

			j += 1

		elif not gra and not mor:
			index = j + 1
			j += 1

		if re.match(punctuations, form):
			upos = "PUNCT"

		# print(f"new: {index} {form} {surface}")

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
					multi=multi,
					surface=surface)
		if tok.index is not None:
			tokens.append(tok)
		all_tokens.append(tok)

	return all_tokens, tokens


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
	tokens, positions = normalise_utterance(lines[0].split('\t')[-1])  # normalise line (speaker removed)

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
		#   comments.append(t)
	# print(comments)
	# print(tiers_dict.keys())
	# print(tiers_dict.items())

	# ---- gra, mor ----
	gra, mor = None, None
	if ('mor' or 'xmor') in tiers_dict:
		mor = tiers_dict.get('mor') if 'mor' in tiers_dict else tiers_dict.get('xmor')
	if 'gra' in tiers_dict:
		gra = tiers_dict.get('gra')

	# ---- clean form ----
	checked_tokens = [check_token(t) for t in tokens]
	tokens, toks = extract_token_info(checked_tokens, gra, mor)


	return Sentence(speaker=speaker,
					tiers=tiers_dict,
					gra=gra,
					mor=mor,
					tokens=tokens,
					clean=clean,
					comments=comments,
					sent_id=(idx+1),
					toks=toks
					), positions


def to_conllu(filename, meta, utterances):
	with open(filename, mode='w', encoding='utf-8') as f:
		# write meta as headers
		for k, v in meta.items():
			f.write(f"# {k}\t{v}\n")
		f.write("\n")
		# write each sentence
		for idx, utterance in enumerate(utterances):
			try:
				sent, _ = create_sentence(idx, utterance)
			except IndexError:
				logger.info(f"writing sent {sent.get_sent_id()} to {filename}...")
				quit()
			# if not sent.toks:
			#   continue
			# if sent.text() == '.':
				# continue
			# logger.info(f"writing sent {sent.get_sent_id()} to {filename}...")
			f.write(f"# sent_id = {sent.get_sent_id()}\n")
			f.write(f"# text = {sent.text()}\n")
			f.write(f"# speaker = {sent.speaker}\n")
			for t in sent.tiers.keys():
				f.write(f"# {t} = {sent.tiers.get(t)}\n")
			if not sent.toks:
				f.write(sent.conllu_str(mute=True))
			if sent.text() == '.':
				f.write(sent.conllu_str(mute=True))
			else:
				f.write(sent.conllu_str())
			f.write("\n")


def chat2conllu(files, remove=True):
	for f in files:
		# if f.with_suffix(".conllu").is_file():
		#   continue
		# ---- create a new .cha file ----
		# logger.info(f"reading {f} and generating a new .cha file...")
		read_file(f)

		# ---- parse chat ----
		logger.info(f"parsing {f}...")
		meta, utterances = parse_chat(f)

		# ---- test print meta ----
		# print(len(meta))
		# for i, x in enumerate(meta.items()):
		#   print(i, x)
		# # ---- test print utterances----
		# print(len(utterances))
		# for i, l in enumerate(utterances[1019]):
		#   print(i, l)
		# # ---- test single utterance ----
		# n = 1019
		# sent, _ = create_sentence(n, utterances[n])
		# print(sent.get_sent_id(), sent.text())

		fn = f.with_suffix(".conllu")
		to_conllu(fn, meta, utterances)

		if remove:
			tmp_file = Path(_TMP_DIR, f"{f.stem}_new").with_suffix(".cha")
			if tmp_file.is_file():
				os.remove(tmp_file)

		# quit()




def conllu2chat(files):
	pass


if __name__ == "__main__":
	pass
	# TEST = "/home/jingwen/Desktop/thesis/Chang2"
	# TEST = "tests"
	# logger.info(f"listing all files in {TEST}...")
	# files = list_files(TEST)
	# chat2conllu(files)
	# path = Path("/home/jingwen/Desktop/thesis/Brown/Sarah/020322.cha")
	# chat2conllu([path], remove=False)


