# Python docs parser

Парсер документации Python

____

### Описание:

Парсер осуществляет сбор данных с официального сайта Python, анализирует их  и выдаёт в нужном формате.

У парсера 4 режима работы:
- **whats-new** — получение списка ссылок на статьи об изменениях в версиях Python, заголовков и авторов статей
- **latest-versions** — получение списка ссылок на документацию для всех версий Python, номеров версий и их статусов
- **download** — скачивание архива с документацией в формате pdf для последней версии Python
- **pep** — получение данных о количестве PEP в каждом из возможных статусов и суммарном количестве PEP

Для вывода данных предусмотрено 2 специальных режима:
- **pretty** — вывод в терминал в табличной форме
- **file** — запись результатов работы в файл .csv

### Стек технологий 

![](https://img.shields.io/badge/Python-3.10-black?style=flat&logo=python) 
![](https://img.shields.io/badge/BeautifulSoup-4.9.3-black?style=flat)
![](https://img.shields.io/badge/Requests_cache-0.6.3-black?style=flat)
![](https://img.shields.io/badge/TQDM-4.61.0-black?style=flat&logo=tqdm)
![](https://img.shields.io/badge/PrettyTable-2.1.0-black?style=flat)

### Запуск проекта
- Клонировать репозиторий:
```
git clone https://github.com/Legyan/python_docs_parser
```

- Cоздать и активировать виртуальное окружение:

```
windows: python -m venv env
linux: python3 -m venv env
```

```
windows: source env/Scripts/activate
linux: source env/bin/activate
```

- Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

- Запустить парсер в выбранном режиме работы:

```
python src/main.py {whats-new, latest-versions, download, pep} [-h] [-c] [-o {pretty, file}]
```

Позиционные аргументы {whats-new, latest-versions, download, pep} определяют режима работы парсера.

Опциональный аргумент [-h, --help] вызывает справку о команде запуска парсера.

Опциональный аргумент [-c, --cache] осуществляет очистку кеша перед запуском парсера.

Опциональный аргумент [-o {pretty, file}] определяет режим вывода парсера. При отсутствии аргумента будет осуществлён стандартный вывод в терминал.

### Примеры команд:

- Для запуска парсера в режиме сбора данных о PEP с табличным выводом в треминал:

```
python src/main.py pep -o pretty
```

Ответ парсера в терминале:

```
+-------------+------------+
| Статус      | Количество |
+-------------+------------+
| Active      | 31         |
| Accepted    | 44         |
| Deferred    | 36         |
| Final       | 269        |
| Provisional | 0          |
| Rejected    | 120        |
| Superseded  | 20         |
| Withdrawn   | 55         |
| Draft       | 29         |
| April Fool! | 1          |
| Total       | 605        |
+-------------+------------+
```

- Для запуска парсера в режиме сбора данных о версиях Python c очисткой кеша и стандартным выводом в терминал:

```
python src/main.py latest-versions -c
```

Ответ парсера в терминале:

```
Ссылка на документацию Версия Статус
https://docs.python.org/3.12/ 3.12 in development
https://docs.python.org/3.11/ 3.11 stable
https://docs.python.org/3.10/ 3.10 stable
https://docs.python.org/3.9/ 3.9 security-fixes
https://docs.python.org/3.8/ 3.8 security-fixes
https://docs.python.org/3.7/ 3.7 security-fixes
https://docs.python.org/3.6/ 3.6 EOL
https://docs.python.org/3.5/ 3.5 EOL
https://docs.python.org/2.7/ 2.7 EOL
https://www.python.org/doc/versions/ All versions 
```

- Для запуска парсера в режиме загрузки документации Python:

```
python src/main.py download
```

Архив формата .zip с документацией будет загружен в директорию 'downloads' внутри директории с запускаемым файлом.

- Для запуска парсера в режиме сбора данных об изменениях в версиях Python с выводом в файл:

```
python src/main.py whats-new -o file
```

Файл формата .csv будет загружен в директорию 'results' внутри директории с запускаемым файлом.
