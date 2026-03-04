# Release Notes

## v1.1.0 - 2026-03-04

- Добавлены реальные входные документы задания:
  - `data/raw/lemmas_1.txt`
  - `data/raw/lemmas_2.txt`
  - `data/raw/tokens_1.txt`
- Сгенерированы итоговые файлы токенов и лемм для этих документов:
  - `output/tokens/lemmas_1_tokens.txt`
  - `output/tokens/lemmas_2_tokens.txt`
  - `output/tokens/tokens_1_tokens.txt`
  - `output/lemmas/lemmas_1_lemmas.txt`
  - `output/lemmas/lemmas_2_lemmas.txt`
  - `output/lemmas/tokens_1_lemmas.txt`

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
