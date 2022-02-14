import os

import requests
from bs4 import BeautifulSoup
from faunadb import query
from faunadb.client import FaunaClient

from database import get_all_cource

fauna_key = os.environ['FAUNAKEY']
lmskey = os.environ['LMSKEY']
clientf = FaunaClient(fauna_key)
data = get_all_cource()


# def get_number_courses():
#     request = f'https://lms.syktsu.ru/webservice/rest/server.php?wstoken={lmskey}' \
#               f'&wsfunction=core_course_get_enrolled_courses_by_timeline_classification&' \
#               f'classification=all&moodlewsrestformat=json'
#
#     result = requests.get(request, headers={"User-Agent": "Mozilla/5.0"})
#     all_cource = result.json()['courses']
#     print(len(data))
#     return len(all_cource)
# get_number_courses()

def get_count_in_lms(id):
    request = f'https://lms.syktsu.ru/webservice/rest/server.php?wstoken={lmskey}&' \
              f'wsfunction=core_course_get_contents&courseid={id}&moodlewsrestformat=json'

    result = requests.get(request, headers={"User-Agent": "Mozilla/5.0"})
    data = result.json()
    tasks_cource = [x for x in data if len(x['modules']) != 0]
    tasks_list = []
    summary_text = ''
    for i in tasks_cource:
        # print(i)

        summary_html = i['summary']
        if summary_html != '':
            # print(summary)
            soup = BeautifulSoup(summary_html, 'lxml')
            blocks = soup.find_all('p')
            for block in blocks:
                summary_text += block.getText(separator="\n").strip()
            tasks_list.append(
                {
                    'id': i['id'],
                    'name': i['name'],
                    'summary': summary_text
                }
            )
            summary_text = ''
        for j in i.get('modules'):
            if 'description' not in j.keys():
                tasks_list.append(
                    {
                        'id': j['id'],
                        'name': j['name'],
                        'link': j['url']
                    }
                )
            elif j['modname'] == 'label':
                tasks_list.append(
                    {
                        'id': j['id'],
                        'name': j['name']
                    }
                )
            else:
                description = j['description']
                soup = BeautifulSoup(description, 'lxml').text
                tasks_list.append(
                    {
                        'id': j['id'],
                        'name': j['name'],
                        'link': j['url'],
                        'description': soup
                    }
                )

    return tasks_list


def collect_data():
    answer_data = []
    for cource in data:
        tasks_list = get_count_in_lms(cource['id'])

        id_tasks = [x['id'] for x in tasks_list]  # id заданий с Moodle
        diff_id = list(set(cource['id_tasks']) ^ set(id_tasks))  # id новых заданий
        # try:
        #     diff_id = list(set(cource['id_tasks']) ^ set(id_tasks))  # id новых заданий
        # except:
        #     print("ERRROORORR")
        #     clientf.query(
        #         query.update(query.select('ref', query.get(query.match(query.index("courses_by_id"), cource['id']))),
        #                      {'data': {'id_tasks': id_tasks}}))

        if len(diff_id) > 0:
            for task in tasks_list:
                id = task['id']
                for new_id in diff_id:
                    if id == new_id:
                        task['fullname'] = cource['fullname']
                        answer_data.append(task)
            real_count = len(tasks_list)
            if len(id_tasks) < len(cource['id_tasks']):
                print("ERROR MOODLE.py")
                clientf.query(
                    query.update(
                        query.select('ref', query.get(query.match(query.index("courses_by_id"), cource['id']))),
                        {'data': {'count': real_count}}))

            clientf.query(
                query.update(query.select('ref', query.get(query.match(query.index("courses_by_id"), cource['id']))),
                             {'data': {'id_tasks': id_tasks}}))

    return answer_data


def main():
    collect_data()


if __name__ == "__main__":
    main()
