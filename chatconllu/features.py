import re
from logger import logger

WELLS = {
	'-AGT',
	'-MENT',
	'-ATION',
	'&13S',
	'-PL',
	'&dn',
	'-DIM',
	'-POSS',
	'-ISH',
	'-CP',
	'-LESS',
	'-LY',
	'-ABLE',
	'-NESS',
	'-FULL',
	'-Y',
	'-SP'
	}

BROWN = {
	'-AGT',
	'-ATION',
	'-FULL',
	'&13S',
	'-ISH',
	'-PRESP',
	'-lantern',
	'-CP',
	'-SP',
	'-DIM',
	'-PAST',
	'-PL',
	'-ABLE',
	'-LESS',
	'&dn',
	'-AL',
	'-NESS',
	'-Y',
	'-LY',
	'-toe',
	'-MENT',
	'-POSS'
	}

BELFAST = {
	'-PL',
	'&13S',
	'-ATION',
	'-3S',
	'-CP',
	'-FULL',
	'-AL',
	'-sac',
	'-MENT',
	'&dn',
	'-POSS',
	'-LY',
	'-ABLE',
	'-PAST',
	'-ISH',
	'-AGT',
	'-NESS',
	'-SP',
	'-Y',
	'-LESS',
	'-DIM'
	}

LEIVILLE = {
	'&sg',
	'&PASS',
	'&3p',
	'&SUB',
	'&f',
	'&pl',
	'-PPRE',
	'&2p',
	'&1p',
	'&2s',
	'&IMP',
	'-PL',
	'&3sp',
	'&23s',
	'&12s',
	'&3s',
	'&PRES',
	'&PP',
	'&m',
	'&13s',
	'&1s'
	}

MTLN = {
	'&13s',
	'&1s',
	'-PL',
	'&2p',
	'&2s',
	'&pl',
	'&IMP',
	'&3s',
	'&3p',
	'&PASS',
	'-PPRE',
	'&1p',
	'&f',
	'&12s',
	'&m',
	'&PRES',
	'&SUB',
	'&sg'
	}

GENEVA = {
	'&2p',
	'&pl',
	'-PL',
	'&1s',
	'&PRES',
	'&SUB',
	'&1p',
	'&13s',
	'&m',
	'&f',
	'-PPRE',
	'&3s',
	'&2s',
	'&3p',
	'&IMP',
	'&PP',
	'&sg',
	'&12s',
	'&PASS'}

VIONCOLAS = {
	'&pl',
	'&m',
	'&SUB',
	'&1s',
	'-PL',
	'&3p',
	'-DEIC',
	'&f',
	'&3sp',
	'&PASS',
	'&sg',
	'&3s',
	'&2p',
	'&1p',
	'&12s',
	'&23s',
	'&13s',
	'&PRES',
	'&2s',
	'-PPRE',
	'&PPRE'
	}

TONELLI = {
	'&SUBJ',
	'&PRES',
	'-m',
	'-3S',
	'&IMP',
	'-f',
	'&pl',
	'&PAST',
	'&SUB',
	'&OBJ',
	'-SG',
	'&FUT',
	'&2S',
	'&FEM',
	'&m',
	'-DIM',
	'&PRET',
	'&sg',
	'&COND',
	'&f'}

ENGLISH_MIAMIBILING = {'-PL', '&13S', '-AGT', '-LY', '-PASTP', '-FULL', '-POSS', '-Y'}
ENG = [ENGLISH_MIAMIBILING, BROWN, BELFAST, WELLS]
FRA = [MTLN, LEIVILLE, VIONCOLAS, GENEVA]
ITA = [TONELLI]
ALL = [
	ENGLISH_MIAMIBILING,
	BROWN,
	BELFAST,
	WELLS,
	MTLN,
	LEIVILLE,
	VIONCOLAS,
	GENEVA,
	TONELLI,
	]
# res = set()
# for en in ALL:
#   res = res.union(en)
#   logger.info(res)

ENG_FEATS = {
	# ---- inflectional categories ----
	'-CP',  # Degree=Cmp
	'-SP',  # Degree=Sup
	'&13S',  # # Number=Sing|Person=3
	'-PRESP',  # Tense=Pres|VerbForm=Part
	'-POSS',  # Poss=Yes
	'-PASTP',  # Tense=Past|VerbForm=Part
	'-AGT',  # agent
	'-3S',  # Number=Sing|Person=3
	'-PL',  # Number=Plur
	'-PAST',  # Tense=Past
	# ---- derivational categories ----
	'&dn',  # derivation from noun, dx indicates derivation from original category x
	'-LESS'
	'-ISH',  # denominal
	'-LY',  # deadjectival
	'-FULL',
	'-ATION',
	'-NESS',
	'-lantern',
	'-MENT',
	'-sac',
	'-AL',
	'-ABLE',  # deverbal
	'-toe',
	'-Y',  # deverbal, denominal
	'-DIM',  # diminutive
		}

ALL_FEATS = {
	'-PL', '&dn', '-lantern', '-NESS', '&PASS', '-f', '-SG', '-PASTP',
	'&PPRE', '&12s', '&PAST', '&1p', '&sg', '&SUBJ', '&13S', '-FULL',
	'&2S', '-SP', '&3sp', '-PPRE', '&PP', '&OBJ', '-DEIC', '&FEM', '-toe',
	'&3s', '-MENT', '-sac', '-ATION', '-DIM', '-PRESP', '&f', '-LY',
	'&SUB', '&pl', '-ISH', '&23s', '&2s', '-POSS', '-Y', '-CP', '-3S',
	'-LESS', '-AL', '&FUT', '-m', '&m', '&2p', '&COND', '&IMP', '-AGT',
	'-ABLE', '&3p', '&PRES', '&PRET', '-PAST', '&13s', '&1s',
	}


# feats = []
# for f in ALL_FEATS:
#   feats.append(re.sub("^[&|-]", "", f).lower())
# feats.sort()
# logger.info(feats)

MOR2FEATS = {
	'12s':'Number=Sing|Person=2',  #
	'13s':'Number=Sing|Person=3',  #
	'1p':'Number=Plur|Person=1',
	'1s':'Number=Sing|Person=1',
	'23s':'Number=Sing|Person=3',  #
	'2p':'Number=Plur|Person=2',
	'2s':'Number=Sing|Person=2',
	'3p':'Number=Plur|Person=3',
	'3s':'Number=Sing|Person=3',
	'3sp':'Number=Plur|Person=3',  #
	'cond':'Mood=Cnd',
	'cp':'Degree=Cmp',
	'f':'Gender=Fem',
	'fem':'Gender=Fem',
	'fut':'Tense=Fut',
	'inf':'VerbForm=Inf',
	'imp':'Mood=Imp',  # imperative
	'impf':'Tense=Imp',
	'm':'Gender=Masc',
	'pass':'Voice=Pass',
	'past':'Tense=Past',
	'pastp':'Tense=Past|VerbForm=Part',
	'pl':'Number=Plur',
	'poss':'Poss=Yes',
	'pp':'Tense=Past|VerbForm=Part',
	'ppre':'Tense=Pres|VerbForm=Part',
	'pres':'Tense=Pres',
	'presp':'Tense=Pres|VerbForm=Part',
	'pret':'Tense=Past',
	'sg':'Number=Sing',
	'sp':'Degree=Sup',
	'sub':'Mood=Sub',
	'subj':'Mood=Sub',
	'ppart':"Tense=Past|VerbForm=Part",
	'super':"Degree=Sup",
	'prog':"VerbForm=Ger",
	'mas':"Gender=Masc",
	'masc':"Gender=Masc",
	# ---- no corresponding value ----
	'able':'',
	'adv':'',
	'agt':'',
	'al':'',
	'ation':'',
	'deic':'',
	'dim':'',
	'dn':'',
	'dv':'',
	'dadj':'',
	'dup':'',
	'ful':'',
	'full':'',
	'ish':'',
	'le':'',
	'les':'',
	'less':'',
	'ly':'',
	'ment':'',
	'n':'',
	'ness':'',
	'obj':'',
	'sac':'',
	'v':'',
	'toe':'',
	'y':'',
	'zero':'',
	'aug':'',
}

def mor2feats(mor_code: str) -> str:
	"""If the given mor_code is in the predefined MOR2FEATS dict, return the
	corresponding upos, otherwise return mor_code.
	"""
	if not mor_code:  # empty or None
		return ''

	m = re.sub("^[&|-]", "", mor_code).lower()

	if not m in MOR2FEATS:
		logger.warning(f"{mor_code} does not have a corresponding UD feature in MOR2FEATS.")

	return MOR2FEATS[m] if m in MOR2FEATS else ''

def is_key(feat):
	return feat in MOR2FEATS
