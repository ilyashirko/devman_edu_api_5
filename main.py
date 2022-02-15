from email import header
import json

import requests

from tqdm import tqdm

BASE_URL = 'https://api.hh.ru/'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}

AREAS = {
    "Saint-Petersburg": "2",
    "Moscow": "1"
}

SPECIALIZATIONS = {
    "Программирование, Разработка": "1.221"
}

TOP_LANGS = (
        "JavaScript",
        "Java",
        "Python",
        "Ruby",
        "PHP",
        "C++",
        "C#",
        "C",
        "Go",
        "Shell"
    )


  # ОТЛАДОЧНАЯ
def save_content(content, file_name):
    try:
        with open(f'{file_name}.json', 'w') as file:
            json.dump(content, file, indent=4, ensure_ascii=False)
    except:
        with open(f'{file_name}.txt', 'w') as file:
            file.write(content)


def get_areas():
    areas = requests.get(f'{BASE_URL}areas', headers=HEADERS)
    areas.raise_for_status()
    save_content(areas.json(), 'areas')


def get_specializations():
    specializations = requests.get(f'{BASE_URL}specializations', headers=HEADERS)
    specializations.raise_for_status()
    save_content(specializations.json(), 'specializations')


def get_vacancies(params):
    vacancies = requests.get(f'{BASE_URL}vacancies', headers=HEADERS, params=params)
    vacancies.raise_for_status()
    save_content(vacancies.json(), 'test')
    return vacancies.json()


def predict_rub_salary(vacancy):
    if vacancy['salary']['currency'] != 'RUR':
        return None
    salary_from = vacancy['salary']['from']
    salary_to = vacancy['salary']['to']
    if salary_from and salary_to:
        return round((salary_from + salary_to) / 2)
    elif salary_from:
        return round(salary_from * 1.2)
    else:
        return round(salary_to * 0.8)


def get_hh_salary_stat():
    languages_salary_stat = {}
    for language in tqdm(TOP_LANGS):
        salaries = []
        page = 1
        while True:
            params = {
                "area": AREAS['Moscow'],
                "specialization": SPECIALIZATIONS['Программирование, Разработка'],
                "period": "30",
                "host": "hh.ru",
                "per_page": "100",
                "page": page,
                "text": language
            }
            try:
                vacancies = get_vacancies(params)
            except requests.exceptions.HTTPError:
                break
            
            languages_salary_stat.update(
                {
                language: {
                    'vacancies_found': vacancies['found']
                    }
                }
            )
            
            for vacancy in get_vacancies(params)['items']:
                if vacancy['salary']:
                    salary = predict_rub_salary(vacancy)
                    if salary:
                        salaries.append(salary)

            page += 1

        languages_salary_stat[language].update(
            {
                "vacancies_processed": len(salaries),
                "average_salary": round(sum(salaries) / len(salaries))
            }
        )
    return languages_salary_stat


if __name__ == '__main__':
    languages_salary_stat = get_hh_salary_stat()
    save_content(languages_salary_stat, 'salary_stat')
    json.dumps(languages_salary_stat, indent=4)