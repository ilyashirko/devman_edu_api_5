from itertools import count

import requests
import environs

from terminaltables import AsciiTable
from tqdm import tqdm

HH_BASE_URL = 'https://api.hh.ru/'

SJ_BASE_URL = 'https://api.superjob.ru/2.0/'

AREAS = {
    'hh': {
        "Saint-Petersburg": "2",
        "Moscow": "1"
    },
    'sj': {
        "Moscow": "4"
    }
}

SPECIALIZATIONS = {
    'hh': {
        "Программирование": "1.221"
    },
    'sj': {
        'Программирование': "48"
    }
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


def predict_rub_salary_for_headhunter(vacancy):
    if vacancy['salary']['currency'] != 'RUR':
        return None
    salary_from = vacancy['salary']['from']
    salary_to = vacancy['salary']['to']
    return predict_salary(salary_from, salary_to)


def predict_rub_salary_for_superjob(vacancy):
    salary_from = vacancy['payment_from']
    salary_to = vacancy['payment_to']
    return predict_salary(salary_from, salary_to)


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return round((salary_from + salary_to) / 2)
    elif salary_from:
        return round(salary_from * 1.2)
    elif salary_to:
        return round(salary_to * 0.8)


def get_hh_salary_stat(hh_headers, language, area, specialization):
    salaries = []
    for page in count(0, 1):
        params = {
            "area": area,
            "specialization": specialization,
            "period": "30",
            "host": "hh.ru",
            "per_page": "100",
            "page": page,
            "text": language
        }
        response = requests.get(
            'https://api.hh.ru/vacancies',
            headers=hh_headers,
            params=params
        )

        response.raise_for_status()
        vacancies = response.json()

        for vacancy in vacancies['items']:
            if vacancy['salary']:
                salary = predict_rub_salary_for_headhunter(vacancy)
                if salary:
                    salaries.append(salary)

        if vacancies['pages'] == (page + 1):
            break
    return vacancies['found'], salaries


def get_sj_salary_stat(sj_headers, language, area, specialization):
    salaries = []
    for page in count(0, 1):
        sj_params = {
            'keyword': language,
            'town': area,
            'catalogue': specialization,
            'page': page
        }

        response = requests.get(
            'https://api.superjob.ru/2.0/vacancies',
            headers=sj_headers,
            params=sj_params
        )

        response.raise_for_status()
        vacancies = response.json()

        for vacancy in vacancies['objects']:
            salary = predict_rub_salary_for_superjob(vacancy)
            if salary:
                salaries.append(salary)

        if not vacancies['more']:
            break
    return vacancies['total'], salaries


def make_salary_table(languages_info, title):
    table = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        ]
    ]
    for language, info in languages_info.items():
        table.append(
            [
                language,
                info['vacancies_found'],
                info['vacancies_processed'],
                info['average_salary']
            ]
        )
    return AsciiTable(table, title)


if __name__ == '__main__':
    env = environs.Env()
    env.read_env()

    hh_headers = {
        'User-Agent': env.str('USER_AGENT')
    }

    sj_headers = {
        'X-Api-App-Id': env.str('SJ_SECRET_KEY')
    }
    print('Getting data...')
    sj_coding_salaries, hh_coding_salaries = {}, {}
    for language in tqdm(TOP_LANGS):
        try:
            sj_total, sj_salaries = get_sj_salary_stat(
                sj_headers,
                language,
                AREAS['sj']['Moscow'],
                SPECIALIZATIONS['sj']['Программирование']
            )
            sj_coding_salaries.update(
                {
                    language: {
                        'vacancies_found': sj_total,
                        'vacancies_processed': len(sj_salaries),
                        'average_salary': round(
                            sum(sj_salaries) / len(sj_salaries)
                        )
                    }
                }
            )
        except requests.exceptions.HTTPError:
            print(f'Sorry, {language} is not available now in SuperJob.')

        try:
            hh_total, hh_salaries = get_hh_salary_stat(
                hh_headers,
                language,
                AREAS['hh']['Moscow'],
                SPECIALIZATIONS['hh']['Программирование']
            )
            hh_coding_salaries.update(
                {
                    language: {
                        'vacancies_found': hh_total,
                        'vacancies_processed': len(hh_salaries),
                        'average_salary': round(
                            sum(hh_salaries) / len(hh_salaries)
                        )
                    }
                }
            )
        except requests.exceptions.HTTPError:
            print(f'Sorry, {language} is not available now in HeadHunter.')

    print(make_salary_table(sj_coding_salaries, 'SuperJob Moscow').table)
    print(make_salary_table(hh_coding_salaries, 'HeadHunter Moscow').table)
