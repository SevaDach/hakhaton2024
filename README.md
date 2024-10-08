# <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Logo_%D0%9C%D0%A2%D0%A1_%282023%29.svg/1200px-Logo_%D0%9C%D0%A2%D0%A1_%282023%29.svg.png" alt="Alt Text" width="40" height="40"> МТС Линк. Использование ИИ в продукте, команда Ш.У.Е. <img src="https://i.ibb.co/FnHRxxT/Vix2-9-HZn-Q.jpg" alt="Vix2-9-HZn-Q" width="40" height="40" border="0" />
**Использование локальной нейронной сети для анализа ответов опроса и генерация облаков слов, основаном на анализе нейронной сети.**
## Содержание
1. [Описание](#описание)
2. [Особенности](#особенности)
3. [Использование](#использование)
4. [Структура проекта](#структура)
5. [Презентация](#презентация)
6. [Авторы](#авторы)

---

## Описание

**SHUE-wordcloud** — это веб-приложение, которое позволяет анализировать данные, полученные из опросов или любым другим путем. Для простоты, результат визуализируется в виде настраемового облака слов, в котором размер слова или фразы напрямую зависит от важности конкретного ответа. Детальный результат доступен в виде круговой диаграммы и `json` таблицы. 

## Особенности

- Поддержка текстовых файлов `.txt` при условии разделения данных строками.
- Чтение таблиц форматов `.xlsx`, `.csv` с возможностью выбора данных по строкам или столбцам.
- Генерация облака слов на основе ответов.
- Асинхронный API для быстрой обработки запросов.
- Самая быстрая и точная нейросеть на базе **ChatGPT 4o**
- Возможность фильтрации ненормативной лексики.
- Различные цветовые схемы для отображения результатов.
- Понятный и дружелюбный интерфейс для пользователей.
- Деалицзация анализа в виде круговой диаграммы.
- Полный список самых популярных результатов в виде `json` таблицы.

## Использование

1. Откройте - [SHUE-wordcloud](https://hack.agicotech.ru/) в браузере.
2. Загрузите файл `.xlsx`, `.csv`, или `.txt`.
3. Выберите стиль оформления облака слов.
4. Выберите строку или столбец для анализа.
5. Система обработает данные с помощью локальной нейронной сети и сгенерирует облако слов.
6. Получите визуализацию и опцию скачать облако в виде изображения.
7. (Опционально) Посмотрите детализацию анализа ваших данных по кнопке `Details`.

<img src="https://i.ibb.co/56MPPDM/2.png" alt="2" border="0">

## Структура

- Корневая директория содержит файлы кода Backend на `Python`.
- Директория `asserts` содержит файлы с необходимыми (и не очень) ресурсами для работы Backend.
- Директория `frontend` содержит статические файлы UI WEB приложения.
- Frontend использует исколючительно HTML + CSS + JS без дополнительных фреймворков и библиотек
- Backend реализует асинхронные эндпоинты с обработкой вычислительных задач в Threads
- Основной запускаемый файл - `main.py`


## Презентация
<a href="https://docs.google.com/presentation/d/1Vp1QekFBLx9jzfZZbDZ-OBhL1xi6SUj5m_1HU6qSUHg">🔗 Google Slides</a>

## Авторы

- [SevaDach](https://github.com/SevaDach)
- [Agicotech](https://github.com/Agicotech)

