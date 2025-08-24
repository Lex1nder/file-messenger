#!/usr/bin/env python3
"""
Тестирование системы File Messenger
"""

import requests
import os
import time
import subprocess
import sys
from threading import Thread

def test_server_connection(server_url="http://localhost:5000"):
    """Тестирует подключение к серверу"""
    try:
        response = requests.get(server_url, timeout=5)
        if response.status_code == 200:
            print("✅ Сервер доступен")
            return True
        else:
            print("❌ Сервер недоступен")
            return False
    except:
        print("❌ Не удалось подключиться к серверу")
        return False

def test_file_upload(server_url="http://localhost:5000"):
    """Тестирует загрузку файла"""
    try:
        # Создаем тестовый файл
        test_file = "test_upload.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Тестовый файл для проверки загрузки\n")
            f.write("Строка 2\n")
            f.write("Строка 3\n")
        
        # Загружаем файл
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{server_url}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            code = result['code']
            filename = result['filename']
            print(f"✅ Файл загружен: {filename} -> Код: {code}")
            
            # Удаляем тестовый файл
            os.remove(test_file)
            return code
        else:
            print(f"❌ Ошибка загрузки: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка тестирования загрузки: {e}")
        return None

def test_file_download(server_url="http://localhost:5000", code=None):
    """Тестирует скачивание файла"""
    if not code:
        print("❌ Нет кода для тестирования скачивания")
        return False
    
    try:
        # Проверяем статус файла
        status_url = f"{server_url}/status/{code}"
        response = requests.get(status_url, timeout=5)
        
        if response.status_code == 200:
            file_info = response.json()
            print(f"✅ Файл найден: {file_info['filename']} ({file_info['size']} байт)")
        else:
            print("❌ Файл не найден")
            return False
        
        # Скачиваем файл
        download_url = f"{server_url}/file/{code}"
        response = requests.get(download_url, stream=True, timeout=10)
        
        if response.status_code == 200:
            # Сохраняем скачанный файл
            downloaded_file = f"downloaded_{code}.txt"
            with open(downloaded_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ Файл скачан: {downloaded_file}")
            
            # Проверяем содержимое
            with open(downloaded_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "Тестовый файл" in content:
                    print("✅ Содержимое файла корректно")
                else:
                    print("❌ Содержимое файла некорректно")
            
            # Удаляем скачанный файл
            os.remove(downloaded_file)
            return True
        else:
            print(f"❌ Ошибка скачивания: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования скачивания: {e}")
        return False

def test_kivy_app():
    """Тестирует запуск Kivy приложения"""
    try:
        # Проверяем, что Kivy установлен
        import kivy
        print("✅ Kivy установлен")
        
        # Проверяем основные модули
        from kivy.app import App
        from kivy.uix.button import Button
        print("✅ Основные модули Kivy доступны")
        
        return True
    except ImportError as e:
        print(f"❌ Kivy не установлен: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования Kivy: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование системы File Messenger")
    print("=" * 50)
    
    # Тест 1: Проверка Kivy
    print("\n1. Тестирование Kivy...")
    kivy_ok = test_kivy_app()
    
    # Тест 2: Проверка сервера
    print("\n2. Тестирование сервера...")
    server_ok = test_server_connection()
    
    if not server_ok:
        print("\n⚠️  Сервер не запущен. Запустите: python test_server.py")
        print("   Затем запустите этот тест снова.")
        return
    
    # Тест 3: Загрузка файла
    print("\n3. Тестирование загрузки файла...")
    code = test_file_upload()
    
    if code:
        # Тест 4: Скачивание файла
        print("\n4. Тестирование скачивания файла...")
        download_ok = test_file_download(code=code)
        
        if download_ok:
            print("\n🎉 Все тесты пройдены успешно!")
            print("\n📱 Теперь можете:")
            print("   1. Запустить Android приложение: python main.py")
            print("   2. Использовать код для скачивания: " + code)
            print("   3. Собрать APK: buildozer android debug")
        else:
            print("\n❌ Тест скачивания не пройден")
    else:
        print("\n❌ Тест загрузки не пройден")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 