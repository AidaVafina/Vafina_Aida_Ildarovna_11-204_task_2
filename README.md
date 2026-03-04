# Токенизация и лемматизация документов (`2_task`)

Решение задания по предмету «Информационный поиск».

## Что делает скрипт

1. Извлекает токены из каждого файла выкачки.
2. Удаляет дубликаты (в рамках страницы), числа, смешанные буквенно-цифровые и мусорные токены.
3. Удаляет служебные части речи (предлоги, союзы, частицы, числительные).
4. Группирует токены по леммам с помощью `pymorphy3`.
5. Формирует отдельные файлы токенов и лемм для каждого входного файла.

## Структура

```text
.
├── crawl_output/pages/        # входные документы
├── tokens_by_page/            # токены по страницам
├── lemmas_by_page/            # леммы по страницам
├── tokens.txt                 # общий список токенов по всем страницам
├── lemmatized_tokens.txt      # общий список лемм по всем страницам
├── tokenize_and_lemmatize.py  # точка входа
└── src/main.py                # основная логика
```

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 tokenize_and_lemmatize.py
```

## Формат файлов

1. `tokens_by_page/*.txt`  
`<токен>\n`

2. `lemmas_by_page/*.txt`  
`<лемма> <токен1> <токен2> ... <токенN>\n`

## Соответствие файлов

- `crawl_output/pages/lemmas_1.txt` -> `tokens_by_page/lemmas_1.txt` + `lemmas_by_page/lemmas_1.txt`
- `crawl_output/pages/lemmas_2.txt` -> `tokens_by_page/lemmas_2.txt` + `lemmas_by_page/lemmas_2.txt`
- `crawl_output/pages/tokens_1.txt` -> `tokens_by_page/tokens_1.txt` + `lemmas_by_page/tokens_1.txt`

Преподаватель может проверить результат без запуска кода, так как выходные файлы уже находятся в репозитории.
