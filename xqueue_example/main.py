# -*- coding=utf-8 -*-

from xqueue_example import settings, utils, api, api_utils, core

import logging
import time
import urllib2

log = logging.getLogger(__name__)


def main():

    log.info("Start polling")
    while True:

        # Получаем авторизованную сессию
        session = api_utils.xqueue_login()

        # Получаем количество элементов в очереди на данный момент
        (queue_len_result, queue_len) = api.get_queue_length(
            session,
            settings.XQUEUE_INTERFACE['queue']
        )

        # И все их обрабатываем по очереди, пока можем
        while queue_len_result and queue_len:

            log.info("Getting submission")

            # Получаем очередное решение из очереди
            (submission_result, submission) = api.get_submission(
                session,
                settings.XQUEUE_INTERFACE['queue']
            )

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

            (put_result, put_message) = api.put_result(session, response)

            log.info("Submission graded")

            queue_len -= 1

        # Закрываем сессию
        session.close()

        # Отдыхаем
        log.info("Empty queue, will now sleep, re-poll in 5s...")
        time.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
