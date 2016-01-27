# -*- coding=utf-8 -*-

# Настройки доступа к очереди, которую будем периодически пуллить
XQUEUE_INTERFACE = {
    'url': 'http://127.0.0.1:8040/xqueue',
    'login': '',
    'password': '',
    'queue': '',
}

# Относительные адреса api
XQUEUE_URLS = {
    'login': '/login/',
    'get_len': '/get_queuelen/',
    'get_submission': '/get_submission/',
    'put_result': '/put_result/',
}
