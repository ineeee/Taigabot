import re


# smush multiple spaces into one
def compress_whitespace(text: str) -> str:
    whitespace = re.compile(r"\s+")
    return whitespace.sub(' ', text).strip()


# replaces newlines (unix or windows) with a space
def remove_newlines(text: str, separator: str = ' ') -> str:
    lines = re.compile(r"[\r\n]+")
    return lines.sub(separator, text).strip()
