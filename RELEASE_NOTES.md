# Release Notes

## v1.4.0 - 2026-03-04

- Приведена структура проекта к формату репозитория-образца:
  - входные данные в `crawl_output/pages/`
  - результаты по страницам в `tokens_by_page/` и `lemmas_by_page/`
- Добавлен скрипт запуска `tokenize_and_lemmatize.py` (аналогично образцу).
- Изменен формат имен выходных файлов:
  - для `crawl_output/pages/<name>.txt` создаются
    - `tokens_by_page/<name>.txt`
    - `lemmas_by_page/<name>.txt`
- Добавлены общие агрегированные файлы:
  - `tokens.txt`
  - `lemmatized_tokens.txt`
- Улучшена фильтрация мусорных токенов:
  - исключены смешанные латиница+кириллица токены.

## v1.3.0 - 2026-03-04

- Возвращены исходные названия входных файлов:
  - `data/raw/lemmas_1.txt`
  - `data/raw/lemmas_2.txt`
  - `data/raw/tokens_1.txt`
- Пересобраны выходные файлы строго от исходных имен входных данных:
  - `output/tokens/lemmas_1_tokens.txt`
  - `output/tokens/lemmas_2_tokens.txt`
  - `output/tokens/tokens_1_tokens.txt`
  - `output/lemmas/lemmas_1_lemmas.txt`
  - `output/lemmas/lemmas_2_lemmas.txt`
  - `output/lemmas/tokens_1_lemmas.txt`

## v1.2.0 - 2026-03-04

- Переименованы входные документы в формат страниц выкачки:
  - `data/raw/page_1.txt`
  - `data/raw/page_2.txt`
  - `data/raw/page_3.txt`
- Пересобраны выходные файлы в явном формате «страница -> токены + леммы»:
  - `output/tokens/page_1_tokens.txt`
  - `output/tokens/page_2_tokens.txt`
  - `output/tokens/page_3_tokens.txt`
  - `output/lemmas/page_1_lemmas.txt`
  - `output/lemmas/page_2_lemmas.txt`
  - `output/lemmas/page_3_lemmas.txt`
- Удалены файлы со старыми именами, которые могли мешать проверке.

## v1.0.0 - 2026-03-04

- Реализована токенизация сохраненных документов (`txt/html/htm/md`).
- Добавлена фильтрация:
  - удаление дубликатов;
  - удаление чисел и токенов с цифрами;
  - удаление мусорных фрагментов;
  - удаление союзов, предлогов и частиц.
- Добавлена лемматизация через `pymorphy3`.
- Для каждого входного файла создаются два отдельных файла:
  - список токенов;
  - список лемм с соответствующими токенами.
- Добавлены документы:
  - `README.md`
  - `DEPLOYMENT_MANUAL.md`
  - `RELEASE_NOTES.md`
