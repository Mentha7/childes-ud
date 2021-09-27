import argparse
import chatparser
import conlluparser
from helpers.utils import list_files
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
        "-fn",
        "--filename",
        type=str,
        help="if specified, matches a single file")
    argp.add_argument(
        "corpora",
        nargs="+",
        help="names of CHILDES corpora if all files within needs conversion")
    #---- booleans ----
    argp.add_argument('--mor', dest='clear_mor', action='store_false')
    argp.add_argument('--no-mor', dest='clear_mor', action='store_true')
    argp.set_defaults(clear_mor=False)

    argp.add_argument('--gra', dest='clear_gra', action='store_false')
    argp.add_argument('--no-gra', dest='clear_gra', action='store_true')
    argp.set_defaults(clear_gra=False)

    argp.add_argument('--misc', dest='clear_misc', action='store_false')
    argp.add_argument('--no-misc', dest='clear_misc', action='store_true')
    argp.set_defaults(clear_misc=False)

    argp.add_argument('--new-mor', dest='generate_mor', action='store_true')
    argp.set_defaults(generate_mor=False)

    argp.add_argument('--new-gra', dest='generate_gra', action='store_true')
    argp.set_defaults(generate_gra=False)

    argp.add_argument('--cnl', dest='generate_cnl', action='store_true')
    argp.set_defaults(generate_gra=False)

    argp.add_argument('--pos', dest='generate_pos', action='store_true')
    argp.set_defaults(generate_pos=False)

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

        files = []
        if args.filename:
            files = list_files(directory, args.format, args.filename)
        else:
            files = list_files(directory, args.format)
        if not files:
            logger.fatal(f"No files with extension '{args.format}' are found within {Path(args.directory, c)}.")
            return

        # logger.info(f"Listing all .{args.format} files in {directory}...")
        # for f in files:
        #   logger.info(f"\t{f}")

        if args.format == "cha":
            chatparser.chat2conllu(files, args.clear_mor, args.clear_gra, args.clear_misc)
        elif args.format == "conllu":
            conlluparser.conllu2chat(files, args.generate_mor, args.generate_gra, args.generate_cnl, args.generate_pos)
    end_time = time.time()
    logger.info(f"It took {end_time-start_time:.2f} secods.")

if __name__ == "__main__":
    main()
