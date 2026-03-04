# Deployment Manual

## 1. Требования

- Python 3.10+
- Git

## 2. Клонирование

```bash
git clone https://github.com/AidaVafina/Vafina_Aida_Ildarovna_11-204_task_2.git
cd Vafina_Aida_Ildarovna_11-204_task_2
```

## 3. Установка зависимостей

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Подготовка входных данных

Разместить файлы выкачки в:

```text
crawl_output/pages/
```

## 5. Запуск

```bash
python3 tokenize_and_lemmatize.py
```

## 6. Результаты

Для каждого входного файла `<name>.txt` создаются:

- `tokens_by_page/<name>.txt`
- `lemmas_by_page/<name>.txt`

Также формируются общие файлы:

- `tokens.txt`
- `lemmatized_tokens.txt`

## 7. Проверка без запуска

Готовые файлы `tokens_by_page/`, `lemmas_by_page/`, `tokens.txt`, `lemmatized_tokens.txt` уже добавлены в репозиторий.
