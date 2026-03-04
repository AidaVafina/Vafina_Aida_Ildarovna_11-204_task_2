# Deployment Manual

## 1. Предварительные требования

- Python 3.10+
- Git

## 2. Клонирование репозитория

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

Сохраненные документы (txt/html/htm/md) поместить в папку:

```text
data/raw/
```

## 5. Запуск обработки

```bash
python -m src.main --input-dir data/raw --output-dir output
```

## 6. Где смотреть результаты

Для каждого файла из `data/raw/` будут созданы:

- `output/tokens/<source_name>_tokens.txt`
- `output/lemmas/<source_name>_lemmas.txt`

## 7. Проверка без запуска

В репозитории уже есть готовые примеры результатов в папке `output/`.
