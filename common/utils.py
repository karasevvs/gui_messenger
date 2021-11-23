"""Утилиты"""

import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
import custom_exceptions
from decos import Log


@Log()
def get_msg(socket):
    """
    Утилита приёма и декодирования сообщения
    принимает байты выдаёт словарь, если приняточто-то другое отдаёт ошибку значения
    :param socket: объект сокета
    :return: словарь
    """

    encoded_response = socket.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise custom_exceptions.ErrorIncorrectData
    raise ValueError


@Log()
def send_msg(socket, message):
    """
    Утилита кодирования и отправки сообщения
    принимает словарь и отправляет его
    :param socket: объект сокета
    :param message: сообщение в виде словаря
    :return: None
    """

    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    socket.send(encoded_message)
