from __future__ import annotations

import argparse
import html
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

try:
    from pymorphy3 import MorphAnalyzer
except ImportError as error:  # pragma: no cover
    raise SystemExit(
        "Dependency 'pymorphy3' is not installed. Run: pip install -r requirements.txt"
    ) from error

TOKEN_PATTERN = re.compile(r"[A-Za-zА-Яа-яЁё]+(?:-[A-Za-zА-Яа-яЁё]+)*")
IGNORED_PARTS_OF_SPEECH = {"PREP", "CONJ", "PRCL", "NUMR"}
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
        description="Tokenize saved documents and group page tokens by lemmas."
    )
    parser.add_argument(
        "--pages-dir",
        type=Path,
        default=Path("crawl_output/pages"),
        help="Directory with source documents (.txt/.html/.htm/.md).",
    )
    parser.add_argument(
        "--tokens-dir",
        type=Path,
        default=Path("tokens_by_page"),
        help="Directory where token files per source page will be written.",
    )
    parser.add_argument(
        "--lemmas-dir",
        type=Path,
        default=Path("lemmas_by_page"),
        help="Directory where lemma files per source page will be written.",
    )
    parser.add_argument(
        "--combined-tokens",
        type=Path,
        default=Path("tokens.txt"),
        help="Path for combined token list from all pages.",
    )
    parser.add_argument(
        "--combined-lemmas",
        type=Path,
        default=Path("lemmatized_tokens.txt"),
        help="Path for combined lemma-to-token mapping from all pages.",
    )
    # Backward-compatible aliases.
    parser.add_argument("--input-dir", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--output-dir", type=Path, help=argparse.SUPPRESS)
    return parser.parse_args()


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    input_dir = args.input_dir if args.input_dir else args.pages_dir
    if args.output_dir:
        return input_dir, args.output_dir / "tokens", args.output_dir / "lemmas"
    return input_dir, args.tokens_dir, args.lemmas_dir


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
    if len(letters_only) < 2:
        return False
    if not letters_only.isalpha():
        return False
    has_cyrillic = any(("а" <= char <= "я") or char == "ё" for char in letters_only)
    has_latin = any("a" <= char <= "z" for char in letters_only)
    if has_cyrillic and has_latin:
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
    path.write_text("".join(f"{token}\n" for token in tokens), encoding="utf-8")


def write_lemmas(path: Path, lemmas: dict[str, list[str]]) -> None:
    path.write_text(
        "".join(f"{lemma} {' '.join(tokens)}\n" for lemma, tokens in lemmas.items()),
        encoding="utf-8",
    )


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


def process_documents(
    input_dir: Path,
    tokens_dir: Path,
    lemmas_dir: Path,
    combined_tokens_path: Path,
    combined_lemmas_path: Path,
) -> None:
    morph = MorphAnalyzer()
    tokens_dir.mkdir(parents=True, exist_ok=True)
    lemmas_dir.mkdir(parents=True, exist_ok=True)

    all_tokens: set[str] = set()
    all_lemmas: dict[str, set[str]] = defaultdict(set)

    for source_path in get_input_files(input_dir):
        raw_text = read_document(source_path)
        visible_text = extract_visible_text(raw_text, source_path.suffix)
        tokens = tokenize(visible_text, morph)
        lemma_groups = group_tokens_by_lemmas(tokens, morph)

        token_output = tokens_dir / source_path.name
        lemma_output = lemmas_dir / source_path.name
        write_tokens(token_output, tokens)
        write_lemmas(lemma_output, lemma_groups)

        all_tokens.update(tokens)
        for lemma, lemma_tokens in lemma_groups.items():
            all_lemmas[lemma].update(lemma_tokens)

        print(
            "Processed:",
            source_path,
            "->",
            token_output,
            "and",
            lemma_output,
        )

    combined_tokens = sorted(all_tokens)
    combined_lemma_map = {lemma: sorted(tokens) for lemma, tokens in sorted(all_lemmas.items())}
    write_tokens(combined_tokens_path, combined_tokens)
    write_lemmas(combined_lemmas_path, combined_lemma_map)
    print("Combined tokens file:", combined_tokens_path)
    print("Combined lemmas file:", combined_lemmas_path)


def main() -> None:
    args = parse_args()
    input_dir, tokens_dir, lemmas_dir = resolve_paths(args)
    process_documents(
        input_dir=input_dir,
        tokens_dir=tokens_dir,
        lemmas_dir=lemmas_dir,
        combined_tokens_path=args.combined_tokens,
        combined_lemmas_path=args.combined_lemmas,
    )


if __name__ == "__main__":
    main()
