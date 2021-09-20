"""
Utilities to obtain clean utterances from CHAT.
"""

import re
from logger import logger

until_eow = re.compile(r"[^,.;?!”<>\[\] ]+")

# -------- define patterns to omit --------
pause = r"^\(\.+\)"  # (.), (..), (...)
timed_pause = r"^\((\d+?:)?(\d+?)?\.(\d+?)?\)"  # ((min:)(sec).(decimals))
best_guess = r"^\[\?\]"  # [?]
complex_local_event = r"^\[\^.*?\]"  # [^ xxx] [^c]
self_completion = r"^\+,"
other_completion = r"^\+\+"
stressing = r"^\[!!?\]"
quoted_utterance = r"^\+\""
quotation_follows = r"^\+\"/\."
quick_uptake = r"^\+\^"
lazy_overlap = r"^\+<"
error_marking = r"^\[\*\]"

omission = [
	pause,
	timed_pause,
	best_guess,
	complex_local_event,
	self_completion,
	other_completion,
	stressing,
	quotation_follows,
	quoted_utterance,
	quick_uptake,
	lazy_overlap,
	error_marking,
	]
# -------- define delete previous token/scope pattern --------
retracing_no_angle_brackets = r"^\[/(?:[/?])?\]"  # [//] or [/?] or [/] --> [retrace]
x_retrace = r"^\[[=%?] [()@\-\+\.\"\w]+(\')?\w*( [()@\-\+\.\"\w]+)*( )??\] \[/(?:[/?])?\]"

delete_previous = [
	retracing_no_angle_brackets,
	x_retrace,
	]
# -------- define start bracketed elements pattern --------
postcodes = r"^\[\+"  # [+
repetitions = r"^\[x"  # [x
alternative_transcriptions = r'^\[=\?'  # [=?
explanations = r'^\[='  # [=
error = r"^\[\^"  # [^
error_star = r"^\[\*"  # [*
comment_on_main = r"^\[%"  # [%
paralinguistics_prosodics = r'^\[=!'

start = [
	postcodes,
	repetitions,
	alternative_transcriptions,
	explanations,
	error,
	error_star,
	comment_on_main,
	paralinguistics_prosodics,
]
# ---- compile regex patterns ----
to_omit = re.compile('|'.join(o for o in omission))  # <whatever> [/?] or <whatever> [//]

to_replace = re.compile(r"^\[::?( )?")

delete_prev = re.compile('|'.join(delete_previous))

start_bracket = re.compile('|'.join(start))

overlap = re.compile(r"^\[?[<>]\]")

trailing_off = re.compile(r"\+...")  # +...

special_terminators = re.compile(r'^\+(?:/(?:/\.|[.?])|"/\.)')

quotation = re.compile(r"[“”]")

def push(obj, l, depth):
	"""Based on the answer on
		https://stackoverflow.com/questions/4284991/\
		parsing-nested-parentheses-in-python-grab-content-by-level
	"""
	if depth < 0:
		raise ValueError('mismatch')
	while depth:
		l = l[-1]
		depth -= 1
	l.append(obj)

def normalise_utterance(line):
	""" Based on the answer on
		https://stackoverflow.com/questions/4284991/\
		parsing-nested-parentheses-in-python-grab-content-by-level
		Transform nested angle brackets into nested lists, also take [<] and [>] into account.
	"""
	if line is None:
		return None, None

	if line == "0 .":
		return [], line
	groups = []
	depth = 0

	tmp = []
	i = 0
	while i < len(line):
		if line[i] == '<':
			if i !=0 and line[i-1] == '[':
				# print("2: is scoped symbol, do not open")
				tmp.append(line[i])
				i += 1
				continue
			push([], groups, depth)
			# print(f"1: open depth {depth}")
			depth += 1
			i += 1
		elif line[i] == '>':
			if i !=0 and line[i-1] == '[':
				# print("4: is scoped symbol, do not close")
				tmp.append(line[i])
				i += 1
				continue
			token = ''.join(tmp)
			tmp = []
			if token:
				push(token, groups, depth)
			# print(f"3: close depth {depth}")
			depth -= 1
			i += 1
		elif line[i] == " ":
			token = ''.join(tmp)
			tmp = []
			if token:
				push(token, groups, depth)
			i += 1
		elif line[i] == "]" and i+1 < len(line) and line[i+1] == "[":
			tmp.append(line[i])
			token = ''.join(tmp)
			tmp = []
			if token:
				push(token, groups, depth)
			i += 1
		elif line[i] == "," and line[i-1].isalpha():
			token = ''.join(tmp)
			tmp = []
			if token:
				push(token, groups, depth)
			push(line[i], groups, depth)
			i += 1
		else:
			tmp.append(line[i])
			i += 1
		if i == len(line):  # final token
			token = ''.join(tmp)
			tmp = []
			if token:
				push(token, groups, depth)
			i += 1
	return replace(remove_elements(omit(flatten(delete(groups))))), line
	# return remove_elements(replace(omit(flatten(delete(groups))))), line

def flatten(groups):
	""" Flatten a list of lists.
	"""
	flat = []
	for subgroup in groups:
		if isinstance(subgroup, list):
			for g in subgroup:
				flat.append(g)
		else:
			flat.append(subgroup)
	return flat

# def replace(flat):
# 	for i, f in enumerate(flat):
# 		# logger.info(f)
# 		if re.match(to_replace, f):
# 			# logger.info("replace")
# 			ind = i+1
# 			while ind < len(flat):
# 				if flat[ind].endswith(']'):
# 					new = ''.join(x for x in flat[ind] if x.isalpha())
# 					break
# 				else:
# 					ind += 1
# 			flat[ind] = new
# 			flat.pop(i)
# 			flat.pop(i-1)
# 	return flat

# def remove_elements(flat):
# 	for i, f in enumerate(flat):
# 		if re.match(start_bracket, f):
# 			# logger.debug(flat)
# 			# logger.info("remove space-separated square-bracketed elements")
# 			# logger.debug(f)
# 			ind = i+1
# 			while ind < len(flat):
# 				if flat[ind].endswith(']'):
# 					flat.pop(ind)
# 					break
# 				else:
# 					flat.pop(ind)
# 			flat.pop(i)
# 		elif re.match(trailing_off, f):
# 			flat[i] = f[1:]  # remove +
# 	return flat

def remove_elements(flat):
	results = []
	keep = True

	for i, f in enumerate(flat):
		if re.match(start_bracket, f):
			keep = False

		if keep:
			results.append(f)

		if not keep and f.endswith(']'):
			keep = True

	return results

def replace(flat):
	results = []
	replace = False
	replace_tmp = []

	for i, f in enumerate(flat):
		if re.match(to_replace, f):
			replace = True

		if replace:
			replace_tmp.append(f)
		else:
			results.append(f)

		if replace and f.endswith(']'):
			replace_tmp[-1] = replace_tmp[-1][:-1]
			results.pop()
			results += replace_tmp[1:]
			replace_tmp = []
			replace = False

	return results

def omit(flat):
	result = flat.copy()
	for i, f in enumerate(flat):
		tmp = f
		if re.match(special_terminators, tmp):
			tmp = tmp[-1]
		if re.search(to_omit, tmp):
			tmp = re.sub(to_omit, '', tmp)
		if re.search(quotation, tmp):
			tmp = re.sub(quotation, '', tmp)
		if re.match(delete_prev, tmp):
			tmp = re.sub(delete_prev, '', tmp)
		if re.match(overlap, tmp):
			tmp = re.sub(overlap, '', tmp)
		if re.match(trailing_off, tmp):
			tmp = tmp[1:]  # remove +
		result[i] = tmp
	return [r for r in result if r]

def delete(groups):
	""" Delete from nested list the elements followed by members in delete_prev.
	"""
	for i, g in enumerate(groups):
		if isinstance(g, list):
			delete(g)
		else:
			if re.match(delete_prev, g):
				if i-1 < 0:
					print("index error")
				else:
					deleted = groups.pop(i-1)
					if not isinstance(deleted, list):
						while re.match(to_omit, deleted):
							print("=======================================================")
							print(groups)
							deleted = groups.pop(i)

	return groups



if __name__ == '__main__':
	# print(normalise_utterance('<du [/] <in &Kin> [/] <in im &Ki> [/] im Kinderladen xxx>')) # ['a', ['b', ['c', 'd'], 'f']]
	# print(normalise_utterance("<<pattycake> [/] (.) pattycake (.) baker's man> [?] ."))
	# print(normalise_utterance("<here <monk(ey)> [/] monkey> [>] +..."))
	# print(normalise_utterance("<<yeah yeah> [/] yeah> [?] ."))
	# print(normalise_utterance("< 结果 开 冰箱 > [<] < 就 > [//] 他"))
	# print(normalise_utterance("< 结果 开 冰箱 > [//] < 就 > [<] 他"))
	print(normalise_utterance("tam [:: some] more [: moore] ."))
	print(normalise_utterance("tam [:: some bla] more [: moore] ."))
	print(normalise_utterance("tam [:: some][:: asdf] more [: moore] ."))
	print(normalise_utterance("dat [: that] Urs(u)la's [?] coffee . [% \\comment something]"))
	# print(normalise_utterance("<Mommy stair> [?] ."))
	# print(normalise_utterance("0 ."))
	# print(normalise_utterance("Fraser . [+ IMIT]"))
	# print(normalise_utterance("I [?] [/] (.) I yyy Bobo ."))
	# print(normalise_utterance("pop@o goes the measle [: weasel][* sem] ."))
	# print(normalise_utterance("what cha [: you] going to draw ?"))
	print(normalise_utterance("<&h> [/?] her [^ ew:she] [^ epronoun] pour [^ ev] a [^ ew:the] [^ emorph] juice in there [^ eu] ."))
	print(normalise_utterance("<&h> [/?] her [^ ew:she] a [^ epronoun] pour [^ ev] a [^ ew:the] a [^ emorph] juice in there [^ eu] ."))

	# normalise_utterance("<&h> [/?] her [^ ew:she] [^ epronoun] pour [^ ev] a [^ ew:the] [^ emorph] juice in there [^ eu] .")
	# normalise_utterance("<&h> [/?] her [^ ew:she] a [^ epronoun] pour [^ ev] a [^ ew:the] a [^ emorph] juice in there [^ eu] .")
	print(normalise_utterance("<and I will> [?] [//] (.) and I was +..."))
	print(normalise_utterance("<and I will> [//] (.) and I was +..."))
	print(normalise_utterance("when it's one it's “man (.)” and when there're two (.) it's +..."))
