import argparse
import chatparser
from pathlib import Path
from logger import logger
import time


def main():
	argp = argparse.ArgumentParser()
	argp.add_argument(
		"-d",
		"--directory",
		type=str,
		default="/home/jingwen/Desktop/thesis",
		help="directory of CHILDES corpora")
	argp.add_argument(
		"-f",
		"--format",
		type=str,
		default="cha",
		help="input format, supports 'conllu' and 'cha'")
	argp.add_argument(
		"corpora",
		nargs="+",
		help="names of CHILDES corpora if all files within needs conversion")

	args = argp.parse_args()

	if args.format != "cha" and args.format != "conllu":
		logger.fatal(f"'{args.format}' is not supported. Supported values for format are 'cha' and 'conllu'")
		return

	start_time = time.time()
	for c in args.corpora:
		directory = Path(args.directory, c)
		if not directory.exists():
			logger.fatal(f"The directory you specified does not exist.\nPlease recheck if you entered the path correctly: '{directory}'")
			return

		files = chatparser.list_files(directory, args.format)
		if not files:
			logger.fatal(f"No files with extension '{args.format}' are found within {Path(args.directory, c)}.")
			return

		logger.info(f"Listing all .{args.format} files in {directory}...")
		for f in files:
			logger.info(f"\t{f}")

		if args.format == "cha":
			chatparser.chat2conllu(files)
		elif args.format == "conllu":
			chatparser.conllu2chat(files)
	end_time = time.time()
	logger.info(f"It took {end_time-start_time:.2f} secods.")

if __name__ == "__main__":
	main()
