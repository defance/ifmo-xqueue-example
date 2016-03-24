# -*- coding=utf-8 -*-

from xqueue_example import settings, utils, core

import logging
import time
import urllib2

import xqueue_api

log = logging.getLogger(__name__)


def main():

    log.info("Start polling")
    while True:

        # Получаем авторизованную сессию
        xsession = xqueue_api.XQueueSession(base_url=settings.XQUEUE_INTERFACE['url'],
                                            username=settings.XQUEUE_INTERFACE['login'],
                                            password=settings.XQUEUE_INTERFACE['password'],
                                            queue=settings.XQUEUE_INTERFACE['queue'],
                                            autoconnect=True)

        # Получаем количество элементов в очереди на данный момент
        (queue_len_result, queue_len) = xsession.get_len()

        # И все их обрабатываем по очереди, пока можем
        while queue_len_result and queue_len:

            log.info("Getting submission")

            # Получаем очередное решение из очереди
            (submission_result, submission) = xsession.get_submission()

            # Если не удалось получить решение на проверку, заканчиваем
            if not submission_result:
                break

            submission = utils.parse_submission(submission)
            submission_data = submission['body']
            submission_head = submission['header']

            if submission['file']:
                submission_file = submission['file'].items()[0]
                student_response = urllib2.urlopen(submission_file[1]).read()
                student_response = student_response.decode('utf-8')
            else:
                student_response = submission_data['student_response']

            # Оцениваем решение пользователя
            (grade, message) = core.grade(
                student_response,
                submission_data['grader_payload']
            )

            response = utils.create_xobject(
                submission_head['submission_id'], submission_head['submission_key'],
                grade >= 1, grade, message,
                "demo_grader"
            )
            response = utils.serialize_xobject(response)

            (put_result, put_message) = xsession.put_result(response)

            log.info("Submission graded")

            queue_len -= 1

        # Закрываем сессию
        xsession.logout()

        # Отдыхаем
        log.info("Empty queue, will now sleep, re-poll in 5s...")
        time.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
