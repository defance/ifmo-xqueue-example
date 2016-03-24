# -*- coding=utf-8 -*-

import json
import logging
import requests


def log_handler():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    return handler


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