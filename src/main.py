from __future__ import annotations

import argparse
import html
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

try:
    from pymorphy3 import MorphAnalyzer
except ImportError as error:  # pragma: no cover - dependency check on runtime environment.
    raise SystemExit(
        "Dependency 'pymorphy3' is not installed. Run: pip install -r requirements.txt"
    ) from error

TOKEN_PATTERN = re.compile(r"[A-Za-zА-Яа-яЁё]+(?:-[A-Za-zА-Яа-яЁё]+)*")
IGNORED_PARTS_OF_SPEECH = {"PREP", "CONJ", "PRCL"}
SUPPORTED_EXTENSIONS = {".txt", ".html", ".htm", ".md"}


class VisibleTextExtractor(HTMLParser):
    """Extracts only visible text and skips script/style blocks."""

    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._chunks.append(data)

    def get_text(self) -> str:
        return " ".join(self._chunks)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tokenization and lemmatization for saved documents."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory with source documents (.txt/.html/.htm/.md).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory where token and lemma files will be written.",
    )
    return parser.parse_args()


def read_document(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_visible_text(raw_text: str, suffix: str) -> str:
    if suffix.lower() in {".html", ".htm"}:
        parser = VisibleTextExtractor()
        parser.feed(raw_text)
        parser.close()
        return html.unescape(parser.get_text())
    return raw_text


def normalize_token(token: str) -> str:
    return token.strip("-").lower()


def is_valid_token(token: str) -> bool:
    if not token:
        return False
    if any(char.isdigit() for char in token):
        return False
    letters_only = token.replace("-", "")
    if not letters_only.isalpha():
        return False
    return True


def tokenize(text: str, morph: MorphAnalyzer) -> list[str]:
    unique_tokens: set[str] = set()
    for raw_token in TOKEN_PATTERN.findall(text):
        token = normalize_token(raw_token)
        if not is_valid_token(token):
            continue
        pos = morph.parse(token)[0].tag.POS
        if pos in IGNORED_PARTS_OF_SPEECH:
            continue
        unique_tokens.add(token)
    return sorted(unique_tokens)


def group_tokens_by_lemmas(tokens: list[str], morph: MorphAnalyzer) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for token in tokens:
        lemma = morph.parse(token)[0].normal_form
        grouped[lemma].append(token)
    return {lemma: sorted(values) for lemma, values in sorted(grouped.items())}


def write_tokens(path: Path, tokens: list[str]) -> None:
    lines = [f"{token}\n" for token in tokens]
    path.write_text("".join(lines), encoding="utf-8")


def write_lemmas(path: Path, lemmas: dict[str, list[str]]) -> None:
    lines = [f"{lemma} {' '.join(tokens)}\n" for lemma, tokens in lemmas.items()]
    path.write_text("".join(lines), encoding="utf-8")


def get_input_files(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    files = [
        path
        for path in sorted(input_dir.rglob("*"))
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not files:
        raise FileNotFoundError(
            f"No documents with supported extensions found in: {input_dir}"
        )
    return files


def process_documents(input_dir: Path, output_dir: Path) -> None:
    morph = MorphAnalyzer()
    token_dir = output_dir / "tokens"
    lemma_dir = output_dir / "lemmas"
    token_dir.mkdir(parents=True, exist_ok=True)
    lemma_dir.mkdir(parents=True, exist_ok=True)

    for source_path in get_input_files(input_dir):
        raw_text = read_document(source_path)
        visible_text = extract_visible_text(raw_text, source_path.suffix)
        tokens = tokenize(visible_text, morph)
        lemma_groups = group_tokens_by_lemmas(tokens, morph)

        stem = source_path.stem
        token_output = token_dir / f"{stem}_tokens.txt"
        lemma_output = lemma_dir / f"{stem}_lemmas.txt"
        write_tokens(token_output, tokens)
        write_lemmas(lemma_output, lemma_groups)

        print(
            "Processed:",
            source_path,
            "->",
            token_output,
            "and",
            lemma_output,
        )


def main() -> None:
    args = parse_args()
    process_documents(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
