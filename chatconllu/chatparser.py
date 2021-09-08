"""
Utilities to parse files in CHILDES CHAT format.
"""
import sys, os
import re
import fileinput
from itertools import chain
from typing import List, Tuple, Dict, Union
from pathlib import Path

from collections import OrderedDict

from logger import logger
from helpers.sentence import Sentence
from helpers.token import Token


_TMP_DIR = 'tmp'
_OUT_DIR = 'out'

UTTERANCE = re.compile('^\\*')
PUNCT = re.compile("([,.;?!:”])")


def parse_chat(fp):
	utterances = []
	utterance = []
	metas = []
	meta = []
	tiers = []
	lines = fp.readlines()
	i = 0
	ltmp = ""
	while i < len(lines):
		if not lines[i].startswith("\t"):
			ltmp = lines[i].strip()
			i += 1
		while i < len(lines) and lines[i].startswith("\t"):
			ltmp += " " + lines[i].strip()
			i += 1
		print(i, ltmp)
		if ltmp.startswith("*"):
			metas.append(meta)
			if tiers:
				utterances[-1].extend(tiers)
			tiers = []
			utterance.append(ltmp)
			utterances.append(utterance)
			meta = []
			utterance = []
		if ltmp.startswith("@"):
			logger.debug(tiers)
			if tiers: utterances[-1].extend(tiers)
			tiers = []
			meta.append(ltmp)
		if ltmp.startswith("%"):
			tiers.append(ltmp)

	return metas, utterances

# def new_chat(filepath: 'pathlib.PosixPath'):
# 	""" Writes a new .cha file such that utterances and their dependent tiers
# 	 grouped together while different utterances are separated by an empty line.
# 	"""
# 	Path(_TMP_DIR).mkdir(parents=True, exist_ok=True)
# 	fn = filepath.stem
# 	with open(Path(_TMP_DIR, f'{fn}_new.cha'), 'w', encoding='utf-8') as f:
# 		for line in fileinput.input(filepath, inplace=False):
# 			match = UTTERANCE.match(line)
# 			print('\n'+ line.strip('\n').replace('    ', '\t') if match or line == '@End\n' else line.strip('\n').replace('    ', '\t'), file=f)


# def parse_chat(filepath: 'pathlib.PosixPath') -> Tuple[OrderedDict, List[List[str]]]:
# 	Reads the new .cha file created by new_chat(filepath) line by line, returns
# 	a tuple: (meta, utterances).

# 	The new .cha file has utterances and their dependent tiers grouped together while
# 	different utterances are separated by an empty line.

# 	Read file line by line, if line:
# 		- starts with @: is header/comment, store line number:line content to `meta` dict
# 		- elif line is not empty: line is part of one utterance, append to `lines` list [*note]
# 		- is empty
# 			- utterance is complete, append to `utterance` list
# 			- clear `lines` for next utterance
# 	*note:
# 		- field and value are separated by tabs
# 		- lines starting with tab character is a continuation of the last line

# 	Parameters:
# 	-----------
# 	filepath: the path to the original .cha file, which will be converted to the path to the
# 			  new .cha file inside this method.

# 	Return value: A tuple (meta, utterances).
# 				- `meta` is an ordered dictionary with line numbers as keys and headers/comments
# 				as values.
# 				- `utterances` is a list of utterances, each utterance is a
# 				list of strings corresponding to the lines of one utterance group.
# 				The first line is always the main utterance, the other lines are the
# 				dependent tiers.


# 	meta = {}
# 	utterances = []
# 	fn = filepath.stem

# 	with open(Path(_TMP_DIR, f'{fn}_new.cha'), 'r', encoding='utf-8') as f:

# 		lines = []
# 		file_lines = f.readlines()

# 		for i, l in enumerate(file_lines):
# 			l = l.strip('\n')
# 			if l.startswith('@'):
# 				j = i + 1
# 				while j < len(file_lines):
# 					if file_lines[j].startswith('\t'):
# 						meta[j] = file_lines[j].strip()  # keep the tab for putting back the chat file as is
# 						break
# 					else:
# 						break
# 				meta[i] = l  # needs to remember line number for positioning back the headers
# 				continue

# 			elif l:
# 				while l.startswith('\t'):  # tab marks continuation of last line
# 					if lines:
# 						lines[-1] += l.replace('\t', ' ')  # replace initial tab with a space
# 					break
# 				else:
# 					lines.append(l)
# 			elif lines:  # if empty line is met, store the utterance, clear the list
# 				utterances.append(lines)
# 				lines = []

# 		meta = OrderedDict(sorted(meta.items()))

# 	return meta, utterances


def normalise_utterance(line: str) -> Union[Tuple[List[str], List[str]], Tuple[None, None]]:
	"""Adopted and modified from coltekin/childes-tr/misc/parse-chat.py.
	Normalises a given utterance with CHILDES symbols to a clean form.
	"""

	until_rangleb = re.compile("([^>]+)>")
	until_rbracket = re.compile("([^]]+)]")
	until_eow = re.compile(r"[^,.;?!”<>\[\] ]+")  # added [] just in case something like this happens: "blah[: blahblah]""

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

	to_replace = re.compile(r"^\[::?( )?")

	retracing_no_angle_brackets = r"^\[/(?:[/?])?\]"  # [//] or [/?] or [/] --> [retrace]
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

	if line is None:
		return None, None

	if line == "0 .":
		return tokens, line

	i = 0
	while i < len(line):
		if line[i] == " ":
			i += 1
		elif line[i:].startswith("<"):
			tokens.extend(prev_tokens)
			i += 1
			if line[i:].startswith("<"):
				# logger.warn(f"This is a mistake in the corpus: two consecutive '<<' found. Skipping this utterance:\n{line}.")
				logger.warn(f"Actually this is a special case where we need to match the second next right angle bracket.")
				s = re.match(until_rangleb, line[i:])
				i += len(s.group(0))
				prev_tokens = s.group(1).strip().split()
				m = re.match(until_rangleb, line[i:])
				prev_tokens += m.group(1).strip().split()

			s = re.match(until_rangleb, line[i:])
			prev_tokens = s.group(1).strip().split()
			i += len(s.group(0))
		elif re.match(delete_prev, line[i:]):
			# logger.debug(f"previous to be deleted: {prev_tokens}")
			s = re.match(delete_prev, line[i:])
			i += len(s.group(0))
			prev_tokens = []  # forget previous tokens
		elif re.match(special_terminators, line[i:]):
			tokens.extend(prev_tokens)
			s = re.match(special_terminators, line[i:])
			i += len(s.group(0))
			prev_tokens = [s.group(0).strip()[-1]]
		elif re.match(to_omit, line[i:]):
			s = re.match(to_omit, line[i:])
			tokens.extend(prev_tokens)  # keep previous tokens
			i += len(s.group(0))
			prev_tokens = []
		elif re.match(overlap, line[i:]):
			s = re.match(overlap, line[i:])
			tokens.extend(prev_tokens)
			i += len(s.group(0))
			prev_tokens = []
		elif re.match(to_replace, line[i:]):
			s = re.match(to_replace, line[i:])
			i += len(s.group(0))
			m = re.match(until_rbracket, line[i:])
			tokens.extend(m.group(1).strip().split())
			i += len(m.group(0))
			prev_tokens = []
		elif re.match(strip_quotation, line[i:]):
			tokens.extend(prev_tokens)
			s = re.match(strip_quotation, line[i:])
			i += len(s.group(0))
			prev_tokens = s.group(0).strip()[1:-1].split()  # remove '+'
		elif re.match(trailing_off, line[i:]):  # above punctuation block, handles `...`
			tokens.extend(prev_tokens)
			s = re.match(trailing_off, line[i:])
			i += len(s.group(0))
			prev_tokens = [s.group(0).strip()[1:]]  # remove '+'
		elif re.match(PUNCT, line[i:]):  # punctuations, doesn't handle more than 1 place like '...'
			tokens.extend(prev_tokens)
			prev_tokens = [line[i]]
			i += 1
		else:  # normal tokens
			tokens.extend(prev_tokens)
			m = re.match(until_eow, line[i:])
			prev_tokens = [m.group(0)] if m else []
			i += len(m.group(0)) if m else 1
		for m, pt in enumerate(prev_tokens):  # loop over collected 'tokens' for patterns
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
				prev_tokens[ind] = new
				prev_tokens.pop(m)
				prev_tokens.pop(m-1)
			if re.match(to_omit, pt):
				prev_tokens.remove(pt)

	tokens.extend(prev_tokens)

	# logger.debug(f"----utterance----:\n{line}")
	# logger.debug(f"tokens: {tokens}")

	return tokens, line


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
		"post":"ADP",
		"prep":"ADP",
		"adv":"ADV",
		"adv:tem":"ADV",
		"v:aux":"AUX",
		"aux":"AUX",
		"coord":"CCONJ",
		"qn":"DET",
		"det":"DET",
		"quant":"DET",  # jpn
		"co":"INTJ",
		"n":"NOUN",
		"on":"NOUN",
		"onoma":"NOUN",  # jpn
		"part":"PART",
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

	if not mor_code:  # empty or None
		return mor_code

	if not mor_code in mor2upos:
		if not re.match(PUNCT, mor_code) and not mor_code.split(':')[0] in mor2upos:
			logger.warning(f"{mor_code} does not have a corresponding UPOS in mor2upos.")
		return mor2upos[mor_code.split(':')[0]] if mor_code.split(':')[0] in mor2upos else mor_code

	return mor2upos[mor_code] if mor_code in mor2upos else mor_code


def parse_gra(gra_segment: str) -> Tuple[str, str]:
	head = gra_segment.split('|')[1]
	deprel = gra_segment.split('|')[-1].lower()
	return head, deprel


def parse_sub(sub_segment: str)-> Tuple[Union[str, None], List[str], str, str]:
	feat_pattern = re.compile(r"\d?[A-Z]+(?![a-z])")
	lemma = None
	feat_str = []
	feat = ''
	lemma_feats, _, translation = sub_segment.partition('=')  # translation
	tmps = re.findall(r'[&|-]\w+', lemma_feats)
	if tmps:  # has feature
		feat_str = [f"FEAT={t[1:].title()}" for t in tmps]  # need to convert to UD feats
		feats = [f"{t}" for t in tmps]
		feat = '#'.join(feats)
	tmp = re.split('&|-', lemma_feats)
	# lemma = tmp[0]
	if tmp[0] == 'I' or not re.match(feat_pattern, tmp[0]):  # !!! sometimes lemma is encoded
		lemma = tmp[0]
	if not feat_str:
		feat_str = ''
	return lemma, feat_str, translation, feat


def parse_mor(mor_segment: str):
	"""Given a word-level MOR segment, extract the pos tag, lemma, features and other information
	   to be stored in the MISC field.
	"""
	lemma = None
	feat_str = []
	translation = None
	feat = None
	miscs = []
	# logger.info(f"Input MOR segment: {mor_segment}")
	pos, _, lemma_feats = mor_segment.partition("|")  # split by first |
	if pos == lemma_feats:
		miscs.append(f"form={mor_segment.replace('|', '@')}")
	if pos == '' or '+' in pos:  # punct
		lemma = lemma_feats.replace('+', '')  # special case of punctuations
		miscs.append(f"form={pos}")
	elif '+' in lemma_feats:  # compound
		tmps = re.split(r"\+\w+?\|", lemma_feats)
		# logger.debug(tmps)
		l, f, t, feat = zip(*(parse_sub(tmp) for tmp in tmps[1:]))    # tmp[0] is empty string
		lemma = ''.join(l)
		if any(t): translation = '+'.join(t)  # or leave empty
		feat_str = list(chain(*f))  # or leave empty
		if any(feat): miscs.append(f"feats={'+'.join(feat)}")  # or leave empty
		ctmps = re.split(r"\+", lemma_feats)
		# components = [f"{tuple(ctmp.split('|'))}" for ctmp in ctmps[1:]]
		components = [f"{ctmp.replace('|', '@')}" for ctmp in ctmps[1:]]
		comp = '#'.join(components)
		miscs.append(f"components={comp}")
		if translation: miscs.append(f"translation={translation}")
	else:
		lemma, feat_str, translation, feat = parse_sub(lemma_feats)
		if feat: miscs.append(f"feats={feat}")
		if translation: miscs.append(f"translation={translation}")
	misc = '|'.join(miscs)
	# logger.info(f"pos:{pos}\nlemma:{lemma}\nfeats:{feat_str}\nmisc:{misc}")
	return pos, lemma, feat_str, misc


def get_lemma_and_feats(mor_segment: str, is_multi=False) -> Union[List[Tuple], Tuple]:
	if is_multi:
		return [parse_mor(l) for l in re.split(r"~|\$", mor_segment)]  # ['pro:int|what', 'aux|be&3S']
	else:
		return parse_mor(mor_segment)


def extract_token_info(checked_tokens: List[Tuple[str, str]], gra: Union[List[str], None], mor: Union[List[str], None]) -> List[Token]:
	"""Extract information from mor and gra tiers when supplied, create Token objects with the information.

	Parameters:
	-----------
	checked_tokens: list of token tuples (surface, clean), returned by `check_token()`.
	gra: list of gra segments roughly corresponds to the list of tokens, since multi-word tokens
		 have separated gra segments.
	mor: list of mor segments with one-to-one correspondance with the list of tokens.

	Return value: a list of chatconllu.Token objects.

	----TO-DO----
	"""

	tokens = []
	idx = []

	if not checked_tokens:  # if provided empty list or None, return []
		return tokens

	surface, clean = zip(*checked_tokens)
	clean = list(filter(None, clean))  # remove empty strings

	if mor:
		idx = [x for x, g in enumerate(mor) if '~' in g or '$' in g]  # get multi-word tokens' indices in mor tier
		try:
			assert len(clean) == len(mor)  # one-to-one correspondance between tokens and mor segments
		except AssertionError:
			logger.warn(f"Something went wrong: clean and mor should have the same length!")
			logger.debug(f"utterance: {' '.join(clean)}\n")
			logger.debug(f"mor:\t{mor}\n")
			logger.debug(f"clean:\t{clean}\n")


	## ---- test prints ----
	# logger.debug(f"\n* utterance: {' '.join(clean)}\n")
	# logger.debug(mor)

	j = 0  # j keeps track of clean tokens
	tok_index = 1

	for c in clean:  # index, (surface, clean)
		# ---- initialise all Token attributes ----
		index = j + 1
		form = c  # don't remove `+` seen in compounds yet, should keep the dash for words like "qu'est-ce" in French
		lemma = None
		upos = None
		xpos = None
		feats = None
		head = None
		deprel = None
		deps = None
		misc = None
		multi = None
		type = None
		surface = None  # don't need this attribute, to be removed in Token
		translation=None
		# ---- simplified logic ----
		# if j in idx: multi-word tokens
		# if mor: lemma for compounds
		# if gra: head, deprel and deps
		# modify compound form, assign PUNCT to punctuations
		# add translation to MISC field
		# create Tokens
		if j in idx:  # multi-word tokens, implies has mor tier
			m = idx.index(j)  # the current token is the m th multi-word token in this utterance
			index = index + m
			num = len(re.split(r'~|\$', mor[j]))  # number of components in mwt
			multi = index + num - 1
			# logger.debug(f"j:{j}\tindex:{index}\tnum:{num}\tend:{multi}")
			if re.findall(r'~|\$', mor[j]):
				type = re.findall(r'~|\$', mor[j])
			# ---- get token info from mor ----
			xpos, lemma, feats, misc = zip(*get_lemma_and_feats(mor[j], is_multi=True))
			# if misc == ('', ''): misc = ''

			upos = [to_upos(x.replace('+', '')) for x in xpos]
			upos = [to_upos(x.split(':')[0]) for x in upos]
			if '+' in xpos:
				xpos = None
			tok_index = multi
			# logger.debug(misc)

			# ---- get token info from gra, if gra ----
			if gra:
				head = []
				deprel = []
				for x in range(index-1, multi):
					# print(parse_gra(gra[x]))
					h, d = parse_gra(gra[x])
					head.append(h)
					deprel.append(d)
				deps = [f"{h}:{deprel[x]}" for x, h in enumerate(head)]
				# logger.debug(f"tok_index:{tok_index}\tmulti:{multi}\tend:{multi}")
		else:
			if mor:
				xpos, lemma, feats, misc = get_lemma_and_feats(mor[j])
				index = tok_index
				upos = to_upos(xpos.replace('+', ''))
				upos = to_upos(upos.split(':')[0]) if ':' in upos else upos
				if '+' in xpos:
					xpos = None

			if gra:
				head, deprel = parse_gra(gra[tok_index-1])
				deps = f"{head}:{deprel}"
				index = int(gra[tok_index-1].split('|')[0])

		j+=1
		tok_index += 1

		# ---- assign PUNCT to punctuations ----
		if re.match(PUNCT, form):
			upos = "PUNCT"
			lemma = form
			xpos = 'punct'

		# ---- remove + in form ----
		form = form.replace('+', '')

		# ---- create Tokens ----
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
					type=type,
					surface=surface)
		if tok.index is not None:
			tokens.append(tok)
		# print(tok.feats)

	return tokens


def create_sentence(idx: int, lines: List[str]) -> Sentence:
	"""Given idx and lines, create a Sentence object.

	"""
	# ---- speaker ----
	speaker = lines[0][1:4]
	print(f"speaker: {speaker}")

	# ---- tiers ----
	tiers = [x.split('\t')[0] for x in lines[1:]]
	print(tiers)

	# ---- tokens ----
	tokens, utterance = normalise_utterance(lines[0].split('\t')[-1])  # normalise line (speaker removed)

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
	# print(tiers_dict.items())

	# ---- gra, mor ----
	gra, mor = None, None
	if 'mor' in tiers_dict.keys():
		mor = tiers_dict.get('mor')
	if 'gra' in tiers_dict:
		gra = tiers_dict.get('gra')

	# ---- clean form ----
	checked_tokens = [check_token(t) for t in tokens]
	toks = extract_token_info(checked_tokens, gra, mor)

	return Sentence(speaker=speaker,
					tiers=tiers_dict,
					gra=gra,
					mor=mor,
					chat_sent=utterance,
					clean=clean,
					comments=comments,
					sent_id=(idx+1),
					toks=toks
					)


def to_conllu(filename: 'pathlib.PosixPath', metas: List[List[str]], utterances:List[List[str]]):
	with open(filename, mode='w', encoding='utf-8') as f:
		# for k, v in meta.items():
		# 	f.write(f"# {k}\t{v}\n")  # write meta as headers
		# f.write("\n")
		for idx, utterance in enumerate(utterances):
			try:
				sent = create_sentence(idx, utterance)
			except IndexError as e:
				logger.exception(e)
				logger.info(f"writing sent {utterance} to {filename}...")
				raise
			if metas[idx]:  # if has comments/headers
				for m in metas[idx]:
					f.write(f"# {m}\n")
			f.write(f"# sent_id = {sent.get_sent_id()}\n")
			f.write(f"# text = {sent.text()}\n")
			f.write(f"# chat_sent = {sent.chat_sent}\n")
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


def chat2conllu(files: List['pathlib.PosixPath']):  #, remove=True):
	for f in files:
		# if f.with_suffix(".conllu").is_file():
		#   continue

		# ---- create a new .cha file ----
		# new_chat(f)

		# ---- parse chat ----
		logger.info(f"parsing {f}...")
		with open(f, 'r', encoding='utf-8') as fp:
			metas, utterances = parse_chat(fp)

			fn = f.with_suffix(".conllu")
			to_conllu(fn, metas, utterances)

		# if remove:
		# 	tmp_file = Path(_TMP_DIR, f"{f.stem}_new").with_suffix(".cha")
		# 	if tmp_file.is_file():
		# 		os.remove(tmp_file)


if __name__ == "__main__":
	# test = ['beg|beg', '+"/.', 'pro:sub|I', 'pro:sub|I~v|will']

	# pos, lemma, feat_str, misc = get_lemma_and_feats(test[0])

	# pos, lemma, feat_str, misc = zip(*get_lemma_and_feats(test[1], is_multi=True))

	# logger.info(pos)
	# logger.info(lemma)
	# logger.info(feat_str)
	# logger.info(misc)
	pass
