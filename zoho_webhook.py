"""
Webhook receiver для Zoho Forms
Слухає на localhost:5000, отримує дані форми, обробляє їх через PDO pipeline
"""

import json
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import sys

PORT = 5000
PDO_DIR = Path(__file__).parent


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/webhook':
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            # Zoho Forms відправляє JSON або form data
            data = json.loads(body) if body else {}
            print(f'\n📝 Отримано форму від Zoho:')
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # Обробити дані
            process_form_submission(data)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        except Exception as e:
            print(f'❌ Помилка: {e}')
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def log_message(self, format, *args):
        print(f'[{self.address_string()}] {format % args}')


def process_form_submission(data):
    """
    Обробити дані форми і запустити PDO pipeline.

    Очікується структура:
    {
        'name': 'Ім\'я Прізвище По-батькові',
        'answers': {
            'q1': 2,
            'q2': 3,
            ...
        }
    }
    """
    print('\n⚙️  Обробляю дані...')

    # Витягти ім'я та відповіді
    name = data.get('name', 'TestUser')
    answers = data.get('answers', {})

    if not answers:
        print('❌ Немає відповідей у формі')
        return

    print(f'👤 Клієнт: {name}')
    print(f'📊 Відповідей: {len(answers)}')

    # Тут буде логіка: зберегти дані у "Реєстраційний лист.docx"
    # та запустити pdo.py
    # TODO: Реалізувати збереження у .docx та запуск PDO

    print(f'✅ Дані готові для обробки')
    # Потім: запустити pdo.py


def start_server():
    server = HTTPServer(('localhost', PORT), WebhookHandler)
    print(f'\n🚀 Webhook server слухає на http://localhost:{PORT}/webhook')
    print('Введіть цю URL в Zoho Forms → Integrations → Webhooks')
    print('\nЧекаю на форми...\n')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n\n👋 Server зупинений')
        server.shutdown()


if __name__ == '__main__':
    start_server()
