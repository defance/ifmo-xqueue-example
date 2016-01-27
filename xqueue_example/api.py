# -*- coding=utf-8 -*-

from xqueue_example import settings
from xqueue_example import utils


def login(session, username, password):

    # URL логина
    url_login = settings.XQUEUE_INTERFACE['url'] + settings.XQUEUE_URLS['login']

    # Пытаемся залогиниться
    response = session.post(
        url_login,
        {
            'username': username,
            'password': password
        }
    )

    # Поднимаем исключение, если что-то пошло не так
    response.raise_for_status()

    return utils.parse_xreply(response.content)


def get_queue_length(session, queue_name):

    url_get_len = settings.XQUEUE_INTERFACE['url'] + settings.XQUEUE_URLS['get_len']

    return utils.xqueue_get(session, url_get_len, {'queue_name': queue_name})


def get_submission(session, queue_name):

    url_get_submission = settings.XQUEUE_INTERFACE['url'] + settings.XQUEUE_URLS['get_submission']

    return utils.xqueue_get(session, url_get_submission, {'queue_name': queue_name})


def put_result(session, data):

    url_put_result = settings.XQUEUE_INTERFACE['url'] + settings.XQUEUE_URLS['put_result']

    return utils.xqueue_post(session, url_put_result, data)



