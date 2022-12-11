# hw05_final

Это  мой учебный проект от Яндекс.Практикума, в рамках которого я создал веб-проект приложения, в котором пользователи могут оставлять, просматривать и коментировать записи (посты).
### Технологии
Python 3.7
Django 2.2.19
HTML
CSS

### Запуск проекта в dev-режиме
1. Запустите терминал и откройте в нем папку, в которую хотите клонировать проект.
Клонируйте репозиторий и перейдите в него в командной строке:
```
https://github.com/Spacemarine1789/hw05_final.git
```
```
cd hw05_final
```
2. Cоздате и активируйте виртуальное окружение:
```
python3 -m venv env
```
```
source env/bin/activate
```
Если вы пользователь Windows:
```
source env/Scripts/activate
```
```
python3 -m pip install --upgrade pip
```
3. Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
4. Выполните миграции:
```
python3 manage.py makemigrations
python3 manage.py migrate
```
обратите внимание что запускать проект и выполнять миграции необходимо из дериктории, в которой расположен файл manage.py.
5. Запустите проект:
```
python3 manage.py runserver
```
