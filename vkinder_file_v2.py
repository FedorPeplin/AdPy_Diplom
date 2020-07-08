import requests
import json
from pprint import pprint
import string
import psycopg2

conn = psycopg2.connect(database='netology', user='netology', password='netology', host='localhost', port=5432)
cur = conn.cursor()

with open('tokenfile.txt') as f:
    token = f.read()

params = {
    'access_token': token,
    'v': 5.103
}

def get_id(in_data):
    #Возврат численного ID пользователя
    if in_data.isdecimal():
        u_id = in_data
    else:
        request_url = 'https://api.vk.com/method/users.get?user_ids=' + in_data
        response = requests.get(
            request_url,
            params
        )
        response_json = response.json()
        u_id = response_json['response'][0]['id']
    return u_id

def get_searcher_id():
    searcher_id = input('Введите ID пользователя: ')
    return get_id(searcher_id)

def get_country_code(country_name):
    params['need_all'] = 0
    params['code'] = country_name
    response_country = requests.get(
        'https://api.vk.com/method/database.getCountries',
        params
    )
    counries_json = response_country.json()
    return counries_json['response']['items'][0]['id']


def get_city_code(city_string):
    #Берёт имя города и возвращает его код ВК. Если не найден - то возвращает 0)
    country_name = input('Введите имя страны (2 латинские буквы): ')
    country_code = get_country_code(country_name)
    params['country_id'] = country_code
    params['q'] = city_string
    params['need_all'] = 0
    response_cities = requests.get(
        'https://api.vk.com/method/database.getCities',
        params
    )
    cities_json = response_cities.json()
    if cities_json['response']['count'] > 0:
        for city in cities_json['response']['items']:
            if country_code >= 4 or country_code < 4 and city['title'].lower() == city_string.lower():
                return city['id']
    return 0


def enter_data():
    try:
        require_dict = {'city': get_city_code(input('Enter city: ')), 'age_from': int(input('Enter minimal age: ')),
                        'age_to': int(input('Enter maximal age: ')), 'sex': input('Enter gender (M/F): '),
                        'interests': input('Enter interests: '), 'music': input('Enter music interests: '),
                        'books': input('Enter literature interests: ')}
        if require_dict['sex'].lower() not in ['m', 'f']:
            raise KeyError
    except KeyError:
        print('Некорректный ввод, попробуйте сначала')
        require_dict = enter_data()
    except ValueError:
        print('Некорректный ввод, возраст должен быть в виде числа, попробуйте заново')
        require_dict = enter_data()
    return require_dict


# def enter_data_2(): #втораая версия ввода данных
#     user_dict = get_user_data(user_id)
#     require_dict = {}
#     try:
#         if user_dict['city']:
#             require_dict['city'] = user_dict['city']
#         else:
#             require_dict['city'] = get_city_code(input('Введите город: '))
#
#         if user_dict['age']:
#             require_dict['age_from'] = user_dict['age'] - 5
#             require_dict['age_to'] = user_dict['age'] + 5
#         else:
#             require_dict['age_from'] = int(input('Введите минимальный возраст: '))
#             require_dict['age_to'] = int(input('Введите максимальный возраст: '))
#
#         if user_dict['sex']:
#             require_dict['sex'] = (require_dict['sex'] + 1) % 2
#         else:
#             require_dict['sex'] = input('Введите пол (M/F): ')
#
#         require_dict['interests'] = input('Введите интересы: ')
#         require_dict['music'] = input('Введите музыкальные интересы: ')
#         require_dict['books'] = input('Введите литературне интересы: ')
#
#         if require_dict['sex'].lower() not in ['m', 'f']:
#             raise KeyError
#
#     except KeyError:
#         print('Некорректный ввод, попробуйте сначала')
#         require_dict = enter_data()
#     except ValueError:
#         print('Некорректный ввод, возраст должен быть в виде числа, попробуйте заново')
#         require_dict = enter_data()
#     return require_dict


def get_requirements_dict():
    #берёт и возвращает словарь предпочитаемых данных поиска пользователей
    print('Введите данные')
    req_dict = enter_data()
    user_data = get_user_data(user_id)
    if req_dict['sex'].lower() == 'm':
        req_dict['sex'] = 2
    elif req_dict['sex'].lower() == 'f':
        req_dict['sex'] = 1
    for key, value in req_dict.items():
        if not value:
            if key == 'возраст от':
                req_dict[key] = 1
            elif key == 'возраст до':
                req_dict[key] = 90
            else:
                req_dict[key] = user_data[key]
    print('Успешно')
    return req_dict


def get_user_data(u_id):
    #берёт данные пользователя и помещает их в словарь
    print('Получение пользовательских данных...')
    params['user_ids'] = u_id
    params['fields'] = ['city', 'interests', 'music', 'movies', 'tv', 'books', 'games']
    response_user_info = requests.get(
        'https://api.vk.com/method/users.get',
        params
    )
    user_info_json = response_user_info.json()
    response_dict = user_info_json['response'][0]
    if 'deactivated' in response_dict.keys() or response_dict['is_closed'] and not response_dict['can_access_closed']:
        print('Нет доступа в профиль, возможно, он закрыт')
    else:
        print('Пользовательские данные получены успешно')
        return response_dict


def search_for_major_propers(req_dict):
    #получение пользователей, соответствующих требованиям и возвращение списка пользователей
    keys_list = ['city', 'age_to', 'age_from', 'sex']
    param = {
        'access_token': token,
        'v': 5.103,
        'sort': 0,
        'count': 500,
        'has_photo': 1,
        'fields': ['interests, music, movies, tv, books, games, about']
    }
    for key in keys_list:
        param[key] = req_dict[key]
    response_search_users = requests.get(
        'https://api.vk.com/method/users.search',
        param
    )
    search_users_json = response_search_users.json()
    search_users_result = search_users_json['response']['items']
    return search_users_result


def delete_marks(string1):
    #удаляет все пунктуационные знаки из текста и возвращает результат
    st = str.maketrans(dict.fromkeys(string.punctuation))
    string2 = string1.translate(st)
    return string2


def make_list_from_dict(data_dict):
    #объединяет все величины словаря в список слов. величины должны быть формата string
    major_user_keys = ['can_access_closed', 'id', 'first_name', 'last_name', 'city',
                       'age_from', 'age_to', 'sex', 'is_closed', 'track_code', 'relation']
    data_string = ''
    data_list = []
    for key, value in data_dict.items():
        if key not in major_user_keys:
            data_string += value
    data_string = delete_marks(data_string)
    data_list = data_string.split()
    return data_list


def search_for_minor_propers(list1, user_data_dict):
    #проверяет если пользователь имеет некоторые схожести в неосновных требованиях. возвращает список "количество_схожести: пользователь"
    count = 0
    res_dict = {}
    list2 = make_list_from_dict(user_data_dict)
    for word in list1:
        if word in list2:
            count += 1
    if count > 0:
        res_dict = {count: user_data_dict['id']}
    return res_dict


def get_users_dict(string1, users_list):
    #возвращает словарь с количеством совпадений как ключи и списки id как величины
    res_dict = {}
    ind = 0
    for usr in users_list:
        if 'relation' not in usr.keys() or usr['relation'] in [0, 1, 6]:
            proper = search_for_minor_propers(string1, usr)
            if proper:
                for key, value in proper.items():
                    if key in res_dict.keys():
                        res_dict[key].append(value)
                    else:
                        res_dict[key] = [value]
            ind += 1
    return res_dict


def sort_data_dict(data_dict):
    #сортирует входящий словарь по ключу и возвращает их значения в сортированный список от максимального к минимальному
    res_list = []
    keys_list = list(data_dict.keys())
    keys_list.sort()
    keys_list = keys_list[-1:-4:-1]
    for i in keys_list:
        res_list.append(data_dict[i])
    return res_list


def get_best_photos(u_id):
    #возвращает 3 пользовательских фотки из последних 20 фоток с наибольшим количеством лайков
    photo_dict = {}
    param = {
        'access_token': token,
        'v': 5.103,
        'owner_id': u_id,
        'album_id': 'profile',
        'rev': 1,
        'extended': 1,
        'count': 20
    }
    response_photos = requests.get(
        'https://api.vk.com/method/photos.get',
        param
    )
    photos_json = response_photos.json()
    if 'error' in photos_json.keys():
        return
    for item in photos_json['response']['items']:
        photo_dict[item['likes']['count']] = item['id']
    pics_list = sort_data_dict(photo_dict)
    return pics_list


def get_pics(user_dict):
    #возвращает список словарей с id, лучшими фотками и количеством совпаений подходящих пользователей
    final_dict = {}
    final_list = []
    for key, value in user_dict.items():
        for val in value:
            final_dict['id'] = val
            final_dict['matches'] = key
            final_dict['photos'] = get_best_photos(val)
            final_list.append(final_dict)
            final_dict = {}
    return final_list


def create_db():
    cur.execute('''CREATE TABLE IF NOT EXISTS photos(
    id serial PRIMARY KEY,
    photo1_id INTEGER,
    photo2_id INTEGER,
    photo3_id INTEGER);
    ''')
    conn.commit()

    cur.execute('''CREATE TABLE IF NOT EXISTS users(
    key_id serial PRIMARY KEY,
    id integer NOT NULL,
    matches integer NOT NULL,
    photos_id integer REFERENCES photos(id));
    ''')
    conn.commit()


def set_to_base(user_dict):
    if user_dict['photos']:
        photos_ids = user_dict['photos']
    else:
        photos_ids = [0, 0, 0]
    while len(photos_ids) < 3:
        photos_ids.append(0)

    cur.execute('INSERT INTO photos (photo1_id, photo2_id, photo3_id) VALUES (%s, %s, %s)',
                (photos_ids[0], photos_ids[1], photos_ids[2]))
    conn.commit()
    cur.execute('INSERT INTO users (id, matches) VALUES (%s, %s)', (user_dict['id'], user_dict['matches']))
    conn.commit()
    # print('done')


if __name__ == '__main__':
    user_id = input('Введите пользовательский ID: ')
    requirements_dict = get_requirements_dict()
    users_data_list = search_for_major_propers(requirements_dict)
    suitable_users_dict = get_users_dict(make_list_from_dict(requirements_dict), users_data_list)
    if not suitable_users_dict:
        users_list = []
        for user in users_data_list:
            users_list.append(user['id'])
        suitable_users_dict[1] = users_list
    file_name = user_id + 'recommendations.json'
    file_info = get_pics(suitable_users_dict)
    create_db()
    for final_user in file_info:
        set_to_base(final_user)
