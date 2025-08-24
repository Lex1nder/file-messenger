from flask import Flask, request, jsonify, send_file
import os
import uuid
import tempfile

app = Flask(__name__)

# Хранилище файлов (в реальном приложении это будет база данных)
files_storage = {}

@app.route('/upload', methods=['POST'])
def upload_file():
    """Загружает файл и возвращает код"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Генерируем уникальный код
    code = str(uuid.uuid4())[:8].upper()
    
    # Сохраняем файл
    filename = file.filename
    file_path = os.path.join(tempfile.gettempdir(), f"{code}_{filename}")
    file.save(file_path)
    
    # Сохраняем информацию о файле
    files_storage[code] = {
        'filename': filename,
        'path': file_path,
        'size': os.path.getsize(file_path)
    }
    
    print(f"File uploaded: {filename} -> Code: {code}")
    return jsonify({'code': code, 'filename': filename})

@app.route('/status/<code>')
def file_status(code):
    """Проверяет статус файла"""
    if code not in files_storage:
        return jsonify({'error': 'File not found'}), 404
    
    file_info = files_storage[code]
    return jsonify({
        'filename': file_info['filename'],
        'size': file_info['size'],
        'exists': True
    })

@app.route('/file/<code>')
def download_file(code):
    """Скачивает файл по коду"""
    if code not in files_storage:
        return jsonify({'error': 'File not found'}), 404
    
    file_info = files_storage[code]
    return send_file(
        file_info['path'],
        as_attachment=True,
        download_name=file_info['filename']
    )

@app.route('/')
def index():
    """Простая страница для тестирования"""
    return '''
    <h1>File Messenger Test Server</h1>
    <p>Этот сервер используется для тестирования Android приложения.</p>
    <p>Для загрузки файла используйте POST /upload</p>
    <p>Для скачивания используйте GET /file/&lt;code&gt;</p>
    '''

if __name__ == '__main__':
    print("Запуск тестового сервера на http://localhost:5000")
    print("Для тестирования Android приложения измените IP в main.py на ваш IP адрес")
    app.run(host='0.0.0.0', port=5000, debug=True) 