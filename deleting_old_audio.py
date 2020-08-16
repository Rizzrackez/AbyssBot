import os
import datetime


def modification_date(filename):
    """Возвращает дату и время создания файла формата {YYYY-MM-DD HH:MM:SS}."""
    t = os.stat(filename)[9]
    return datetime.datetime.fromtimestamp(t)


for file in os.listdir("music/"):
    """Удаление всех файлов, которые существуют более 60 минут, из директории music."""
    difference_in_time = datetime.datetime.now() - modification_date(f'music/{file}')
    if difference_in_time.total_seconds() > 3600:
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'music/{file}')
        os.remove(path)

