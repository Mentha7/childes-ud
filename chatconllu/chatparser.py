"""
Utilities to parse .cha files.
"""

from pathlib import Path

from logger import logger

BROWN_EVE = "/home/jingwen/Desktop/thesis/Brown"
FILE = "010600a.cha"

def list_files(dir):
    return (x for x in Path(dir).glob("**/*.cha") if not x.name.startswith("._"))

def read_file(filename):
    """ Read file line by line, if line:
        - starts with @
        - starts with *
        - starts with %
        note: field and value are separated by tabs
    """
    pass

if __name__ == "__main__":
    logger.info(f"listing all .cha files in {BROWN_EVE}...")
    files = list_files(BROWN_EVE)
    try:
        while True:
            i = next(files)
            print(i)
    except StopIteration:
        pass

    # read file
    logger.info(f"reading {FILE}...")
