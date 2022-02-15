import requests
import environs

from terminaltables import AsciiTable
from tqdm import tqdm

env = environs.Env()
env.read_env()

HH_BASE_URL = 'https://api.hh.ru/'

SJ_BASE_URL = 'https://api.superjob.ru/2.0/'

HH_HEADERS = {
    'User-Agent': env.str('USER_AGENT')
}

SJ_HEADERS = {
    'X-Api-App-Id': env.str('SJ_SECRET_KEY')
}

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
    return None


def get_hh_salary_stat():
    languages_salary_stat = {}
    for language in tqdm(TOP_LANGS):
        salaries = []
        page = 1
        while True:
            params = {
                "area": AREAS['hh']['Moscow'],
                "specialization": SPECIALIZATIONS['hh']['Программирование'],
                "period": "30",
                "host": "hh.ru",
                "per_page": "100",
                "page": page,
                "text": language
            }
            response = requests.get(
                f'{HH_BASE_URL}vacancies',
                headers=HH_HEADERS,
                params=params
            )

            response.raise_for_status()
            vacancies = response.json()

            for vacancy in vacancies['items']:
                if vacancy['salary']:
                    salary = predict_rub_salary_for_headhunter(vacancy)
                    if salary:
                        salaries.append(salary)

            if vacancies['pages'] == page:
                break
            page += 1

        languages_salary_stat.update(
            {
                language: {
                    'vacancies_found': vacancies['found'],
                    "vacancies_processed": len(salaries),
                    "average_salary": round(sum(salaries) / len(salaries))
                }
            }
        )
    return languages_salary_stat


def get_sj_salary_stat():
    languages_salary_stat = {}
    for language in tqdm(TOP_LANGS):
        salaries = []
        page = 0
        while True:
            sj_params = {
                'keyword': language,
                'town': AREAS['sj']['Moscow'],
                'catalogue': SPECIALIZATIONS['sj']['Программирование'],
                'page': page
            }

            response = requests.get(
                f'{SJ_BASE_URL}vacancies',
                headers=SJ_HEADERS,
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

            page += 1

        languages_salary_stat.update(
            {
                language: {
                    'vacancies_found': vacancies['total'],
                    'vacancies_processed': len(salaries),
                    'average_salary': round(sum(salaries) / len(salaries))
                }
            }
        )
    return languages_salary_stat


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
    try:
        sj_coding_salaries = get_sj_salary_stat()
    except requests.exceptions.HTTPError as error:
        print(f'Sorry, information from SuperJob is temporarily unavailable.\n'
              f'{error}')

    try:
        hh_coding_salaries = get_hh_salary_stat()
    except requests.exceptions.HTTPError as error:
        print(f'Sorry, information from HeadHunter is temporarily unavailable.'
              f'\n{error}')

    print(make_salary_table(sj_coding_salaries, 'SuperJob Moscow').table)
    print(make_salary_table(hh_coding_salaries, 'HeadHunter Moscow').table)
