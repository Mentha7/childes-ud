"""
Utilities to parse files in CHILDES CHAT format.
"""
import sys, os
import re
import ast
import fileinput
from itertools import chain
from typing import List, Tuple, Dict, Union
from pathlib import Path

from collections import OrderedDict

from logger import logger
from helpers.sentence import Sentence
from helpers.token import Token
from helpers.clean_utterance import normalise_utterance


PUNCT = re.compile("([,.;?!:”])")
FEAT = re.compile(r"^\d?[A-Z]+$")

# ---- define unidentifiable patterns to omit----
unidentifiable = [
	r"yyy",  # phono_coding
	r"www",  # untranscribed
	r"^&",  # phono_fragments
	]
TO_OMIT = re.compile("|".join(unidentifiable))

# define a mapping between MOR codes and UPOS tags.
MOR2UPOS = {
		"adj":"ADJ",
		"post":"ADP",  # adpositions
		"prep":"ADP",  # adpositions
		"adv":"ADV",
		"adv:tem":"ADV",
		"v:aux":"AUX",
		"aux":"AUX",
		"coord":"CCONJ",
		"qn":"DET",
		"det":"DET",
		"quant":"DET",  # jpn
		"co":"INTJ",  # interjection, interaction
		"n":"NOUN",
		"on":"NOUN",  # onomatopoeia
		"onoma":"NOUN",  # jpn onomatopoeia
		"part":"PART",
		"pro":"PRON",
		"n:prop":"PROPN",
		"conj":"SCONJ",
		"comp":"SCONJ",
		"num":"NUM",
		"v":"VERB",
		"inf":"PART",  # infinitive particles
		"cop":"VERB",
		"mod":"VERB",
		"art":"DET",  # article, PronType=Art
		"prepart":"DET",  # preposition with article
		"vimp":"VERB",  # verb imperative Mood=Imp
		"vpfx":"ADP",  # preverb/verbal particles, according to UD website shouldn't be PART
		# ---- punctuation marks ----
		"end":"PUNCT",
		"beg":"PUNCT",
		"cm":"PUNCT",
		"bq":"PUNCT",
		"eq":"PUNCT",
		"bq2":"PUNCT",
		"eq2":"PUNCT",
		# ---- hard to decide ----
		"fil":"INTJ",  # ?
		"neg":"ADV",  # ?
		"wplay":"INTJ",  # wordplay
		"bab":"INTJ",  # babbling
		"sing":"INTJ",  # singing
		# ---- empty or X? ----
		"none":"X",
		"dia":"X",  # dialect
		"test":"X",  # test words like "wug"
		"meta":"X",  # metalinguistic use
		"phon":"X",  # phonologically consistent form
		"fam":"X",  # family-specific form
		"uni":"X",  # Unibet transcription
		"L2":"X",  # second-language form
		"neo":"X",  # neologism
		"chi":"X",  # child-invented form
	}

# define a mapping between GRs and UD deprels.
GR2DEPREL = {
		'mod':'nmod',
		'coord':'cc',
		'subj':'nsubj',
		'com':'discourse',
		'pq':'det',
		'neg':'advmod',
		'cjct':'advcl',
		'cpred':'ccomp',
		'obj2':'iobj',
		'incroot':'root',
		'xmod':'acl',
		# 'beg':'vocative',  # or parataxis, change head from 0 to root's index
		'date':'flat',
		'comp':'ccomp',
		'xjct':'advcl',
		'pred':'xcomp',
		'name':'flat:name',
		'srl':'xcomp',
		'jct':'advmod',
		'link':'mark',
		'app':'appos',
		'cmod':'ccomp',
		# 'end':'parataxis',
		'enum':'conj',
		# ---- has alternative ----
		'poss':'case',  # or "nmod:poss"
		'quant':'det',  # if numbers 'nummod'
		'postmod':'amod',  # or "xcomp"
		# ---- as is ----
		'obj':'obj',
		'csubj':'csubj',
		'conj':'conj',
		'punct':'punct',
		'det':'det',
		'root':'root',
		'aux':'aux',
		# ---- punctuations ----
		'endp':'punct',
		'begp':'punct',
		'lp':'punct',
		# ---- undecided ----
		'om':'discourse:omission',
		'cpobj':'obj',
		'cobj':'obj',
		'njct':'obj',
		'pobj':'obj',
		'inf':'obj',
	}


def parse_chat(fp):
	""" For a open file in CHAT format, get the utterances grouped with
	their dependent tiers, meta data including headers and comments, and
	the final lines of the file.
	"""

	meta, metas = [], []
	tiers, utterances = [], []
	final = []

	lines = fp.readlines()
	i = 0
	ltmp = ""

	while i < len(lines):
		# ---- obtain full lines by appending tab-initiated continuations to previous lines ----
		if not lines[i].startswith("\t"):
			ltmp = lines[i].strip()
			i += 1
		while i < len(lines) and lines[i].startswith("\t"):
			ltmp += " " + lines[i].strip()
			i += 1
		# ---- decide type of ltmp ----
		#  if ltmp starts with:
		#    *: utterance
		#    @: meta
		#    %: dependent tier
		if ltmp.startswith("*"):
			# ---- collect previous meta, clear meta ----
			metas.append(meta)
			meta = []
			# ---- if tiers, add to previous utterance, clear tiers ----
			if tiers: utterances[-1].extend(tiers)
			tiers = []
			# ---- add current line to utterances ----
			utterances.append([ltmp])  # as list to hold dependent tiers
		if ltmp.startswith("@"):
			# ---- if tiers, add to previous utterance, clear tiers ----
			if tiers: utterances[-1].extend(tiers)
			tiers = []
			# ---- add current line to meta ----
			meta.append(ltmp)
			# ---- if EOF, store remaining meta in final ----
			if ltmp == "@End":
				final.extend(meta)
		if ltmp.startswith("%"):
			tiers.append(ltmp)

	return metas, utterances, final

def check_token(surface: str) -> Tuple[str, str]:
	"""Adopted and modified from coltekin/childes-tr/misc/parse-chat.py
	For a given surface form of the token, return (surface, clean), where
	clean is the token form without CHAT codes.
	"""

	if surface is None:
		return None, None

	clean=''
	if re.match(TO_OMIT, surface):   # phonological forms are also omitted
		return surface, clean

	# remove unwanted markings to normalise token form
	clean = surface.replace(' ', '')
	clean = clean.replace('xxx', '')  # unintelligible, 'wxxxord' --> 'word'
	clean = clean.replace('(', '').replace(')', '')
	clean = clean.replace('0', '')  # 0token is omitted token
	clean = clean.replace('‡', ',')  # prefixed interactional marker
	clean = clean.replace('„', ',')  # suffixed interactional marker
	# clean = clean.replace('_', ' ')  # compound, uncomment to remove '_' in compounds
	if "@" in clean:
		clean = clean[:clean.index("@")]  # drop any @endings

	return surface, clean

# def to_deprel(gr: str) -> str:
	# Directly translate a given GR (grammatical relation) to its UD counterpart
	# using predefined dictionary GR2DEPREL.
	# If the given gr is in GR2DEPREL, return its corresponding deprel,
	# otherwise return gr (and give a warning).

# 	if not gr:  # empty or None
# 		return gr
# 	if not gr in GR2DEPREL:
# 		logger.warning(f"{gr} does not have a corresponding deprel in GR2DEPREL.")

# 	return GR2DEPREL[gr] if gr in GR2DEPREL else gr

def root_token(tokens: List[Token]) -> int:
	"""Get index of the real root in multi-root sentences.
	Current solution is perhaps inefficient.
	"""
	root_idx = -1
	for tok in tokens:
		if tok.deprel == 'root':
			root_idx = tok.index
		elif tok.deprel == 'incroot':
			root_idx = tok.index
		elif tok.head == '0' and tok.deprel not in ['vocative', 'parataxis']:
			root_idx = tok.index
	return root_idx if root_idx > 0 else None


def change_head_to_root(tok: Token, tokens: List[Token], is_multi=False, i=-1):
	"""Store original head in MISC, change head to root."""
	if is_multi and i >= 0:
		if not tok.misc[i]:
			tok.misc[i] = f"head={str(tok.head[i])}"
		else:
			tok.misc[i] += f"|head={str(tok.head[i])}"
		tok.head[i] = root_token(tokens)
	else:
		if not tok.misc:
			tok.misc = f"head={str(tok.head)}"
		else:
			tok.misc += f"|head={str(tok.head)}"
		tok.head = root_token(tokens)

def conditional_deprel(gr: str, tok: Token, tokens: List[Token], is_multi=False, upos: str=None, lemma: str=None, i=-1) -> str:
	"""Translate a given GR (grammatical relation) to its UD counterpart
	using conditional mapping for several selected cases, the rest uses dictionary mapping.
	Conditional mapping is based on grammatical information of other
	tokens in the sentence.

	To-Dos:
	--------
	- be extended to include more cases
	- use morph dict to organise input
	"""
	if gr == 'beg':
		if upos and upos not in ['INTJ', 'PROPN']:
			logger.info("BEG but not vocative.")
			return 'parataxis'
		else:
			return 'vocative'
		change_head_to_root(tok, tokens, is_multi, i)
	elif gr == 'end':
		return 'parataxis'
		change_head_to_root(tok, tokens, is_multi, i)
	# ---- dict translation ----
	elif not gr in GR2DEPREL:
		logger.warning(f"{gr} does not have a corresponding deprel in GR2DEPREL.")
		return gr
	else:
		return GR2DEPREL[gr]

def gr2deprel(tok: Token, tokens: List[Token], is_multi=False):
	"""Stores original GR in MISC, translate a given GR (grammatical relation)
	to its UD counterpart and modify deps accordingly, also works for multi-word tokens.
	"""
	upos = ''
	lemma = ''
	if is_multi:
		if not tok.misc:
			tok.misc = tuple(f"gr={gr}" for gr in tok.deprel if gr)
		else:
			tok.misc = tuple((s + f"|gr={tok.deprel[i]}" if s else f"gr={tok.deprel[i]}" for i, s in enumerate(tok.misc) if tok.deprel[i]))
			# ==== readable version ====
			# tmps = []
			# for i, s in enumerate(tok.misc):
			# 	tmp = ""
			# 	if s and tok.deprel[i]:
			# 		tmp = s + f"|gr={tok.deprel[i]}"
			# 	elif tok.deprel[i]:
			# 		tmp = f"gr={tok.deprel[i]}"
			# 	tmps.append(tmp)
			# tok.misc = tuple(tmps)
		for i, gr in enumerate(tok.deprel):
			upos = tok.upos[i] if tok.upos else ''
			lemma = tok.lemma[i] if tok.lemma else ''
			tok.deprel[i] = conditional_deprel(gr, tok, tokens, is_multi, upos, lemma, i)
			tok.deps[i] = f"{tok.head[i]}:{tok.deprel[i]}"
	else:
		if not tok.misc:
			tok.misc = f"gr={tok.deprel}"
		else:
			tok.misc += f"|gr={tok.deprel}"
		gr = tok.deprel  # less confusing name
		upos = tok.upos
		tok.assign_ud_deprel(conditional_deprel(gr, tok, tokens, is_multi, upos, lemma))
		tok.deps = f"{tok.head}:{tok.deprel}"

def to_ud_values(tokens: List[Token]) -> List[Token]:
	""" Translate CHAT annotations to UD values, currently for GRs to deprels.
	This method can also be extended for future decision of feature types and values
	if one would like to convert them to UD style. (To-Do)
	"""
	for tok in tokens:
		if type(tok.deprel) is list:  # multi-word tokens
			gr2deprel(tok, tokens, is_multi=True)
		elif tok.deprel:  # normal tokens
			gr2deprel(tok, tokens)
	return tokens

def to_upos(mor_code: str) -> str:
	"""If the given mor_code is in the predefined MOR2UPOS dict, return the
	corresponding upos, otherwise return mor_code.
	"""
	if not mor_code:  # empty or None
		return mor_code
	elif not mor_code[:1].isalpha():  # for '+...' and things alike
		return None

	if not mor_code in MOR2UPOS:
		if not re.match(PUNCT, mor_code) and not mor_code.split(':')[0].lower() in MOR2UPOS:
			logger.warning(f"{mor_code} does not have a corresponding UPOS in MOR2UPOS.")
		return MOR2UPOS[mor_code.split(':')[0]] if mor_code.split(':')[0].lower() in MOR2UPOS else mor_code

	return MOR2UPOS[mor_code] if mor_code in MOR2UPOS else mor_code

def parse_gra(gra_segment: str) -> Tuple[str, str]:
	head = gra_segment.split('|')[1]
	deprel = gra_segment.split('|')[-1].lower()
	return head, deprel

def parse_sub(sub_segment: str)-> Tuple[Union[str, None], List[str], str, str]:
	feat_pattern = re.compile(r"\d?[A-Z]+[a-z]?")
	lemma = None
	feat_str = []
	feat = ''
	lemma_feats, _, translation = sub_segment.partition('=')  # translation

	tmps = re.findall(r"[&|-]\w+", lemma_feats)
	if tmps:  # has feature
		feat_str = [f"FEAT={t[1:].title()}" for t in tmps]  # need to convert to UD feats
		feats = [f"{t}" for t in tmps]
		feat = '^'.join(feats)
	tmp = re.split(r'[|&#-]', lemma_feats)
	# lemma = tmp[0]
	if tmp[0] == 'I' or not re.match(FEAT, tmp[0]):  # !!! sometimes lemma is encoded
		lemma = tmp[0]
	elif re.match(FEAT, tmp[0]):
		logger.info(tmp[0])
		feat_str = tmp[0] + '^' + feat_str if feat_str else tmp[0]
	if not feat_str:
		feat_str = ''
	return lemma, feat_str, translation, feat

def parse_mor(mor_segment: str):
	"""Given a word-level MOR segment, extract the POS tag, lemma, features and other information
	   to be stored in the MISC field.
	"""
	lemma = None
	feat_str = []
	translation = None
	feat = None
	miscs = []

	pos, _, lemma_feats = mor_segment.partition("|")  # split by first |

	if pos == lemma_feats:
		miscs.append(f"form={mor_segment.replace('|', '@')}")
	if '#' in pos:  # has prefix
		miscs.append(f"prefix={pos.split('#')[0]}")
		pos = pos.split('#')[-1]
	if pos == '' or '+' in pos:  # punct
		lemma = lemma_feats.replace('+', '')  # special case of punctuations
		miscs.append(f"form={pos}")
	elif '+' in lemma_feats:  # compound
		tmps = re.split(r"\+\w+?\|", lemma_feats)
		l, f, t, feat = zip(*(parse_sub(tmp) for tmp in tmps[1:]))    # tmp[0] is empty string
		lemma = ''.join(l)
		if any(t): translation = '+'.join(t)  # or leave empty
		feat_str = list(chain(*f))  # or leave empty
		if any(feat): miscs.append(f"feats={'+'.join(feat)}")  # or leave empty
		ctmps = re.split(r"\+", lemma_feats)
		# components = [f"{tuple(ctmp.split('|'))}" for ctmp in ctmps[1:]]
		components = [f"{ctmp.replace('|', '@')}" for ctmp in ctmps[1:]]
		comp = '^'.join(components)
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
	gra: list of gra segments roughly correspond to the list of tokens, since multi-word tokens
		 have separated gra segments.
	mor: list of mor segments with one-to-one correspondance with the list of tokens.

	Return value: a list of chatconllu.Token objects.
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
			# else: normal tokens
				# if mor: lemma for compounds
				# if gra: head, deprel and deps
			# modify compound form, assign PUNCT to punctuations, modify lemma for proper nouns
			# create Tokens
		# ---------------------------
		if j in idx:  # multi-word tokens, implies has mor tier
			m = idx.index(j)  # the current token is the m th multi-word token in this utterance
			index = index + m
			num = len(re.split(r'~|\$', mor[j]))  # number of components in mwt
			multi = index + num - 1
			# logger.debug(f"j:{j}\tindex:{index}\tnum:{num}\tend:{multi}")
			# ---- get clitics type, for reconstruction of %mor  ----
			if re.findall(r'~|\$', mor[j]):
				type = re.findall(r'~|\$', mor[j])
			# ---- get token info from mor ----
			xpos, lemma, feats, misc = zip(*get_lemma_and_feats(mor[j], is_multi=True))
			upos = [to_upos(x.replace('+', '')) for x in xpos]
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

		# ---- lemma for PROPN ----
		if upos == "PROPN":
			lemma = form

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
		# logger.info(tok.feats)

	return tokens

def create_sentence(idx: int, lines: List[str]) -> Sentence:
	"""Given utterance index and all lines pertaining to the utterance,
	create a Sentence object.
	"""
	# ---- speaker ----
	speaker = lines[0][1:4]
	# print(f"speaker: {speaker}")

	# ---- tiers ----
	tiers = [x.split('\t')[0] for x in lines[1:]]
	# print(tiers)

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
	ud_toks = to_ud_values(toks)

	return Sentence(speaker=speaker,
					tiers=tiers_dict,
					gra=gra,
					mor=mor,
					chat_sent=utterance,
					clean=clean,
					comments=comments,
					sent_id=(idx+1),
					toks=ud_toks  # should be ud_toks
					)

def to_conllu(filename: 'pathlib.PosixPath', metas: List[List[str]], utterances:List[List[str]], final:List[str], clear_mor=False, clear_gra=False, clear_misc=False):
	final_empty = []
	final_idx = -1
	sent = create_sentence(final_idx, utterances[final_idx])
	while not sent.text() or sent.text() in ['.', '0 .']:
		final_empty.append(sent)
		final_idx -= 1
		sent = create_sentence(final_idx, utterances[final_idx])
	with open(filename, mode='w', encoding='utf-8') as f:
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
			if idx == 0:
				f.write(f"# final = {final}\n")
				f.write(f"# final_sents = {final_empty}\n")
			if idx == final_idx + len(utterances) - 1:
				print(idx)
				while final_empty:
					sent = final_empty.pop()
					f.write(f"# final_sent{final_idx} = *{sent.speaker}:\t{sent.chat_sent}\n")
					for t in sent.tiers.keys():
						if t[0].islower():
							symbol = '%'
							val = ' '.join(sent.tiers[t])
						else:
							symbol = '@'
							val = sent.comments
						f.write(f"# final_{t} = {symbol}{t}:\t{val}\n")

			elif idx < final_idx + len(utterances) and not sent.toks or sent.text() == '.':
				f.write(f"# empty_speaker = {sent.speaker}\n")
				f.write(f"# empty_chat_sent = {sent.chat_sent}\n")
				for t in sent.tiers.keys():
					f.write(f"# empty_{t} = {sent.tiers.get(t)}\n")
				# f.write(sent.conllu_str(mute=True))
			# if sent.text() == '.':
			# 	f.write(f"# empty = {sent.chat_sent}\n")
			# 	f.write(sent.conllu_str(mute=True))
			else:
				f.write(f"# sent_id = {sent.get_sent_id()}\n")
				f.write(f"# text = {sent.text()}\n")
				f.write(f"# chat_sent = {sent.chat_sent}\n")
				f.write(f"# speaker = {sent.speaker}\n")
				for t in sent.tiers.keys():
					f.write(f"# {t} = {sent.tiers.get(t)}\n")
				f.write(sent.conllu_str(clear_mor, clear_gra, clear_misc))
				# f.write(sent.conllu_str())
				f.write("\n")

def chat2conllu(files: List['pathlib.PosixPath'], clear_mor=False, clear_gra=False, clear_misc=False):
	for f in files:
		# ----- skip converted files ----
		# if f.with_suffix(".conllu").is_file():
		#   continue

		# ---- parse chat ----
		logger.info(f"parsing {f}...")
		with open(f, 'r', encoding='utf-8') as fp:
			metas, utterances, final = parse_chat(fp)

			fn = f.with_suffix(".conllu")
			to_conllu(fn, metas, utterances, final, clear_mor, clear_gra, clear_misc)

if __name__ == "__main__":

	test = [
		'beg|beg',
	 	'+"/.',
	 	'pro:sub|I',
	 	'pro:sub|I~v|will',
	 	'adj|Jamie&dn-POSS'
	 	]

	for t in test:
		pos, lemma, feat_str, misc = get_lemma_and_feats(t)
		logger.info(pos)
		logger.info(lemma)
		logger.info(feat_str)
		logger.info(misc)

