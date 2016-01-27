# -*- coding=utf-8 -*-

import json
import logging
import requests


def log_handler():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    return handler


def parse_xreply(xreply):
    """
    Расшифровка ответа от очереди.

    xreply представляет собой сериализированный json-объект:
    {
        'return_code': 0 (успех) или 1 (неудача),
        'content': Сообщение от xqueue
    }
    :param xreply: Сериализированное сообщение
    :return: tuple (success, message)
    """

    # Попытаемся декодировать сообщение
    try:
        xreply = json.loads(xreply)
    except ValueError:
        return False, 'Failed to parse xreply'

    if 'return_code' in xreply:
        return_code = (xreply['return_code'] == 0)
        content = xreply['content']
    elif 'success' in xreply:
        return_code = xreply['success']
        content = xreply
    else:
        return False, "Cannot find a valid success or return code."

    if return_code not in [True, False]:
        return False, 'Invalid return code.'

    return return_code, content


def parse_xobject(xobject, queue_name):
    try:
        xobject = json.loads(xobject)

        header = json.loads(xobject['xqueue_header'])
        header.update({'queue_name': queue_name})
        body = json.loads(xobject['xqueue_body'])
        files = json.loads(xobject['xqueue_files'])

        content = {
            'xqueue_header': json.dumps(header),
            'xqueue_body': json.dumps(body),
            'xqueue_files': json.dumps(files)
        }
    except ValueError or KeyError:
        error_message = "Unexpected reply from server."
        return False, error_message

    return True, content


def parse_submission(xobject):
    """
    Десериализует элемент, полученный из очереди.
    См. прилагаемый документ с описанием данных

    :param xobject:
    :return:
    """
    try:
        xobject = json.loads(xobject)
        return {
            'header': json.loads(xobject['xqueue_header']),
            'body': json.loads(xobject['xqueue_body']),
            'file': json.loads(xobject['xqueue_files']),
        }
    except ValueError or KeyError:
        return None


def xqueue_post(session, url, data, timeout=10):
    """
        Contact grading controller, but fail gently.
        Takes following arguments:
        session - requests.session object
        url - url to post to
        data - dictionary with data to post
        timeout - timeout in settings

        Returns (success, msg), where:
        success: Flag indicating successful exchange (Boolean)
        msg: Accompanying message; Controller reply when successful (string)
    """

    try:
        r = session.post(url, data=data, timeout=timeout, verify=False)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        error_message = 'Could not connect to server at %s in timeout=%f' % (url, timeout)
        # log.error(error_message)
        return False, error_message

    if r.status_code not in [200]:
        error_message = "Server %s returned status_code=%d" % (url, r.status_code)
        # log.error(error_message)
        return False, error_message

    if hasattr(r, "text"):
        text = r.text
    elif hasattr(r, "content"):
        text = r.content
    else:
        error_message = "Could not get response from http object."
        # log.exception(error_message)
        return False, error_message

    return True, text


def xqueue_get(session, url, data=None):
    """
        Send an HTTP get request:
        session: requests.session object.
        url : url to send request to
        data: optional dictionary to send
        """
    # По умолчанию -- пустой блок с данными
    if data is None:
        data = {}

    # Делаем get-запрос
    try:
        r = session.get(url, params=data)
    except requests.exceptions.ConnectionError:
        error_message = "Cannot connect to server."
        return False, error_message

    # Валидируем ответ
    (result, text) = verify_response(r)

    # Если валидация не прошла, возвращаем, что есть
    if not result:
        return result, text

    # В противном случае, парсим ответ
    return parse_xreply(text)


def verify_response(response):
    """
    Проверяет ответ по нескольким параметрам.

    :param response:
    :return:
    """

    # Принимаем только ответы с HTTP 200
    if response.status_code not in [200]:
        return False, 'Unexpected HTTP status code [%d]' % response.status_code

    # Объект должен иметь содержимое: text или content
    if hasattr(response, "text"):
        text = response.text
    elif hasattr(response, "content"):
        text = response.content
    else:
        error_message = "Could not get response from http object."
        return False, error_message

    # Ответ не должен быть пустым и содержать исключительно пробельные символы
    if not isinstance(text, basestring) and not text.strip():
        error_message = "Response is empty or not string at all."
        return False, error_message

    return True, text


def create_xobject(submission_id, submission_key, correct, score, feedback, grader_id):
    """

    :param submission_id: Внутренний идентификатор пользовательского ответа (str)
    :param submission_key: Внутренний идентификатор пользовательского ответа (str)
    :param correct: Признак того, верен ли пользовательский ответ (bool)
    :param score: Оценка за пользовательское решение, от 0 до 1 (float)
    :param feedback: Сообщение пользователю, например, о его ошибке (str)
    :param grader_id: Внутренний идентификатор grader'а (str)
    :return:
    """
    xqueue_header = {
        'submission_id': submission_id,
        'submission_key': submission_key,
    }

    xqueue_body = {
        'msg': feedback,
        'correct': correct,
        'score': score,
        'grader_id' : grader_id,
    }

    return {
        'xqueue_header': xqueue_header,
        'xqueue_body': xqueue_body,
    }


def serialize_xobject(xobject):
    return {
        'xqueue_header': json.dumps(xobject.get('xqueue_header')),
        'xqueue_body': json.dumps(xobject.get('xqueue_body')),
    }