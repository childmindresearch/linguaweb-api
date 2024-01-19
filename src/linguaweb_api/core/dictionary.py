"""This module contains the dictionary file reader."""
import functools
import pathlib


@functools.lru_cache
def read_words() -> list[str]:
    """Reads the words from the dictionary file."""
    dictionary_file = (
        pathlib.Path(__file__).parent.parent / "data" / "default_words.txt"
    )

    with dictionary_file.open() as file:
        return file.read().splitlines()
