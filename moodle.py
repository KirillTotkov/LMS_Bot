import requests
from bs4 import BeautifulSoup
from faunadb import query
from faunadb.client import FaunaClient
import os
from database import get_all_cource

fauna_key = os.environ['FAUNAKEY']
lmskey = os.environ['LMSKEY']
clientf = FaunaClient(fauna_key)


def get_count_in_lms(id):
    request = f'https://lms.syktsu.ru/webservice/rest/server.php?wstoken={lmskey}&' \
              f'wsfunction=core_course_get_contents&courseid={id}&moodlewsrestformat=json'

    result = requests.get(request, headers={"User-Agent": "Mozilla/5.0"})
    data = result.json()
    tasks_cource = [x for x in data if len(x['modules']) != 0]
    tasks_list = []
    for i in tasks_cource:
        for j in i.get('modules'):
            if 'description' not in j.keys():
                tasks_list.append(
                    {
                        'name': j['name'],
                        'link': j['url']
                    }
                )
            elif j['modname'] == 'label':
                tasks_list.append(
                    {
                        'name': j['name']
                    }
                )
            else:
                description = j['description']
                soup = BeautifulSoup(description, 'lxml').text
                tasks_list.append(
                    {
                        'name': j['name'],
                        'link': j['url'],
                        'description': soup
                    }
                )
    return tasks_list


def collect_data():
    data = get_all_cource()
    answer_data = []
    for cource in data:
        tasks_list = get_count_in_lms(cource['id'])

        old_count = cource['count']
        real_count = len(tasks_list)
        diff = real_count - old_count

        if diff == 0:
            pass
            # return False
            # print("Ничего не изменилось")
            # print(f"{cource['fullname']} \n" )
        elif diff > 0:
            clientf.query(
                query.update(query.select('ref', query.get(query.match(query.index("courses_by_id"), cource['id']))),
                             {'data': {'count': real_count}}))

            tasks_list = tasks_list[-diff:]

            for i in tasks_list:
                i['fullname'] = cource['fullname']

            answer_data.append(tasks_list)
        else:
            print("ERROR Moodle.py \n")

    return answer_data


def main():
    collect_data()


if __name__ == "__main__":
    main()
