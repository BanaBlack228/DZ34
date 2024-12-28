import requests
import json
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
from requests.exceptions import ConnectionError


def get_html(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200 or str(response.status_code)[0] == '3':
            html = response.text
            return html
        else:
            print(f'Ошибка запроса! код ответа: {response.status_code}')
            return None
    except ConnectionError as err:
        print(f"Ошибка запроса! \n{err}")
        return None


def get_weather_from_day(html):
    soup = BS(html, 'html.parser')
    weather_info_all_days = []

    weather_short_blocks = soup.find_all("div", class_="weather-short")

    for weather_short_block in weather_short_blocks:
        weather_info = {}

        date_element = weather_short_block.find("div", class_=["dates short-d", "dates short-d red"])
        if date_element:
            day_of_week_element = date_element.find("span")
            if day_of_week_element:
                day_of_week = day_of_week_element.text
                date = date_element.text.replace(day_of_week + ", ", "")

                weather_info["Дата"] = f' {date}, {day_of_week}'

                weather_table = weather_short_block.find("table", class_="weather-today")
                if weather_table:
                    time_of_day_rows = weather_table.find_all("tr")

                    for row in time_of_day_rows:
                        time_of_day = row.find("td", class_="weather-day").text
                        temperature = row.find("span").text
                        feeling_temperature = row.find("td", class_="weather-feeling").text
                        probability = row.find("td", class_="weather-probability").text
                        pressure = row.find("td", class_="weather-pressure").text
                        wind_speed = row.find("td", class_="weather-wind").find_all("span")[-1].text
                        humidity = row.find("td", class_="weather-humidity").text

                        weather_info[time_of_day] = {
                            "Температура": temperature,
                            "Ощущается как": feeling_temperature,
                            "Вероятность осадков": probability,
                            "Давление": pressure,
                            "Скорость ветра": wind_speed,
                            "Влажность": humidity
                        }

                weather_info_all_days.append(weather_info)

    return weather_info_all_days


def write_data_to_json(data: dict) -> None:
    with open('weather.json', 'a', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


URL = "https://world-weather.ru/pogoda/russia/saint_petersburg/7days/"
html = get_html(url=URL)
if html:
    data = get_weather_from_day(html)
    write_data_to_json(data)
