"""Six Words to a Payday -- entry writer.

Writes the six-word entry to $MAKEFUN_OUTPUT_DIR/entry.txt, exactly as
specified, with no trailing newline. Validates the entry before writing
and verifies the bytes on disk afterwards.

Usage: MAKEFUN_OUTPUT_DIR=/path/to/out python3 main.py
"""

import os
import sys

ENTRY = "Payday came. I tipped the server."


class BlankError(ValueError):
    """Entry is empty or only whitespace."""


class MultiLineError(ValueError):
    """Entry must be a single line."""


class ControlCharError(ValueError):
    """Entry must not contain control characters."""


class LengthError(ValueError):
    """Entry must be 1-60 characters."""


class WordCountError(ValueError):
    """Entry must be exactly six words."""


def validate(entry: str) -> None:
    if not entry.strip():
        raise BlankError("entry is blank or only whitespace")
    if entry != entry.strip():
        raise BlankError(
            "entry must not have leading or trailing whitespace"
        )
    if "\n" in entry or "\r" in entry:
        raise MultiLineError("entry must be a single line")
    if any(ord(c) < 32 for c in entry):
        raise ControlCharError(
            "entry must not contain control characters"
        )
    if not (1 <= len(entry) <= 60):
        raise LengthError(
            f"entry must be 1-60 characters, got {len(entry)}"
        )
    words = entry.split()
    if len(words) != 6:
        raise WordCountError(
            f"entry must be exactly six words, got {len(words)}"
        )


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print(
            "error: MAKEFUN_OUTPUT_DIR is not set",
            file=sys.stderr,
        )
        return 2

    try:
        validate(ENTRY)
    except (
        BlankError,
        MultiLineError,
        ControlCharError,
        LengthError,
        WordCountError,
    ) as exc:
        print(f"error: validation failed: {exc}", file=sys.stderr)
        return 2

    data = ENTRY.encode("utf-8")
    if data.decode("utf-8") != ENTRY:
        raise RuntimeError(
            "UTF-8 round-trip verification failed: decoded entry "
            "differs from ENTRY"
        )
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "wb") as fh:
        fh.write(data)

    with open(path, "rb") as fh:
        on_disk = fh.read()
    if on_disk != data:
        raise RuntimeError(
            "read-back verification failed: entry.txt bytes differ "
            "from the expected entry"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
