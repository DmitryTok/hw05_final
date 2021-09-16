import datetime as dt


def year(request):
    """Добавляет переменную с текущим годом."""
    year = int(dt.datetime.today().strftime("%Y"))
    return {'year': year}
