# импортируем библиотеки
from flask import Flask, request
import logging
import poems

# библиотека, которая нам понадобится для работы с JSON
import json

# создаём приложение
# мы передаём __name__, в нём содержится информация,
# в каком модуле мы находимся.
# В данном случае там содержится '__main__',
# так как мы обращаемся к переменной из запущенного модуля.
# если бы такое обращение, например, произошло внутри модуля logging,
# то мы бы получили 'logging'
app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Создадим словарь, чтобы для каждой сессии общения с навыком хранились
# подсказки, которые видел пользователь.
# Это поможет нам немного разнообразить подсказки ответов
# (buttons в JSON ответа).
# Когда новый пользователь напишет нашему навыку, то мы сохраним
# в этот словарь запись формата
# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!"]}
# Такая запись говорит, что мы показали пользователю эти три подсказки.
# Когда он откажется купить слона,
# то мы уберем одну подсказку. Как будто что-то меняется :)
sessionStorage = {}


@app.route('/post', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
# Внутри функции доступен request.json - это JSON,
# который отправила нам Алиса в запросе POST
def main():
    logging.info('Request: %r', request.json)

    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом при помощи библиотеки json
    # преобразуем в JSON и отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        },
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз

        sessionStorage[user_id] = {
            'suggests': [
                "Давай стих",
            ],
            'last_poems': []
        }
        # Заполняем текст ответа
        res['response']['text'] = 'Привет! Я умею генерировать стихи! Для активации скажи "давай стих".'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Сюда дойдем только, если пользователь не новый,
    # и разговор с Алисой уже был начат
    # Обрабатываем ответ пользователя.
    # В req['request']['original_utterance'] лежит весь текст,
    # что нам прислал пользователь
    if req['request']['original_utterance'].lower() in [
        'давай стих',
        'давай',
        'стих',
        'ещё!',
        'ещё',
        'еше',
        'еше!',
        'еще!',
        'еще'
    ]:
        # Пользователь согласился
        poem = poems.get(last_poems=sessionStorage[user_id].get('last_poems', []))

        res['response']['text'] = poem['text']
        sessionStorage[user_id]['last_poems'] = sessionStorage[user_id].get('last_poems', []) + [poem['id']]

        sessionStorage[user_id].get('suggests', []).append('Ещё!')
        sessionStorage[user_id].get('suggests', []).append('Хватит')

    elif req['request']['original_utterance'].lower() in [
        'стоп',
        'хватит',
        'хватит.',
        'стоп.',
        'остановись',
        'остановись.'
    ]:
        res['response']['text'] = 'Хорошо'
        res['response']['end_session'] = True

        sessionStorage[user_id]['suggests'] = ["Давай стих",]
    else:
        # Если нет
        res['response']['text'] = 'Не понимаю'
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in set(session['suggests'])
    ]

    if len(suggests) > 1:
        suggests = suggests[:-1]
        suggests = list(reversed(suggests))

    session['suggests'] = session['suggests']
    sessionStorage[user_id] = session

    return suggests


if __name__ == '__main__':
    app.run()
