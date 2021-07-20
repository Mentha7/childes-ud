"""Helpers.
"""
import sys, os
from typing import List, Tuple, Dict, Union
from pathlib import Path

def list_files(directory: str, format="cha", filename="") -> List['pathlib.PosixPath']:
    """Recursively lists all files ending with the given format in the given directory.

    Parameters:
    -----------
    directory: The directory to recursively search for the files with the given format.
    format: The file format/extension to search for, only "cha" and "conllu" should
            be supplied.
    filename: If specified, matches the file with filename only.

    Return value: A list of filepaths.

    """
    return [x for x in Path(directory).glob(f"**/*{filename}.{format}") if not x.name.startswith("._")]
