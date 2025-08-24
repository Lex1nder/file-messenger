# File Messenger - Android App

Простое приложение для передачи файлов по локальной сети между ПК и Android устройством.

## Возможности

- Ввод кода файла для скачивания
- Прогресс-бар загрузки
- Список загруженных файлов
- Автоматическое сохранение в папку Downloads
- Работа по локальной сети

## Установка и сборка

### Вариант 1: Сборка на Ubuntu/Linux (рекомендуется)

#### 1. Установка Buildozer

```bash
pip install buildozer
```

#### 2. Установка зависимостей (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3-pip build-essential git python3 python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
sudo apt install -y libgstreamer1.0-dev gstreamer1.0-plugins-{bad,base,good,ugly} gstreamer1.0-tools
sudo apt install -y cmake pkg-config
sudo apt install -y libjpeg-dev libtiff5-dev libjasper-dev libpng-dev
sudo apt install -y libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libavresample-dev libavfilter-dev
sudo apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
sudo apt install -y libgirepository1.0-dev
sudo apt install -y libssl-dev
```

#### 3. Сборка APK

```bash
buildozer android debug
```

APK файл будет создан в папке `bin/`.

### Вариант 2: Сборка в Docker (проще)

#### 1. Создание Dockerfile

```dockerfile
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip git wget unzip \
    build-essential libssl-dev libffi-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    zlib1g-dev libgstreamer1.0-dev gstreamer1.0-plugins-{bad,base,good,ugly} \
    cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng-dev \
    libgirepository1.0-dev

RUN pip3 install buildozer

WORKDIR /app
COPY . .

CMD ["buildozer", "android", "debug"]
```

#### 2. Сборка в Docker

```bash
docker build -t filemessenger-builder .
docker run -v $(pwd):/app filemessenger-builder
```

### 4. Установка на устройство

```bash
adb install bin/filemessenger-0.1-debug.apk
```

## Быстрый старт

### 1. Тестирование системы

```bash
# Запустите тестовый сервер
python test_server.py

# В другом терминале протестируйте систему
python test_system.py
```

### 2. Запуск Android приложения на ПК

```bash
python main.py
```

### 3. Тестирование загрузки файла

```bash
python test_upload.py
```

## Использование

### На Android:
1. Запустите приложение
2. Введите код файла, полученный от ПК приложения
3. Нажмите "Скачать файл"
4. Файл будет сохранен в папку Downloads

### На ПК:
1. Запустите desktop приложение (будет создано позже)
2. Выберите файл для передачи
3. Получите код
4. Передайте код на Android устройство

## Автоматическое определение IP

Приложение автоматически определяет локальный IP адрес и отображает его в интерфейсе.
Для ручного изменения IP отредактируйте переменную `server_ip` в файле `main.py`.

## Тестирование на ПК

Для тестирования без сборки APK:

```bash
pip install -r requirements.txt
python main.py
```

## Структура проекта

- `main.py` - основное приложение
- `buildozer.spec` - конфигурация сборки
- `requirements.txt` - зависимости Python
- `README.md` - документация 