"""
Utilities to parse files in CHILDES CHAT format.
"""
import sys, os
import re
import fileinput
from typing import List, Tuple, Dict, Union
from pathlib import Path

from collections import OrderedDict

from logger import logger
from helpers.sentence import Sentence
from helpers.token import Token


_TMP_DIR = 'tmp'
_OUT_DIR = 'out'

UTTERANCE = re.compile('^\\*')


def new_chat(filepath: 'pathlib.PosixPath'):
	""" Writes a new .cha file such that utterances and their dependent tiers grouped together while
	different utterances are separated by an empty line.
	"""
	Path(_TMP_DIR).mkdir(parents=True, exist_ok=True)
	fn = filepath.stem
	with open(Path(_TMP_DIR, f'{fn}_new.cha'), 'w', encoding='utf-8') as f:
		for line in fileinput.input(filepath, inplace=False):
			match = UTTERANCE.match(line)
			print('\n'+ line.strip('\n').replace('    ', '\t') if match or line == '@End\n' else line.strip('\n').replace('    ', '\t'), file=f)


def parse_chat(filepath: 'pathlib.PosixPath') -> Tuple[OrderedDict, List[List[str]]]:
	"""Reads the new .cha file created by new_chat(filepath) line by line, returns
	a tuple: (meta, utterances).

	The new .cha file has utterances and their dependent tiers grouped together while
	different utterances are separated by an empty line.

	Read file line by line, if line:
		- starts with @: is header/comment, store line number:line content to `meta` dict
		- elif line is not empty: line is part of one utterance, append to `lines` list [*note]
		- is empty
			- utterance is complete, append to `utterance` list
			- clear `lines` for next utterance
	*note:
		- field and value are separated by tabs
		- lines starting with tab character is a continuation of the last line

	Parameters:
	-----------
	filepath: the path to the original .cha file, which will be converted to the path to the
			  new .cha file inside this method.

	Return value: A tuple (meta, utterances).
				- `meta` is an ordered dictionary with line numbers as keys and headers/comments
				as values.
				- `utterances` is a list of utterances, each utterance is a
				list of strings corresponding to the lines of one utterance group. The first line is always the
				main utterance, the other lines are the dependent tiers.
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
						meta[j] = file_lines[j].strip()  # keep the tab for putting back the chat file as is
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
			elif lines:  # if empty line is met, store the utterance, clear the list
				utterances.append(lines)
				lines = []

		meta = OrderedDict(sorted(meta.items()))

	return meta, utterances


def normalise_utterance(line: str) -> Union[Tuple[List[str], List[str]], Tuple[None, None]]:
	"""Adopted and modified from coltekin/childes-tr/misc/parse-chat.py.
	Normalises a given utterance with CHILDES symbols to a clean form.
	"""

	until_rangleb = re.compile("([^>]+)>")
	until_rbracket = re.compile("([^]]+)]")
	until_eow = re.compile(r"[^,.;?!”<> ]+")
	punct_re = re.compile("([,.;?!:”])")

	# ---- define patterns to omit ----
	pause = r"^\(\.+\)"  # (.), (..), (...)
	timed_pause = r"^\((\d+?:)?(\d+?)?\.(\d+?)?\)"  # ((min:)(sec).(decimals))
	repetitions = r"^\[x \d+\]"  # [x (number)]
	alternative_transcriptions = r'^\[=\? [()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\]'  # [=? some text include's]
	explanations = r'^\[= [ ()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\]'  # [= some text]
	best_guess = r"^\[\?\]"  # [?]
	error = r"^\[\^ e.*?]"  # [^ exxxx]
	error_star = r"^\[\*.*?\]"  # [* xxx]
	comment_on_main = r"^\[% .*?\]"  # [% xxx]
	complex_local_event = r"^\[\^.*?\]"  # [^ xxx] [^c]
	postcodes = r"^\[\+ .*?\]"  # [+ xxx]
	self_completion = r"^\+, "
	other_completion = r"^\+\+"
	stressing = r"^\[!!?\]"
	quoted_utterance = r"^\+\""
	quotation_follows = r"^\+\"/\."
	quick_uptake = r"^\+\^"
	paralinguistics_prosodics = r'^\[=! [()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\]'
	lazy_overlap = r"^\+<"

	omission = [
				pause,
				timed_pause,
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
				lazy_overlap,
				]



	# ---- compile regex patterns ----
	to_omit = re.compile('|'.join(o for o in omission))  # <whatever> [/?] or <whatever> [//]
	# to_expand = re.compile('|'.join(e for e in expansion))

	to_replace = re.compile(r"^\[::?( )?")
	# to_replace_token = re.compile(r"^\[::? [()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\] \[/(?:[/?])?\]")

	retracing_no_angle_brackets = r"^\[/(?:[/?])?\]"  # [//] or [/?] or [/] --> [retrace]
	# best_guess_followed_by_retrace = r"^\[\?\] \[/(?:[/?])?\]"  # [?] [retrace]
	# explanations_retrace = r"^\[= [()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\] \[/(?:[/?])?\]"  # [= blah blah's] [retrace]
	x_retrace = r"^\[[=%?] [()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\] \[/(?:[/?])?\]"

	delete_previous = [
						retracing_no_angle_brackets,
						x_retrace,
					  ]
	delete_prev = re.compile('|'.join(d for d in delete_previous))

	special_terminators = re.compile(r'^\+(?:/(?:/\.|[.?])|"/\.)')

	trailing_off = re.compile(r"\+...")  # +...

	overlap = re.compile(r"^\[?[<>]\]")

	strip_quotation = re.compile(r"^“.*( )??”")

	tokens = []
	prev_tokens = []
	all_scopes = []
	positions = {}

	if line is None:
		return None, None

	if line == "0 .":
		return tokens, positions

	# logger.debug(f"----utterance----:\n{line}")

	i = 0
	while i < len(line):
		full_scope = ''
		if line[i] == " ":
			i += 1
		elif line[i:].startswith("<"):
			tokens.extend(prev_tokens)
			i += 1
			if line[i:].startswith("<"):
				logger.warn(f"This is a mistake in the corpus: two consecutive '<<' found. Skipping this utterance:\n{line}.")
				# quit()
				return tokens, positions
			s = re.match(until_rangleb, line[i:])
			prev_tokens = s.group(1).strip().split()
			# logger.debug(f"prev_tokens_new: {prev_tokens}")
			i += len(s.group(0))
			# logger.debug(f"s.group(0): {s.group(0)}")
			full_scope = "<" + s.group(0)
			all_scopes.append(full_scope)
			# logger.debug(f"{full_scope}")
		elif re.match(delete_prev, line[i:]):
			# logger.debug(f"previous to be deleted: {prev_tokens}")
			s = re.match(delete_prev, line[i:])
			i += len(s.group(0))
			prev_tokens = []  # forget previous tokens
			# logger.debug(f"delete previous: {s.group(0)}")
			full_scope = s.group(0)
			all_scopes.append(full_scope)
			# logger.debug(f"{full_scope}")
		elif re.match(special_terminators, line[i:]):
			tokens.extend(prev_tokens)
			s = re.match(special_terminators, line[i:])
			i += len(s.group(0))
			prev_tokens = [s.group(0).strip()[-1]]
			# logger.debug(f"special_terminators: {s.group(0)} to {prev_tokens}")
			full_scope = s.group(0)
			all_scopes.append(full_scope)
			# logger.debug(f"{full_scope}")
		elif re.match(to_omit, line[i:]):
			s = re.match(to_omit, line[i:])
			tokens.extend(prev_tokens)  # keep previous tokens
			i += len(s.group(0))
			prev_tokens = []
			# logger.debug(f"keep previous tokens and omit: {s.group(0)}")
			full_scope = s.group(0)
			all_scopes.append(full_scope)
			# logger.debug(f"{full_scope}")
		elif re.match(overlap, line[i:]):
			s = re.match(overlap, line[i:])
			tokens.extend(prev_tokens)
			i += len(s.group(0))
			# logger.debug(f"overlap pattern: {s.group(0)}")
			prev_tokens = []
			full_scope = s.group(0)
			all_scopes.append(full_scope)
			# logger.debug(f"{full_scope}")
		elif re.match(to_replace, line[i:]):
			s = re.match(to_replace, line[i:])
			i += len(s.group(0))
			m = re.match(until_rbracket, line[i:])
			tokens.extend(m.group(1).strip().split())
			i += len(m.group(0))
			prev_tokens = []
			# logger.debug(f"to replace pattern: {s.group(0)}")
			# logger.debug(f"\tto replace: {m.group(1).strip().split()}")
			full_scope = s.group(0) + m.group(0)
			all_scopes.append(full_scope)
			# logger.debug(f"{full_scope}")
		elif re.match(strip_quotation, line[i:]):
			tokens.extend(prev_tokens)
			s = re.match(strip_quotation, line[i:])
			i += len(s.group(0))
			prev_tokens = s.group(0).strip()[1:-1].split()  # remove '+'
			# logger.debug(f"strip quotation: {s.group(0)} to {prev_tokens}")
			full_scope = s.group(0)
			all_scopes.append(full_scope)
			# logger.debug(f"{full_scope}")
		elif re.match(trailing_off, line[i:]):  # above punctuation block, handles `...`
			tokens.extend(prev_tokens)
			s = re.match(trailing_off, line[i:])
			i += len(s.group(0))
			prev_tokens = [s.group(0).strip()[1:]]  # remove '+'
			# logger.debug(f"trailing off pattern: {s.group(0)} to {prev_tokens}")
			full_scope = s.group(0)
			all_scopes.append(full_scope)
			# logger.debug(f"{full_scope}")
		elif re.match(punct_re, line[i:]):  # punctuations, doesn't handle more than 1 place like '...'
			tokens.extend(prev_tokens)
			prev_tokens = [line[i]]
			full_scope = line[i]
			i += 1
			all_scopes.append(full_scope)
			# logger.debug(f"single punctuation pattern: {prev_tokens}")
			# logger.debug(f"{full_scope}")
		else:  # normal tokens
			tokens.extend(prev_tokens)
			m = re.match(until_eow, line[i:])
			prev_tokens = [m.group(0)] if m else []
			i += len(m.group(0)) if m else 1
			# logger.debug(f"normal token: {prev_tokens}")
			full_scope = prev_tokens[0] if prev_tokens else ""
			all_scopes.append(full_scope)
			# logger.debug(f"{full_scope}")
		for m, pt in enumerate(prev_tokens):  # loop over collected 'tokens' for patterns
			# print(pt)
			if re.match(delete_prev, pt):
				logger.debug(f"inner delete previous before: {prev_tokens}")
				prev_tokens.pop(m-1)
				logger.debug(f"inner delete previous after pop: {prev_tokens}")
			if re.match(to_replace, pt):
				ind = m+1
				while ind < len(prev_tokens):
					if prev_tokens[ind].endswith(']'):
						new = ''.join(x for x in prev_tokens[m+1] if x.isalpha())
						break
					else:
						ind += 1
				# print(f"new:{new}")
				logger.debug(f"inner replace: to {new}")
				logger.debug(f"inner replace before: {prev_tokens}")
				prev_tokens[ind] = new
				logger.debug(f"inner replace after adding {new} at index {ind}: {prev_tokens}")
				prev_tokens.pop(m)
				logger.debug(f"inner replace after pop index {m}: {prev_tokens}")
				prev_tokens.pop(m-1)
				logger.debug(f"inner replace after pop index {m-1}: {prev_tokens}")
			# print(prev_tokens)
			if re.match(to_omit, pt):
				logger.debug(f"inner omit before remove: {prev_tokens}")
				prev_tokens.remove(pt)
				logger.debug(f"inner omit after remove: {prev_tokens}")
	tokens.extend(prev_tokens)
	positions = {i:v for i, v in enumerate(all_scopes)}

	logger.debug(f"----utterance----:\n{line}")
	# logger.debug(f"all_scopes: {all_scopes}")
	logger.debug(f"tokens: {tokens}")
	# logger.debug(f"{positions}")
	# logger.debug(f"{' '. join(positions.values())}")

	# if len(all_scopes) != len(tokens):
	#   logger.debug(f"----utterance----:\n{line}")
	#   # logger.debug(f"all_scopes: {all_scopes}")
	#   logger.debug(f"tokens: {tokens}")
	#   logger.debug(f"{' '. join(positions.values())}")

	return tokens, all_scopes


def check_token(surface: str) -> Union[Tuple[str, str], Tuple[None, None]]:
	"""Adopted and modified from coltekin/childes-tr/misc/parse-chat.py
	For a given surface form of the token, return (surface, clean), where
	clean is the token form without CHILDES codes.
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


def to_upos(mor_code: str) -> str:
	"""If given mor_code is in predefined mor2upos dict, return the
	corresponding upos, otherwise return the mor_code.
	"""
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


def parse_feats(mor_segment: str) -> List[str]:
	feat_str = []
	ff = mor_segment.split('|')[-1].split('&')[1:]  # e.g. ['PAST', '13S']
	if ff:  # rule out []
		for f in ff:
			feat_str.append("FEAT=" + f.title())  # TO-DO: helper method to define which `FEAT` to use e.g. PERSON, TENSE
	return feat_str


def get_feats(mor_segment: str, is_multi=False) -> Union[List[List[str]], List[str]]:
	if is_multi:
		return [parse_feats(l) for l in mor_segment.split('~')]  # ['pro:int|what', 'aux|be&3S']
	else:
		return parse_feats(mor_segment)


def extract_token_info(checked_tokens: List[Tuple[str, str]], gra: Union[List[str], None], mor: Union[List[str], None]) -> List[Token]:
	"""Extract information from mor and gra tiers when supplied, create Token objects with the information.

	Parameters:
	-----------
	checked_tokens:	list of token tuples (surface, clean), returned by `check_token()`.
	gra: list of gra segments roughly corresponds to the list of tokens, since multi-word tokens
		 have separated gra segments.
	mor: list of mor segments with one-to-one correspondance with the list of tokens.

	Return value: a list of chatconllu.Token objects.


	----TO-DO----
	* rethink lemma for compound words
		- e.g. mor: "n|+n|washing+n|machine", "washing+machine", currently form is "washingmachine", lemma is "machine"
	* rethink preserving information after dash symbol, right now such info is lost
	* reduce duplicate code to helper methods
	*
	"""

	punctuations = re.compile("([,.;?!:”])")

	tokens = []

	if not checked_tokens:  # if provided empty list or None, return []
		return tokens

	surface, clean = zip(*checked_tokens)
	clean = list(filter(None, clean))  # remove empty strings

	## ---- test prints ----
	# logger.debug(f"\n* utterance: {' '.join(clean)}\n")
	# logger.debug(mor)

	j = 0  # j keeps track of clean tokens
	gra_index = 0

	for i, (s, c) in enumerate(checked_tokens):  # index, (surface, clean)
		index = j
		form = c.split('-')[0].replace('+', '')  # currently discard anything after dash, remove `+` seen in compounds
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
		# logger.debug(index, form, surface)

		if form != surface:  # surface form and clean disagree, store surface form in MISC field
			misc = f"surface={surface}"
		# logger.debug(mor)
		if form == "":  # Why did I check this?
			index = None
		elif gra and mor:  # --> is able to determine if there are multi-word tokens
			try:
				assert len(clean) == len(mor)  # one-to-one correspondance between tokens and mor segments
			except AssertionError:
				logger.warn(f"Something went wrong: clean and mor should have the same length!")
				logger.debug(f"utterance: {' '.join(clean)}\n")
				logger.debug(f"mor:\t{mor}\n")
				logger.debug(f"clean:\t{clean}\n")
				break

			if len(gra) != len(mor):  # there are multi-word tokens in this utterance (represented by a list of tokens)
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
					feats = get_feats(mor[j], is_multi=True)
					logger.debug(feats)

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
					lemma = mor[j].split('|')[-1].split('&')[0].split('-')[0]
					if '+' in lemma:
						if not misc:
							misc = ""
							misc += "form=" + lemma
						lemma = lemma.replace('+', '').replace('/', '')
					index = int(gra[gra_index].split('|')[0])
					upos = to_upos(mor[j].split('|')[0].replace('+', ''))
					upos = to_upos(upos.split(':')[0]) if ':' in upos else upos
					xpos = mor[j].split('|')[0]
					if '+' in xpos:
						xpos = None

					feats = get_feats(mor[j])
					logger.debug(feats)

					head = gra[gra_index].split('|')[1]
					deprel = gra[gra_index].split('|')[-1].lower()
					deps = f"{head}:{deprel}"

					# ---- increment indices ----
					gra_index += 1

			else:
				lemma = mor[j].split('|')[-1].split('&')[0].split('-')[0]
				if '+' in lemma:
					if not misc:
						misc = ""
						misc += "form=" + lemma
					lemma = lemma.replace('+', '').replace('/', '')
				index = gra[j].split('|')[0]
				# use a mapping for upos and xpos, naively store the values for now
				upos = to_upos(mor[j].split('|')[0].replace('+', ''))
				upos = to_upos(upos.split(':')[0]) if ':' in upos else upos
				xpos = mor[j].split('|')[0]
				if '+' in xpos:
					xpos = None

				feats = get_feats(mor[j])
				logger.debug(feats)
				head = gra[j].split('|')[1]
				deprel = gra[j].split('|')[-1].lower()
				deps = f"{head}:{deprel}"

			j += 1

		elif mor:
			# print(mor)
			# print(index, form, surface)
			index = j + 1
			lemma = mor[j].split('|')[-1].split('&')[0].split('-')[0]
			if '+' in lemma:
				if not misc:
					misc = ""
					misc += "form=" + lemma
			lemma = lemma.replace('+', '').replace('/', '')
			# use a mapping for upos and xpos, naively store the values for now
			upos = to_upos(mor[j].split('|')[0].replace('+', ''))
			upos = to_upos(upos.split(':')[0]) if ':' in upos else upos
			xpos = mor[j].split('|')[0]
			if '+' in xpos:
				xpos = None
			feats = get_feats(mor[j])
			logger.debug(feats)

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

	return tokens


def create_sentence(idx: int, lines: List[str]) -> Sentence:
	"""Given idx and lines, create a Sentence object.

	"""
	# ---- speaker ----
	speaker = lines[0][1:4]
	# print(f"speaker: {speaker}")

	# ---- tiers ----
	tiers = [x.split('\t')[0] for x in lines[1:]]
	# print(tiers)

	# ---- tokens ----
	tokens, all_scopes = normalise_utterance(lines[0].split('\t')[-1])  # normalise line (speaker removed)

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
	toks = extract_token_info(checked_tokens, gra, mor)
	# if toks[-1].misc is None:
	#   toks[-1].misc = ""
	# toks[-1].misc += "|utt=" + " ".join(all_scopes)  # utterance is stored in misc of punctuation for now

	return Sentence(speaker=speaker,
					tiers=tiers_dict,
					gra=gra,
					mor=mor,
					tokens=all_scopes,
					clean=clean,
					comments=comments,
					sent_id=(idx+1),
					toks=toks
					)


def to_conllu(filename: 'pathlib.PosixPath', meta: OrderedDict, utterances:List[List[str]]):
	with open(filename, mode='w', encoding='utf-8') as f:
		for k, v in meta.items():
			f.write(f"# {k}\t{v}\n")  # write meta as headers
		f.write("\n")
		for idx, utterance in enumerate(utterances):
			try:
				sent = create_sentence(idx, utterance)
			except IndexError:
				logger.info(f"writing sent {sent.get_sent_id()} to {filename}...")
				quit()
			# logger.info(f"writing sent {sent.get_sent_id()} to {filename}...")
			f.write(f"# sent_id = {sent.get_sent_id()}\n")
			f.write(f"# text = {sent.text()}\n")
			f.write(f"# chat_sent = {' '.join(sent.tokens)}\n")
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


def chat2conllu(files: List['pathlib.PosixPath'], remove=True):
	for f in files:
		# if f.with_suffix(".conllu").is_file():
		#   continue
		# ---- create a new .cha file ----
		new_chat(f)

		# ---- parse chat ----
		logger.info(f"parsing {f}...")
		meta, utterances = parse_chat(f)

		fn = f.with_suffix(".conllu")
		to_conllu(fn, meta, utterances)

		if remove:
			tmp_file = Path(_TMP_DIR, f"{f.stem}_new").with_suffix(".cha")
			if tmp_file.is_file():
				os.remove(tmp_file)

		# quit()


if __name__ == "__main__":
	pass



