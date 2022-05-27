from pymongo import MongoClient
from pprint import pprint
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

client = MongoClient('127.0.0.1', 27017)

db = client['HH_db']
HH_vacancy = db.vacancy

url = 'https://ekaterinburg.hh.ru/search/vacancy'
vacancy = input('Введите название вакансии: ')
# vacancy = 'Data scientist'
area = int(input('Введите регион поиска от 0 до 306: ')) #306 регион последний - 'Буркина Фасо'
# area = 1 # Москва
page = 0

params = {'text': vacancy,
          'area': area,
          'experience': 'doesNotMatter',
          'order_by': 'relevance',
          'search_period': 0,
          'items_on_page': 20,
          'page': page}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/101.0.4951.67 Safari/537.36'}

response = requests.get(url, headers=headers, params=params)

# with open('HH.html', 'w', encoding='utf-8') as f:
#     f.write(response.text)
# html = ''
# with open('HH.html', 'r', encoding='utf-8') as f:
#     html = f.read()

soup = bs(response.text, 'html.parser')
#print(soup)
try:
    last_page = int(soup.find_all('a',{'data-qa':'pager-page'})[-1].text)
except:
    last_page = 1

all_vacancies = []

for i in range(last_page):

    soup = bs(response.text, 'html.parser')

    vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies:
        vacancy_info = {}

        vacancy_anchor = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        vacancy_name = vacancy_anchor.getText()
        vacancy_info['name'] = vacancy_name

        vacancy_link = vacancy_anchor['href']
        vacancy_info['link'] = vacancy_link

        vacancy_info['site'] = url + '/'

        vacancy_salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        if vacancy_salary is None:
            min_salary = None
            max_salary = None
            currency = None
        else:
            vacancy_salary = vacancy_salary.getText()
            if vacancy_salary.startswith('до'):
                max_salary = int("".join([s for s in vacancy_salary.split() if s.isdigit()]))
                min_salary = None
                currency = vacancy_salary.split()[-1]

            elif vacancy_salary.startswith('от'):
                max_salary = None
                min_salary = int("".join([s for s in vacancy_salary.split() if s.isdigit()]))
                currency = vacancy_salary.split()[-1]

            else:
                max_salary = int("".join([s for s in vacancy_salary.split('–')[1] if s.isdigit()]))
                min_salary = int("".join([s for s in vacancy_salary.split('–')[0] if s.isdigit()]))
                currency = vacancy_salary.split()[-1]

        vacancy_info['max_salary'] = max_salary
        vacancy_info['min_salary'] = min_salary
        vacancy_info['currency'] = currency

        all_vacancies.append(vacancy_info)

    params['page'] += + 1
    response = requests.get(url, headers=headers, params=params)
    print(len(all_vacancies))
    #print(all_vacancies)


# df = pd.DataFrame(all_vacancies)
# print(df.head())
# df.to_csv("vacancies.csv")


# Добавление новых вакансий в ДБ

def db_update(database, vac_list):
    x = True
    for vac in vac_list:
        for el in HH_vacancy.find({}):
            if el['name'] == vac['name'] and \
                el['max_salary'] == vac['max_salary'] and \
                el['min_salary'] == vac['min_salary'] and \
                el['currency'] == vac['currency']:
                x = False
                break
            else:
                x = True
        if x:
            database.insert_one(vac)
    return database

db_update(HH_vacancy, all_vacancies)

# Вакансии из ДБ по ЗП
def show_vacancy(database):
    try:
        salary = int(input('Введите зарплату: '))
        s = []
        for el in database.find({'$or': [
                                    {'min_salary': {'$gte': salary}},
                                    {'max_salary': {'$gte': salary}}
                                ]}):
            s.append(el)
        return pprint(s)
    except ValueError:
        print('Введите число: ')

show_vacancy(HH_vacancy)





