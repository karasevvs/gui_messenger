import argparse
import socket
import sys
import logging
import time
import json
import threading

import custom_exceptions
import common.variables as variables
from common.utils import send_msg, get_msg
from decos import Log

LOG = logging.getLogger('client')
LOG_F = logging.getLogger('client_func')


class Client:
    """
    Класс клиента
    """

    @Log(LOG_F)
    def __init__(self):
        """
        Метод для инициализации
        self.server_port - порт сервера
        self.server_address - адрес сервера
        self.client_name - имя клиента
        self.transport - сокет клиента
        """
        self.server_port, self.server_address, self.client_name = self.get_params()
        self.transport = self.transport_client()

    @Log(LOG_F)
    def create_msg(self, action, message=None, destination=None):
        """
        Метод для создания сообщений
        :param action: тип действия
        :param message: текст сообщения
        :param destination: адресат сообщения
        :return: сообщение в виде словаря
        """
        result_message = {
            variables.ACTION: action,
            variables.TIME: time.time(),
            variables.PORT: self.server_port,
        }

        if action == variables.PRESENCE:
            result_message[variables.USER] = {variables.ACCOUNT_NAME: self.client_name}

        elif action == variables.MESSAGE and message and destination:
            result_message[variables.SENDER] = self.client_name
            result_message[variables.MESSAGE_TEXT] = message
            result_message[variables.DESTINATION] = destination

        elif action == variables.EXIT:
            result_message[variables.ACCOUNT_NAME] = self.client_name

        return result_message

    @Log(LOG_F)
    def server_answer(self):
        """
        Метод для обработки ответа сервера
        :return: ответ сервера в виде строки
        """
        server_message = get_msg(self.transport)
        if variables.RESPONSE in server_message:
            if server_message[variables.RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {server_message[variables.ERROR]}'
        raise custom_exceptions.ErrorNoResponseInServerMessage

    def server_message(self):
        """
        Метод для обработки сообщений с сервера от других клиентов
        :return: None
        """
        while True:
            try:
                server_message = get_msg(self.transport)
                if server_message.get(variables.ACTION) == variables.MESSAGE and \
                        variables.SENDER in server_message and variables.MESSAGE_TEXT in server_message and \
                        server_message.get(variables.DESTINATION) == self.client_name:
                    LOG.debug(f'{self.client_name}: Получено сообщение от {server_message[variables.SENDER]}')
                    print(f'\n<<{server_message[variables.SENDER]}>> : {server_message[variables.MESSAGE_TEXT]}')
                else:
                    LOG.debug(f'{self.client_name}: Получено сообщение от сервера о некорректном запросе')
                    print(f'\nПолучено сообщение от сервера о некорректном запросе: {server_message}')
            except custom_exceptions.ErrorIncorrectData as error:
                LOG.error(f'Ошибка: {error}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                LOG.critical(f'Потеряно соединение с сервером.')
                break

    @Log(LOG_F)
    def send_msg_server(self, to_client, message):
        """
        Метод для отправки сообщений на сервер для других клиентов
        :param to_client: адресат
        :param message: сообщение
        :return: None
        """
        message_to_send = self.create_msg(variables.MESSAGE, message, to_client)
        try:
            send_msg(self.transport, message_to_send)
            LOG.info(f'{self.client_name}: Отправлено сообщение для пользователя {to_client}')
        except Exception:
            LOG.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @Log(LOG_F)
    def transport_client(self):
        """
        Метод для подготовки сокета клиента
        :return: сокет клиента
        """
        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.connect((self.server_address, self.server_port))
        except ConnectionRefusedError:
            LOG.critical(f'Не удалось подключиться к серверу {self.server_address}:{self.server_port}')
            sys.exit(1)
        return transport

    def interface_client(self):
        """
        Метод для взаимодействия клиента с пользователем
        :return: None
        """
        self.help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.send_msg_server(*self.input_msg())
            elif command == 'help':
                self.help()
            elif command == 'exit':
                send_msg(self.transport, self.create_msg(variables.EXIT))
                print('Завершение соединения.')
                LOG.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @Log(LOG_F)
    def send_pres(self):
        """
        Метод для отправки сообщения на сервер.
        :return: True или False
        """
        try:
            send_msg(self.transport, self.create_msg(variables.PRESENCE))
            answer = self.server_answer()
            LOG.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером.')
            return True if answer == '200 : OK' else False
        except json.JSONDecodeError:
            LOG.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except custom_exceptions.ErrorNoResponseInServerMessage as error:
            LOG.error(f'Ошибка сообщения сервера {self.server_address}: {error}')

    def main(self):
        """
        Основной метод для клиента
        :return: None
        """
        print(self.client_name)
        if self.send_pres():
            receiver = threading.Thread(target=self.server_message)
            receiver.daemon = True
            receiver.start()

            user_interface = threading.Thread(target=self.interface_client)
            user_interface.daemon = True
            user_interface.start()
            LOG.debug(f'{self.client_name}: Запущены процессы')

            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break

    @staticmethod
    @Log(LOG_F)
    def help():
        """
        Метод для вывода справки
        """
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    @staticmethod
    @Log(LOG_F)
    def input_msg():
        """
        Метод для получения адресата и сообщения от пользователя
        :return: кортеж строк
        """
        while True:
            to_client = input('Введите имя пользователя-адресата:')
            message = input('Введите сообщение:')
            if to_client.strip() and message.strip():
                break
            else:
                print('Имя пользователя и сообщение не может быть пустым!')
        return to_client, message

    @staticmethod
    @Log(LOG_F)
    def get_params():
        """
        Метод для получения параметров при запуске из комадной строки
        :return: кортеж параметров
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('port', nargs='?', type=int, default=variables.DEFAULT_PORT)
        parser.add_argument('address', nargs='?', type=str, default=variables.DEFAULT_IP_ADDRESS)
        parser.add_argument('-n', '--name', type=str, default='Guest')

        args = parser.parse_args()

        server_port = args.port
        server_address = args.address
        client_name = args.name

        try:
            if not (1024 < server_port < 65535):
                raise custom_exceptions.ErrorPortOutOfRange
        except custom_exceptions.ErrorPortOutOfRange as error:
            LOG.critical(f'Ошибка порта {server_port}: {error}. Соединение закрывается.')
            sys.exit(1)
        return server_port, server_address, client_name


if __name__ == '__main__':
    client = Client()
    client.main()
