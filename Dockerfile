FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    python3 python3-pip git wget unzip \
    build-essential libssl-dev libffi-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    zlib1g-dev libgstreamer1.0-dev gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly gstreamer1.0-tools \
    cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng-dev \
    libgirepository1.0-dev openjdk-8-jdk

# Установка Buildozer
RUN pip3 install buildozer

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY . .

# Команда по умолчанию
CMD ["buildozer", "android", "debug"] 