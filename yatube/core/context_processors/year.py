from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    today = datetime.now()
    return {
        'year': today.year
    }
