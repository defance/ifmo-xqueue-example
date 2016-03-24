# -*- coding=utf-8 -*-

# Настройки доступа к очереди, которую будем периодически пуллить
XQUEUE_INTERFACE = {
    'url': 'http://127.0.0.1:8040/xqueue',
    'login': '',
    'password': '',
    'queue': '',
}

XQUEUE_INTERFACE = {
    'url': 'http://edx-stage-xqueue.academicmt.ru/xqueue',
    'login': 'programming',
    'password': 'qZY487TJ2aU2uCU',
    'queue': 'programming-test',
}

XQUEUE_INTERFACE = {
    'url': 'http://192.168.33.10:18040/xqueue',
    'login': 'lms',
    'password': 'password',
    'queue': 'test-pull:8040',
}

# Относительные адреса api
XQUEUE_URLS = {
    'login': '/login/',
    'get_len': '/get_queuelen/',
    'get_submission': '/get_submission/',
    'put_result': '/put_result/',
}
