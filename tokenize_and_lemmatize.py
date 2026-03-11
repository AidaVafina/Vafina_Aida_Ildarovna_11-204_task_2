from __future__ import annotations

import argparse
import html
import inspect
import re
import shutil
import subprocess
import sys
from collections import defaultdict, namedtuple
from pathlib import Path
from typing import Iterable


# регулярные выражения для очистки HTML и выделения токенов
SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b.*?>.*?</\1>", re.IGNORECASE | re.DOTALL)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
TOKEN_RE = re.compile(r"[а-яё]+(?:-[а-яё]+)?", re.IGNORECASE)


# базовый набор русских стоп-слов (включая многие предлоги/союзы/частицы)
STOPWORDS = {
    "а", "без", "более", "бы", "был", "была", "были", "было", "быть", "в", "вам", "вас", "весь",
    "во", "вот", "все", "всё", "всего", "всех", "вы", "где", "да", "даже", "для", "до", "его",
    "ее", "её", "если", "есть", "еще", "ещё", "же", "за", "здесь", "и", "из", "или", "им", "их",
    "к", "как", "ко", "когда", "кто", "ли", "либо", "мне", "может", "мы", "на", "над", "надо",
    "наш", "не", "него", "нее", "неё", "нет", "ни", "них", "но", "ну", "о", "об", "однако", "он",
    "она", "они", "оно", "от", "очень", "по", "под", "при", "с", "со", "так", "также", "такой",
    "там", "те", "тем", "то", "того", "тоже", "той", "только", "том", "ты", "у", "уже", "хотя",
    "чего", "чей", "чем", "что", "чтобы", "чье", "чьё", "эта", "эти", "это", "я",
}

SUPPORTED_SUFFIXES = {".txt", ".text", ".md", ".html", ".htm", ".pdf", ".docx"}


def patch_inspect_getargspec() -> None:
    if hasattr(inspect, "getargspec"):
        return

    ArgSpec = namedtuple("ArgSpec", "args varargs keywords defaults")

    def getargspec(func):
        spec = inspect.getfullargspec(func)
        return ArgSpec(spec.args, spec.varargs, spec.varkw, spec.defaults)

    inspect.getargspec = getargspec  # type: ignore[attr-defined]


def get_morph_analyzer():
    """возвращает MorphAnalyzer или None, если библиотека недоступна."""
    patch_inspect_getargspec()

    try:
        import pymorphy3  # type: ignore

        return pymorphy3.MorphAnalyzer()
    except Exception:
        pass

    try:
        import pymorphy2  # type: ignore

        return pymorphy2.MorphAnalyzer()
    except Exception:
        return None


def clean_html(raw_html: str) -> str:
    """удаляет script/style/comments/tags и нормализует пробелы."""
    text = SCRIPT_STYLE_RE.sub(" ", raw_html)
    text = COMMENT_RE.sub(" ", text)
    text = TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def extract_tokens(text: str) -> list[str]:
    """извлекает словарные токены (кириллица, с опциональным дефисом)."""
    return [token.lower() for token in TOKEN_RE.findall(text)]


def token_is_valid(token: str) -> bool:
    """отбрасывает слишком короткие токены и явные стоп-слова."""
    if len(token) < 2:
        return False
    if token in STOPWORDS:
        return False
    return True


def lemmatize_tokens(tokens: Iterable[str], morph):
    """
    возвращает:
    - список финальных токенов (после морфологических фильтров);
    - словарь lemma -> set(tokens).
    """
    filtered_tokens: set[str] = set()
    lemma_to_tokens: dict[str, set[str]] = defaultdict(set)

    # обрабатываем уникальные токены, чтобы не лемматизировать повторно
    for token in sorted(set(tokens)):
        if not token_is_valid(token):
            continue

        lemma = token
        pos = None

        if morph is not None:
            parsed = morph.parse(token)[0]
            lemma = parsed.normal_form
            pos = parsed.tag.POS

        # убираем союзы, предлоги и числительные
        if pos in {"CONJ", "PREP", "NUMR"}:
            continue

        # дополнительно фильтруем по лемме стоп-слов
        if lemma in STOPWORDS:
            continue

        filtered_tokens.add(token)
        lemma_to_tokens[lemma].add(token)

    return sorted(filtered_tokens), lemma_to_tokens


def write_tokens(tokens: list[str], output_path: Path) -> None:
    output_path.write_text("\n".join(tokens) + ("\n" if tokens else ""), encoding="utf-8")


def write_lemmas(lemma_to_tokens: dict[str, set[str]], output_path: Path) -> None:
    lines = []
    for lemma in sorted(lemma_to_tokens):
        token_list = sorted(lemma_to_tokens[lemma])
        lines.append(f"{lemma} {' '.join(token_list)}")
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def read_text_file(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "cp1251", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def extract_text_from_pdf(path: Path) -> str:
    try:
        from pdfminer.high_level import extract_text  # type: ignore

        return extract_text(str(path))
    except Exception:
        pass

    if shutil.which("pdftotext"):
        try:
            result = subprocess.run(
                ["pdftotext", "-layout", str(path), "-"],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout
        except Exception as exc:
            raise RuntimeError(f"Не удалось извлечь текст из PDF {path}: {exc}") from exc

    raise RuntimeError(
        "Не найден способ извлечения текста из PDF. "
        "Установите pdfminer.six или poppler (pdftotext)."
    )


def extract_text_from_docx(path: Path) -> str:
    try:
        import docx  # type: ignore

        doc = docx.Document(str(path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    except Exception:
        pass

    try:
        import docx2txt  # type: ignore

        return docx2txt.process(str(path)) or ""
    except Exception as exc:
        raise RuntimeError(
            f"Не удалось извлечь текст из DOCX {path}. "
            "Установите python-docx или docx2txt."
        ) from exc


def extract_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".html", ".htm"}:
        return read_text_file(path)
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix == ".docx":
        return extract_text_from_docx(path)
    return read_text_file(path)


def collect_input_files(paths: list[str], default_dir: Path) -> list[Path]:
    if paths:
        roots = [Path(p).expanduser() for p in paths]
    else:
        roots = [default_dir]

    files: list[Path] = []
    for root in roots:
        if not root.exists():
            raise FileNotFoundError(f"Не найден путь: {root}")
        if root.is_dir():
            for candidate in sorted(root.rglob("*")):
                if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_SUFFIXES:
                    files.append(candidate)
        elif root.is_file():
            if root.suffix.lower() in SUPPORTED_SUFFIXES:
                files.append(root)
            else:
                raise ValueError(f"Неподдерживаемый формат: {root}")
        else:
            raise ValueError(f"Неподдерживаемый путь: {root}")

    if not files:
        raise FileNotFoundError("Не найдено ни одного подходящего файла для обработки.")

    return files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Токенизация документов и группировка токенов по леммам."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Файлы или папки с документами. Если не указаны, используется ./documents",
    )
    parser.add_argument(
        "--tokens-out",
        default="tokens.txt",
        help="Файл для списка токенов",
    )
    parser.add_argument(
        "--lemmas-out",
        default="lemmatized_tokens.txt",
        help="Файл для списка лемм и токенов",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    default_dir = project_root / "documents"

    input_files = collect_input_files(args.inputs, default_dir)
    morph = get_morph_analyzer()

    all_tokens: list[str] = []
    for path in input_files:
        raw_text = extract_text_from_file(path)
        clean_text = clean_html(raw_text)
        all_tokens.extend(extract_tokens(clean_text))

    tokens, lemma_to_tokens = lemmatize_tokens(all_tokens, morph)

    tokens_out = Path(args.tokens_out).resolve()
    lemmas_out = Path(args.lemmas_out).resolve()

    write_tokens(tokens, tokens_out)
    write_lemmas(lemma_to_tokens, lemmas_out)

    print(f"Документов обработано: {len(input_files)}")
    print(f"Уникальных токенов: {len(tokens)}")
    print(f"Лемм: {len(lemma_to_tokens)}")
    print(f"Файл с токенами: {tokens_out}")
    print(f"Файл с леммами: {lemmas_out}")
    if morph is None:
        print("Внимание: pymorphy не найден, использован упрощённый режим без морфоанализа.")


if __name__ == "__main__":
    main()
