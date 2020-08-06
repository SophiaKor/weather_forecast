import re
import json
import requests
import config
from datetime import date, timedelta
from natasha import LocationExtractor, DatesExtractor
from natasha.markup import format_json
from exceptions import ExternalServiceException, DatesExtractorException, \
    LocationExtractorException


def form_response(city, data):
    """Формирование ответа для пользователя. """
    try:
        return f"Сейчас в {city}:\nтемпература: {data['current']['temp_c']} C\n" \
               f"влажность: {data['current']['humidity']} %\nскорость ветра: {data['current']['wind_kph']} км/ч\n" \
               f"давление: {data['current']['pressure_mb'] // 1.333} мм\n{data['current']['condition']['text']}"
    except (KeyError, TypeError, AttributeError):
        raise ExternalServiceException("Response Error")


def get_weather(city):
    """Обращение к внешнему сервису на получение погоды. """
    params = {
        'q': city,
        'key': config.API_WEATHER_KEY,
        'lang': 'ru'
    }
    try:
        res = requests.get(config.API_WEATHER_URL, params=params)
    except requests.exceptions.RequestException as e:
        raise ExternalServiceException("Request Error")

    try:
        data = res.json()
    except json.decoder.JSONDecodeError:
        raise ExternalServiceException("Response Error")

    return form_response(city=city, data=data)


def get_location(query):
    """Получение города из реплики. """
    loc_extractor = LocationExtractor()
    city = loc_extractor(query)
    try:
        fact_city = city[0].fact.as_json
    except IndexError:
        raise LocationExtractorException("Location Extractor Error")

    loc = format_json(fact_city)
    loc = re.findall(r"\: \"(\w+)", loc)
    return loc


def get_date(query):
    """Получение даты из реплики. """
    dates_dict = {
        "сегодня": date.today(),
        "завтра": (date.today() + timedelta(1)),
        "послезавтра": (date.today() + timedelta(2)),
        "выходн": date.today() + timedelta(6 - date.today().weekday()),
        "начал": date.today() + timedelta(7 - date.today().weekday()),
        "день победы": date(2020, 5, 9),
        "международный день космоса": date(2020, 5, 21),
        "день сварщика": date(2020, 5, 29),
        "всемирный день молока": date(2020, 6, 1)
    }

    for key in dates_dict:
        if key in query:
            month = dates_dict[key].month
            day = dates_dict[key].day
            return month, day

    date_extractor = DatesExtractor()
    dt = date_extractor(query)

    try:
        fact_date = dt[0].fact.as_json
    except IndexError:
        raise DatesExtractorException("Dates Extractor Error")

    time = format_json(fact_date)
    month = re.findall(r'\"month\"\: (\d+),', time)[0]
    day = re.findall(r'\"day\"\: (\d+),', time)[0]
    return month, day


if __name__ == "__main__":
    while True:
        phrase = input("Ввод: ").lower()
        try:
            location = get_location(phrase)
            asked_month, asked_day = get_date(phrase)
            weather = get_weather(location[0].title())
            print(weather)
        except LocationExtractorException:
            print("Вы не указали город...\nДавайте попробуем еще раз.")
        except DatesExtractorException:
            print("Вы не указали день...\nДавайте попробуем еще раз.")
        except ExternalServiceException:
            print("Упс, возникла ошибка при получении погоды :(\nДавайте попробуем еще раз.")
        except Exception as e:
            print(e)
