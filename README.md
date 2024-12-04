# Мессенджер
## Технологии
1. Redis
2. Python Tornado


## Развертывание
1. Клонирование репозитория
```bash
git clone https://github.com/vkkuznetsov/OROPO_lab9.git
cd OROPO_lab9
```

2. Создание виртуального окружения
```bash
python3 -m venv venv
```
3. Активирование венв
```bash
source venv/bin/activate #linux
или
.\venv\Scripts\activate #windows
```
3. Установка зависимостей
```bash
pip install -r req.txt 
```
4. Проверка конфигурации (config/settings.yml)  
Укажите хост и порт на котором запустится Мессенджер, и укажите хост и порт на котором работает Redis  
По дефолту это localhost:8000 и localhost:6369  
Если редиса нет то на windows ставится через wsl
```bash
sudo apt install redis-server 
```
На Linux эта же команда
4. Запуск приложения
```bash
python main.py
```
