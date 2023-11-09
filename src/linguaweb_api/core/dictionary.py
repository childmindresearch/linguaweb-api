"""This module contains the dictionary file reader."""
import functools
import pathlib
import secrets


@functools.lru_cache
def read_words() -> list[str]:
    """Reads the words from the dictionary file."""
    dictionary_file = (
        pathlib.Path(__file__).parent.parent / "data" / "allowed_words.txt"
    )

    with dictionary_file.open() as file:
        return file.read().splitlines()


def get_random_word() -> str:
    """Returns a random word from the dictionary file."""
    words = read_words()
    return secrets.choice(words)
