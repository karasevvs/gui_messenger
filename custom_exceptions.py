class ErrorPortOutOfRange(Exception):
    def __str__(self):
        return 'В качестве порта может быть указано только число в диапазоне от 1024 до 65535'


class ErrorIncorrectData(Exception):
    def __str__(self):
        return 'Получены некорректные данные'


class ErrorClientMode(Exception):
    def __str__(self):
        return 'Киент запущен с недопустимым режимом выполнения'


class ErrorNoResponseInServerMessage(Exception):
    def __str__(self):
        return 'Получено некорректное сообщение от сервера (отсутствует поле "response")'