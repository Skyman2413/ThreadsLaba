import datetime
import json
import os
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread, Lock

import worker
from worker import Worker, monitoring_list, queue_to_consume

max_id = 0
sample_queue_element = {
    "org_name": "sampleName",
    "date": "21.04.2023",
    "product_list": [["ProductA", 1, 4059], ["ProductB", 2, 930], ["ProductC", 3, 3444]],
    "state": "Done Successfully/Error",
    "worker": "worker1",
    "id": 1
}


class MyHHTPRequestHandler(BaseHTTPRequestHandler):
    # Обработчик GET запроса. В нашей программе таких будет 2 - просмотреть всю очередь
    # и получить сформированный файл
    def do_GET(self):
        if self.path == "/get_file":
            # Задание для студентов - реализовать обработку получения файла из готовой очереди
            status_code = 200
            status_info = "OK"
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            json_body = {}
            if self.headers["Content-Type"].lower() not in ("text/json", "application/json"):
                status_code = 405
                status_info = "Method Not Allowed"
            try:
                json_body = json.loads(body)

            except Exception as e:
                print(e)
                status_code = 400
                status_info = "Bad Request"
            pass
            if status_code == 200:
                if not os.path.exists(Path(os.getcwd(), "files_to_send", f"{json_body['id']}.xlsx")):
                    status_code = 404
                    status_info = "Not found"
            self.send_response(status_code, status_info)
            self.send_header('Content-type', 'application/xlsx')
            self.send_header('Content-Disposition', f'attachment; filename="{json_body["id"]}.xlsx"')
            self.end_headers()
            if status_code == 200:
                with open(Path(os.getcwd(), "files_to_send", f"{json_body['id']}.xlsx"), 'rb') as file:
                    self.wfile.write(file.read())
        if self.path == "/queue_info":
            pass
            status_code = 200
            status_info = "OK"
            response_body = json.dumps(monitoring_list)
            self.send_response(status_code, status_info)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(response_body, "utf-8"))

    # Обработчик POST запроса для добавления элемента в очередь
    def do_POST(self):
        global max_id
        status_code = 200
        status_info = "OK"

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        response_body = ""
        if self.headers["Content-Type"].lower() not in ("text/json", "application/json"):
            status_code = 405
            status_info = "Method Not Allowed"
        try:
            json_body = json.loads(body)
            max_id = max_id + 1
            id = max_id
            new_element = {"org_name": json_body["org_name"], "date": json_body["date"],
                           "product_list": json_body["product_list"], "state": "new", "worker": "",
                           "id": id}
            # для очереди
            # queue_to_consume.put(new_element)
            response_body = {"id": new_element["id"]}
            response_body = json.dumps(response_body)

            lock = Lock()
            # блокируем словарь для выполнения не атомарных операций
            with lock:
                monitoring_list[id] = new_element
                monitoring_list[id]["created_at"] = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            time.sleep(2)

            # По-хорошему нужно проверить каждый на корректность. Сейчас может возникнуть только KeyError

        except Exception as e:
            print(e)
            status_code = 400
            status_info = "Bad Request"
            new_element = {}
        if len(new_element) == 0:
            response_body = "{}"
        print("Получен элемент\r\n")
        print(str(new_element) + "\r\n")

        # для очереди
        '''self.send_response(status_code, status_info)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(response_body, "utf-8"))'''
        worker.worker_without_thread(item=new_element)
        if not os.path.exists(Path(os.getcwd(), "files_to_send", f"{new_element['id']}.xlsx")):
            status_code = 404
            status_info = "Not found"
        self.send_response(status_code, status_info)
        self.send_header('Content-type', 'application/xlsx')
        self.send_header('Content-Disposition', f'attachment; filename="{new_element["id"]}.xlsx"')
        self.end_headers()
        if status_code == 200:
            with open(Path(os.getcwd(), "files_to_send", f"{new_element['id']}.xlsx"), 'rb') as file:
                self.wfile.write(file.read())


if __name__ == "__main__":
    threads = []
    httpd = HTTPServer(("localhost", 8080), MyHHTPRequestHandler)
    httpd.serve_forever()
    # для очереди
    '''worker_count = 8
    t = Thread(target=httpd.serve_forever)

    for i in range(1, worker_count+1):
        worker = Worker(name=f"Worker{i}")
        threads.append(worker)
    threads.append(t)

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()'''
