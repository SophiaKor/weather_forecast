import asyncio
import aiohttp
import re
import config
from natasha import LocationExtractor
from natasha.markup import format_json
from exceptions import ExternalServiceException, LocationExtractorException


class WeatherForecast:

    @staticmethod
    def form_response(city, data):
        """Формирование ответа для пользователя. """
        try:
            return f"Сейчас в городе {city}:\nтемпература: {data['current']['temp_c']} C\n" \
                   f"влажность: {data['current']['humidity']} %\nскорость ветра: {data['current']['wind_kph']} км/ч\n" \
                   f"давление: {data['current']['pressure_mb'] // 1.333} мм\n{data['current']['condition']['text']}"
        except (KeyError, TypeError, AttributeError):
            raise ExternalServiceException("Response Error")

    @staticmethod
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

    async def get_weather(self, city):
        """Обращение к внешнему сервису на получение погоды. """
        params = {
            'q': city,
            'key': config.API_WEATHER_KEY,
            'lang': 'ru',
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config.API_WEATHER_URL, params=params) as resp:
                    resp = await resp.json()
        except aiohttp.ClientError as e:
            raise ExternalServiceException("Request Error")

        return self.form_response(city=city, data=resp)


async def main():
    """ Запуск сервиса. """
    weather_forecast = WeatherForecast()
    while True:
        phrase = input("Введите город: ").lower()
        try:
            location = weather_forecast.get_location(phrase)
            weather = await weather_forecast.get_weather(location[0].title())
            print(weather)
        except LocationExtractorException:
            print("Вы не указали город...\nДавайте попробуем еще раз.")
        except ExternalServiceException:
            print("Упс, возникла ошибка при получении погоды :(\nДавайте попробуем еще раз.")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
