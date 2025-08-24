from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
import requests
import os
import socket
from threading import Thread
import time

class FileDownloaderApp(App):
    def __init__(self):
        super().__init__()
        self.server_ip = self._get_local_ip()
        self.server_port = 5000
        self.current_download = None
        
    def build(self):
        # Основной контейнер
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Заголовок
        title = Label(
            text='File Messenger',
            size_hint_y=None,
            height=50,
            font_size='24sp',
            bold=True
        )
        main_layout.add_widget(title)
        
        # Информация о сервере
        server_info = Label(
            text=f'Сервер: {self.server_ip}:{self.server_port}',
            size_hint_y=None,
            height=30,
            color=(0.5, 0.5, 0.5, 1),
            font_size='12sp'
        )
        main_layout.add_widget(server_info)
        
        # Поле ввода кода
        code_label = Label(
            text='Введите код файла:',
            size_hint_y=None,
            height=30
        )
        main_layout.add_widget(code_label)
        
        self.code_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=50,
            font_size='18sp',
            hint_text='Например: ABC123'
        )
        main_layout.add_widget(self.code_input)
        
        # Кнопка скачивания
        self.download_btn = Button(
            text='Скачать файл',
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.6, 1, 1),
            font_size='18sp'
        )
        self.download_btn.bind(on_press=self.download_file)
        main_layout.add_widget(self.download_btn)
        
        # Прогресс бар
        self.progress_bar = ProgressBar(
            max=100,
            size_hint_y=None,
            height=30
        )
        main_layout.add_widget(self.progress_bar)
        
        # Статус
        self.status_label = Label(
            text='Готов к загрузке',
            size_hint_y=None,
            height=30,
            color=(0.3, 0.3, 0.3, 1)
        )
        main_layout.add_widget(self.status_label)
        
        # Список загруженных файлов
        files_label = Label(
            text='Загруженные файлы:',
            size_hint_y=None,
            height=30,
            bold=True
        )
        main_layout.add_widget(files_label)
        
        # Контейнер для списка файлов
        self.files_layout = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )
        self.files_layout.bind(minimum_height=self.files_layout.setter('height'))
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.files_layout)
        main_layout.add_widget(scroll_view)
        
        # Загружаем список существующих файлов
        self.load_downloaded_files()
        
        return main_layout
    
    def download_file(self, instance):
        """Загружает файл по коду"""
        code = self.code_input.text.strip()
        if not code:
            self.status_label.text = 'Введите код файла!'
            return
        
        # Запускаем загрузку в отдельном потоке
        Thread(target=self._download_file_thread, args=(code,)).start()
    
    def _download_file_thread(self, code):
        """Загрузка файла в отдельном потоке"""
        try:
            self.status_label.text = 'Подключение к серверу...'
            self.download_btn.disabled = True
            
            # Проверяем доступность файла
            url = f"http://{self.server_ip}:{self.server_port}/status/{code}"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                Clock.schedule_once(lambda dt: self._update_status(f'Файл не найден: {code}'), 0)
                return
            
            file_info = response.json()
            filename = file_info.get('filename', f'file_{code}')
            
            # Начинаем загрузку
            Clock.schedule_once(lambda dt: self._update_status(f'Загрузка {filename}...'), 0)
            
            download_url = f"http://{self.server_ip}:{self.server_port}/file/{code}"
            response = requests.get(download_url, stream=True, timeout=30)
            
            if response.status_code != 200:
                Clock.schedule_once(lambda dt: self._update_status('Ошибка загрузки'), 0)
                return
            
            # Создаем папку для загрузок
            download_dir = self._get_download_dir()
            os.makedirs(download_dir, exist_ok=True)
            
            filepath = os.path.join(download_dir, filename)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            Clock.schedule_once(lambda dt, p=progress: self._update_progress(p), 0)
            
            # Загрузка завершена
            Clock.schedule_once(lambda dt: self._update_status(f'Файл сохранен: {filename}'), 0)
            Clock.schedule_once(lambda dt: self._update_progress(100), 0)
            Clock.schedule_once(lambda dt: self.load_downloaded_files(), 0)
            
        except requests.exceptions.ConnectionError:
            Clock.schedule_once(lambda dt: self._update_status('Не удалось подключиться к серверу'), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._update_status(f'Ошибка: {str(e)}'), 0)
        finally:
            Clock.schedule_once(lambda dt: self._enable_download_button(), 0)
    
    def _update_status(self, text):
        """Обновляет статус в главном потоке"""
        self.status_label.text = text
    
    def _update_progress(self, value):
        """Обновляет прогресс бар в главном потоке"""
        self.progress_bar.value = value
    
    def _enable_download_button(self):
        """Включает кнопку загрузки в главном потоке"""
        self.download_btn.disabled = False
    
    def _get_download_dir(self):
        """Возвращает путь к папке загрузок"""
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            from android.storage import primary_external_storage_path
            
            # Запрашиваем разрешения
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
            
            # Используем папку Downloads
            return os.path.join(primary_external_storage_path(), 'Download')
        else:
            # Для тестирования на ПК
            return os.path.expanduser('~/Downloads')
    
    def load_downloaded_files(self):
        """Загружает список загруженных файлов"""
        # Очищаем список
        self.files_layout.clear_widgets()
        
        download_dir = self._get_download_dir()
        if not os.path.exists(download_dir):
            return
        
        # Получаем список файлов
        files = []
        try:
            for filename in os.listdir(download_dir):
                filepath = os.path.join(download_dir, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    files.append((filename, size))
        except:
            return
        
        # Сортируем по дате изменения (новые сверху)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(download_dir, x[0])), reverse=True)
        
        # Добавляем в интерфейс
        for filename, size in files[:10]:  # Показываем только 10 последних
            file_info = f"{filename} ({self._format_size(size)})"
            file_label = Label(
                text=file_info,
                size_hint_y=None,
                height=40,
                text_size=(Window.width - 40, None),
                halign='left',
                valign='middle'
            )
            self.files_layout.add_widget(file_label)
    
    def _format_size(self, size_bytes):
        """Форматирует размер файла"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _get_local_ip(self):
        """Определяет локальный IP адрес"""
        try:
            # Создаем временное соединение для определения IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def show_error_popup(self, message):
        """Показывает popup с ошибкой"""
        popup = Popup(
            title='Ошибка',
            content=Label(text=message),
            size_hint=(None, None),
            size=(300, 200)
        )
        popup.open()

if __name__ == '__main__':
    FileDownloaderApp().run() 