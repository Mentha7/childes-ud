import pytest
from chatconllu import chatparser

@pytest.mark.parametrize("form, toks",
					[
						("one (.) two (..) three (...) .",
						 ['one', 'two', 'three', '.']),  # pause
						("one (10:02.05) two (.5) three (2.) .",
						 ['one', 'two', 'three', '.']),  # timed pause
						("<her gonna> [/?] he 0is gonna hug her [^ ns] .",
						 ['he', '0is', 'gonna', 'hug', 'her', '.']),  # retracing
						("now <you tell me> [//] (.) you tell me all about it .",
						 ['now', 'you', 'tell', 'me', 'all', 'about', 'it', '.']),  # retracing
						("commydit@o [x 8] (.) quackquack@o chickchick@o commydit@o [x 5] .",
						 ['commydit@o', 'quackquack@o', 'chickchick@o', 'commydit@o', '.']),  # repetitions
						("dat [: that] Urs(u)la's [?] coffee .",
						 ['that', 'Urs(u)la\'s', 'coffee', '.']),  # best guess
						("<&h> [/?] her [^ ew:she] [^ epronoun] pour [^ ev] a [^ ew:the] [^ emorph] juice in there [^ eu] .",
						 ['her', 'pour', 'a', 'juice', 'in', 'there', '.']),  # utterance error
						("top a [: of][* fil] can .",
						 ['top', 'of', 'can', '.']),  # uttrance error star
						("dat [: that] Urs(u)la's [?] coffee . [% \\comment]",
						 ['that', 'Urs(u)la\'s', 'coffee', '.']),  # comment on main tier
						("又 到 了 另外 一 个 房间 „ 对不对 [^c] ?",
						 ['又', '到', '了', '另外', '一', '个', '房间', '„', '对不对', '?']),  # complex local event
						("Fraser . [+ IMIT]",
						 ['Fraser', '.']),  # utterance postcodes
						("call Grandma and talk +...",
						 ['call', 'Grandma', 'and', 'talk', '...']),  # trailing off
						("0 .",
						 []),  # sign without speech
						("<Mommy stair> [?] .",
						 ['Mommy', 'stair', '.']),  # to expand
						("tam [: some] more .",
						 ['some', 'more', '.']),  # to replace, one colon
						("tam [:: some] more .",
						 ['some', 'more', '.']),  # to replace, double colon
						("< 结果 开 冰箱 > [<] < 就 > [//] 他", ['结果', '开', '冰箱', '他']),  # test order
						("< 结果 开 冰箱 > [//] < 就 > [<] 他", ['就', '他']),  # test order
						("<du [/] <in &Kin> [/] <in im &Ki> [/] im Kinderladen xxx> [>] .", ['im', 'Kinderladen', 'xxx', '.']),
						("",
						 []),  # no utterance
						(None,
						 None),  # none
					])
def test_normalise_utterance_all(form, toks):
	assert chatparser.normalise_utterance(form) == toks


@pytest.mark.parametrize("surface, clean",
						[
						("xxx", ""),  # xxx -- unintelligible
						("yyy", ""),  # yyy -- phonological coding
						("www", ""),  # www -- untranscribed
						("&phon", ""),  # phonological fragments
						("0token", "token"),  # 0token is omitted token
						("‡", ","),  # prefixed interactional marker
						("„", ","),  # suffixed interactional marker
						("all_gone", "all gone"),  # compound
						("commydit@o", "commydit"),  # onomatopoeia
						("blah@q", "blah"),  # meta-linguistic use
						("0all_gone@q", "all gone"),  # mixture
						("", ""),  # empty
						(None, None),  # none
						])
def test_check_token_all(surface, clean):
	assert chatparser.check_token(surface)[1] == clean


@pytest.mark.parametrize("mor_code, upos",
						[
						("adj", "ADJ"),
						("pro:indef","PRON"),
						("doesn't exist", "doesn't exist"),
						("", ""),
						(None, None),
						])
def test_to_upos(mor_code, upos):
	assert chatparser.to_upos(mor_code) == upos
