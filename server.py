from queue import Queue
from http.server import HTTPServer, BaseHTTPRequestHandler

from io import BytesIO

queue = Queue()

class MyHHTPRequestHandler(BaseHTTPRequestHandler):

    # Обработчик GET запроса. В нашей программе таких будет 2 - просмотреть всю очередь
    # и получить сформированный файл
    def do_GET(self):
        if self.path == "/get_file":
            # Задание для студентов - реализовать обработку получения файла из готовой очереди
            pass
        if self.path == "/queue_info":
            pass


    # Обработчик POST запроса для добавления элемента в очередь
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = 
