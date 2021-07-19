import pytest
from chatconllu import chatparser

@pytest.mark.parametrize("form, toks",
						[
						("one (.) two (..) three (...) .", ['one', 'two', 'three', '.']),  # pause
						("one (10:02.05) two (.5) three (2.) .", ['one', 'two', 'three', '.']),  # timed pause
						("<her gonna> [/?] he 0is gonna hug her [^ ns] .", ['he', '0is', 'gonna', 'hug', 'her', '.']),  # retracing
						("now <you tell me> [//] (.) you tell me all about it .", ['now', 'you', 'tell', 'me', 'all', 'about', 'it', '.']),  # retracing
						("commydit@o [x 8] (.) quackquack@o chickchick@o commydit@o [x 5] .", ['commydit@o', 'quackquack@o', 'chickchick@o', 'commydit@o', '.']),  # repetitions
						("dat [: that] Urs(u)la's [?] coffee .", ['that', 'Urs(u)la\'s', 'coffee', '.']),  # best guess
						("<&h> [/?] her [^ ew:she] [^ epronoun] pour [^ ev] a [^ ew:the] [^ emorph] juice in there [^ eu] .", ['her', 'pour', 'a', 'juice', 'in', 'there', '.']),  # utterance error
						("top a [: of][* fil] can .", ['top', 'of', 'can', '.']),  # uttrance error star
						("dat [: that] Urs(u)la's [?] coffee . [% \comment]", ['that', 'Urs(u)la\'s', 'coffee', '.']),  # comment on main tier
						("又 到 了 另外 一 个 房间 „ 对不对 [^c] ?", ['又', '到', '了', '另外', '一', '个', '房间', '„', '对不对', '?']),  # complex local event
						("Fraser . [+ IMIT]", ['Fraser', '.']),  # utterance postcodes
						("call Grandma and talk +...", ['call', 'Grandma', 'and', 'talk', '...']),  # trailing off
						("0 .", []),  # sign without speech
						("<Mommy stair> [?] .", ['Mommy', 'stair', '.']),  # to expand
						("tam [: some] more .", ['some', 'more', '.']),  # to replace, one colon
						("tam [:: some] more .", ['some', 'more', '.']),  # to replace, double colon
						("", []),  # no utterance
						(None, None),  # none
						])
def test_normalise_utterance_all(form, toks):
	assert chatparser.normalise_utterance(form)[0] == toks


# def test_normalise_utterance_pause():
# 	utterance = "one (.) two (..) three (...) ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['one', 'two', 'three', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_timed_pause():
# 	utterance = "one (10:02.05) two (.5) three (2.) ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['one', 'two', 'three', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_retracing1():
# 	utterance = "<her gonna> [/?] he 0is gonna hug her [^ ns] ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['he', '0is', 'gonna', 'hug', 'her', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_retracing2():
# 	utterance = "now <you tell me> [//] (.) you tell me all about it ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['now', 'you', 'tell', 'me', 'all', 'about', 'it', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_repetitions():
# 	utterance = "commydit@o [x 8] (.) quackquack@o chickchick@o commydit@o [x 5] ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['commydit@o', 'quackquack@o', 'chickchick@o', 'commydit@o', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_best_guess():
# 	utterance = "dat [: that] Urs(u)la's [?] coffee ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['that', 'Urs(u)la\'s', 'coffee', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_error():
# 	utterance = "<&h> [/?] her [^ ew:she] [^ epronoun] pour [^ ev] a [^ ew:the] [^ emorph] juice in there [^ eu] ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['her', 'pour', 'a', 'juice', 'in', 'there', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_error_star():
# 	utterance = "top a [: of][* fil] can ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['top', 'of', 'can', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_comment_on_main():
# 	utterance = "dat [: that] Urs(u)la's [?] coffee . [% \comment]"
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['that', 'Urs(u)la\'s', 'coffee', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_complex_local_event():
# 	utterance = "又 到 了 另外 一 个 房间 „ 对不对 [^c] ?"
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['又', '到', '了', '另外', '一', '个', '房间', '„', '对不对', '?']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_postcodes():
# 	utterance = "Fraser . [+ IMIT]"
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['Fraser', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_trailing_off():
# 	utterance = "call Grandma and talk +..."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['call', 'Grandma', 'and', 'talk', '...']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_sign_without_speech():
# 	utterance = "0 ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = []
# 	assert tokens == expected_tokens


# def test_normalise_utterance_to_expand():
# 	utterance = "<Mommy stair> [?] ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['Mommy', 'stair', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_to_replace_one_colon():
# 	utterance = "tam [: some] more ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['some', 'more', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_to_replace_double_colon():
# 	utterance = "tam [:: some] more ."
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = ['some', 'more', '.']
# 	assert tokens == expected_tokens


# def test_normalise_utterance_no_utterance():
# 	utterance = ""
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	expected_tokens = []
# 	assert tokens == expected_tokens


# def test_normalise_utterance_none():
# 	utterance = None
# 	tokens = chatparser.normalise_utterance(utterance)[0]
# 	assert tokens is None


def test_check_token_unintelligible1():
	pass


def test_check_token_unintelligible2():
	pass


def test_check_token_unintelligible3():
	pass


def test_check_token_phono_coding():
	pass


def test_check_token_untranscribed():
	pass


def test_check_token_phono_fragments():
	pass


def test_check_token_meta_linguistic_use():
	pass


def test_check_token_onomatopoeia():
	pass


def test_check_token_omitted_token():
	pass


def test_check_token_prefixed_interactional_marker():
	pass


def test_check_token_suffixed_interactional_marker():
	pass


def test_check_token_compound():
	pass


def test_check_token_combined():
	pass


def test_check_token_none():
	pass
