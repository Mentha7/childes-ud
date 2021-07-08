import argparse
import chatparser
# from pathlib import Path
# from logger import logger


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
		default="conllu"
		help="input format, supports 'conllu' and 'cha'")
	argp.add_argument(
		"corpora",
		nargs="+",
		help="names of CHILDES corpora if all files within needs conversion")

	args = argp.parse_args()

	for c in args.corpora:
		files = chatparser.list_files(dir=args.directory, format=args.format)
		logger.info(f"Processing files from {c}...")
		logger.info(f"listing all .{args.format} files in {args.directory}...")

		if args.format == "cha":
			chatparser.chat2conllu(files)
		elif args.format == "conllu":
			chatparser.conllu2chat(files)
		else:
			logger.info(f"{args.format} is not supported.")
			break


if __name__ == "__main__":
	main()
