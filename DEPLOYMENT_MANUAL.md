# Deployment Manual

## 1. Системные требования

- Python 3.10+
- (Опционально) `pymorphy3` или `pymorphy2` для морфоанализа
- Для PDF:
  - либо утилита `pdftotext` (из пакета poppler),
  - либо библиотека `pdfminer.six`

## 2. Установка зависимостей

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Если работаете с PDF и нет `pdftotext`, установите `pdfminer.six`:

```bash
pip install pdfminer.six
```

## 3. Подготовка входных документов

1. Поместите документы в папку `documents/` **или**
2. Укажите пути к файлам при запуске скрипта.

Поддерживаемые форматы: `txt`, `html`, `htm`, `pdf`, `docx`.

## 4. Запуск

```bash
python3 tokenize_and_lemmatize.py
```

Или с явными путями:

```bash
python3 tokenize_and_lemmatize.py /path/to/doc1.pdf /path/to/doc2.txt /path/to/folder
```

## 5. Результаты

Скрипт создаёт файлы:
- `tokens.txt`
- `lemmatized_tokens.txt`

## 6. Проверка без запуска

Файлы результатов можно открыть напрямую:
- `tokens.txt`
- `lemmatized_tokens.txt`
