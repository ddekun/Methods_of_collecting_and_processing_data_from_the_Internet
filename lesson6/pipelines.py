# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from pymongo import MongoClient

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancy_scrapy


    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['salary_min'], item['salary_max'], item['currency'] = self.process_salary_hh(item['salary'])
        else:
            item['salary_min'], item['salary_max'], item['currency'] = self.process_salary_sj(item['salary'])

        del item['salary']
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    def process_salary_hh(self, salary):
        print(salary)
        if salary == ['з/п не указана']:
            min_v = max_v = curr = 'None'
        elif salary[0] == 'от ' and salary[2] == ' до ':
            min_v = int(salary[1].replace('\xa0', ''))
            max_v = int(salary[3].replace('\xa0', ''))
            curr = salary[5]
        elif salary[0] == 'от ' and salary[2] != ' до ':
            min_v = int(salary[1].replace('\xa0', ''))
            max_v = 'None'
            curr = salary[3]
        elif salary[0] == 'до ':
            min_v = 'None'
            max_v = int(salary[1].replace('\xa0', ''))
            curr = salary[3]
        return min_v, max_v, curr

    def process_salary_sj(self, salary):
        print(salary)
        if salary == ['По договорённости']:
            min_v = max_v = curr = 'None'
        elif salary[0] == 'от':
            min_v_cur = salary[2].replace('\xa0', '')
            min_v = int(''.join(x for x in min_v_cur if x.isdigit()))
            max_v = 'None'
            curr = ''.join(x for x in min_v_cur if x.isalpha())
        elif salary[0] == 'до':
            min_v = 'None'
            max_v_cur = salary[2].replace('\xa0', '')
            max_v = int(''.join(x for x in max_v_cur if x.isdigit()))
            curr = ''.join(x for x in max_v_cur if x.isalpha())
        else:
            min_v = int(salary[0].replace('\xa0', ''))
            max_v = int(salary[1].replace('\xa0', ''))
            curr = salary[3]
        return min_v, max_v, curr

