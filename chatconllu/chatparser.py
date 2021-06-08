"""
Utilities to parse .cha files.
"""
import sys
import re
import fileinput
from pathlib import Path

from logger import logger
from helpers.chat import ChatToken, ChatSentence, ChatLabel, ChatMeta

BROWN = "/home/jingwen/Desktop/thesis/Brown/"
FILE = "test.cha"

old = re.compile('^\\*')

def list_files(dir):
	return (x for x in Path(dir).glob("**/*.cha") if not x.name.startswith("._"))

def read_file(filename):
	""" Read file line by line, if line:
		- starts with @: metadata
		- starts with *: utterance (1)
		- starts with %: tiers (n)
		note:
		- field and value are separated by tabs
		- labels are in square brackets
	"""
	fn = filename.split('.')[0]
	with open(Path('tmp', f'{fn}_new.cha'), 'w', encoding='utf-8') as f:
		for line in fileinput.input(Path(BROWN, filename), inplace=False):
			match = old.match(line)
			print('\n'+ line.strip() if match or line == '@End\n' else line.strip(), file=f)



if __name__ == "__main__":
	logger.info(f"listing all .cha files in {BROWN}...")
	files = list_files(BROWN)
	try:
		while True:
			i = next(files)
			print(i)
	except StopIteration:
		pass

	# read file
	logger.info(f"reading {FILE}...")
	read_file(FILE)
