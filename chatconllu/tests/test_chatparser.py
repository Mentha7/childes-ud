import pytest
from chatconllu import chatparser


def test_normalise_utterance_pause():
	utterance = "one (.) two (..) three (...) ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['one', 'two', 'three', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_timed_pause():
	utterance = "one (10:02.05) two (.5) three (2.) ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['one', 'two', 'three', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_retracing1():
	utterance = "<her gonna> [/?] he 0is gonna hug her [^ ns] ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['he', '0is', 'gonna', 'hug', 'her', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_retracing1():
	utterance = "now <you tell me> [//] (.) you tell me all about it ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['now', 'you', 'tell', 'me', 'all', 'about', 'it', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_repetitions():
	utterance = "commydit@o [x 8] (.) quackquack@o chickchick@o commydit@o [x 5] ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['commydit@o', 'quackquack@o', 'chickchick@o', 'commydit@o', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_best_guess():
	utterance = "dat [: that] Urs(u)la's [?] coffee ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['that', 'Urs(u)la\'s', 'coffee', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_error():
	utterance = "<&h> [/?] her [^ ew:she] [^ epronoun] pour [^ ev] a [^ ew:the] [^ emorph] juice in there [^ eu] ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['her', 'pour', 'a', 'juice', 'in', 'there', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_error_star():
	utterance = "top a [: of][* fil] can ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['top', 'of', 'can', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_comment_on_main():
	utterance = "dat [: that] Urs(u)la's [?] coffee . [% \comment]"
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['that', 'Urs(u)la\'s', 'coffee', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_complex_local_event():
	utterance = "又 到 了 另外 一 个 房间 „ 对不对 [^c] ?"
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['又', '到', '了', '另外', '一', '个', '房间', '„', '对不对', '?']
	assert tokens == expected_tokens


def test_normalise_utterance_postcodes():
	utterance = "Fraser . [+ IMIT]"
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['Fraser', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_trailing_off():
	utterance = "call Grandma and talk +..."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['call', 'Grandma', 'and', 'talk', '...']
	assert tokens == expected_tokens


def test_normalise_utterance_sign_without_speech():
	utterance = "0 ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = []
	assert tokens == expected_tokens


def test_normalise_utterance_to_expand():
	utterance = "<Mommy stair> [?] ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['Mommy', 'stair', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_to_replace_one_colon():
	utterance = "tam [: some] more ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['some', 'more', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_to_replace_double_colon():
	utterance = "tam [:: some] more ."
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['some', 'more', '.']
	assert tokens == expected_tokens


def test_normalise_utterance_no_utterance():
	utterance = ""
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = []
	assert tokens == expected_tokens


def test_normalise_utterance_none():
	utterance = None
	tokens = chatparser.normalise_utterance(utterance)[0]
	expected_tokens = ['that', 'Urs(u)la\'s', 'coffee', '.']
	assert tokens is None


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
