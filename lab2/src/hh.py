import requests
import requests_cache
import itertools
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import random
from abc import ABC, abstractmethod

requests_cache.install_cache('wow')


class VacancyGetter:
    def __init__(self, query: str):
        self.query = query

    def get_vacancies_page(self, page: int) -> dict:
        params = {'text': self.query, 'only_with_salary': True, 'per_page': 100, 'page': page}
        r = requests.get('https://api.hh.ru/vacancies', params=params)
        return r.json()

    def get_all_vacancies(self) -> list:
        items = []

        first_page = self.get_vacancies_page(1)
        pages_count = first_page['pages']
        items.extend(first_page['items'])

        for page in range(2, pages_count):
            more_items = self.get_vacancies_page(page)['items']
            items.extend(more_items)
        return items


class VacancyClassifier(ABC):
    def __init__(self, vacancies: list):
        if len(vacancies) == 0:
            raise Exception('Where are vacancies?')
        self.vacancies = vacancies

    @abstractmethod
    def classify(self):
        pass

    @staticmethod
    def avg_salary(item: dict) -> int:
        salary = item['salary']
        if salary['from'] is None:
            return salary['to']
        elif salary['to'] is None:
            return salary['from']
        else:
            return (salary['from'] + salary['to']) / 2

    @staticmethod
    def filter_and_sort(vacancies: list, key: callable) -> list:
        vacancies = filter(lambda x: x['salary']['currency'] == 'RUR', vacancies)
        vacancies = sorted(vacancies, key=key)
        return vacancies


class VacancyMedianClassifier(VacancyClassifier):
    def __init__(self, vacancies: list):
        super(VacancyMedianClassifier, self).__init__(vacancies)

    def classify(self):
        def calc_median(lst: list):
            sorted_lst = sorted(lst)
            lst_len = len(sorted_lst)
            if lst_len == 1:
                return lst[0]
            index = (lst_len - 1) // 2
            if lst_len % 2:
                return sorted_lst[index]
            else:
                return (sorted_lst[index] + sorted_lst[index + 1]) / 2.0

        self.vacancies = VacancyClassifier.filter_and_sort(self.vacancies, lambda x: x['area']['name'])
        groups = itertools.groupby(self.vacancies, key=lambda x: x['area']['name'])

        data = []

        for city, vacancies in groups:
            salaries = list(map(self.avg_salary, list(vacancies)))
            median = calc_median(salaries)
            proposals_count = len(salaries)
            if proposals_count < 5:
                continue
            print("{:^3} вакансий => {:>16} имеет медианную зарплату {:<7n}".format(proposals_count, city, median))
            data.append({'key': '{} ({})'.format(city, proposals_count), 'value': median})

        return data


class VacancyRangeClassifier(VacancyClassifier):
    GROUP_DIFF = 20000

    def __init__(self, vacancies: list):
        super(VacancyRangeClassifier, self).__init__(vacancies)

    @staticmethod
    def get_currency():
        return "кг" if random.randint(1, 25) == 1 else "руб."

    def classify(self):
        self.vacancies = VacancyClassifier.filter_and_sort(self.vacancies, lambda x: self.avg_salary(x))
        groups = itertools.groupby(self.vacancies, key=lambda x: int(self.avg_salary(x) // self.GROUP_DIFF * self.GROUP_DIFF))

        data = []

        for salary_group, vacancies in groups:
            salaries = list(map(self.avg_salary, list(vacancies)))
            proposals_count = len(salaries)
            key = "от {:^7} до {:^7} {:>4}".format(
                salary_group,
                salary_group + self.GROUP_DIFF,
                VacancyRangeClassifier.get_currency()
            )
            print("Зарплата {}  - {:^2n} предложений".format(key, proposals_count))
            data.append({'key':  key, 'value':  proposals_count})

        return data


class PlotDrawer:
    def __init__(self, **kwargs):
        self.args = kwargs

    def draw(self, data: list):
        sns.set_style('whitegrid')
        sns.set_context('paper', font_scale=0.9)
        ax = sns.barplot(data=pd.DataFrame(data), x='key', y='value')
        ax.set(xlabel=self.args['xlabel'], ylabel=self.args['ylabel'])
        plt.title(self.args['title'])
        plt.xticks(rotation=40)
        plt.subplots_adjust(bottom=0.3)
        plt.show(ax)

