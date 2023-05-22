import requests
from bs4 import BeautifulSoup
import csv
import os

URL = 'https://bestmanikyur.ru/'
url_links = []
test_links = ['https://bestmanikyur.ru/']
hash_list = []

# Запись полученных данных в файл
def write_csv(data):
    with open('manicure.csv', 'a', encoding='utf8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow((data['name'],
                         data['img_name'],
                         data['img_folder'],
                         data['img_folder_y'],
                         data['img_folder_y_m'],
                         data['hash']))

# Количество уникальных хеш тегов , запись в файл
def write_csv_link(link):
    with open('hash.csv', 'a', encoding='utf8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow((link))


def get_html(url):
    r = requests.get(url)
    return r

# Получаем количество страниц на сайте
def get_total_pages(html):
    soup = BeautifulSoup(html.content, 'html.parser')
    pages = soup.find('div', class_='navigation').find_all('a')[-2].get('href')
    total_pages = pages.split('/')[-2]
    return int(total_pages)

# Формируем полный адрес страницы для парсера
def url_page():
    page_part = 'page/'

    total_pages = get_total_pages(get_html(URL))

    for i in range(1, total_pages + 1):
        if i == 1:
            url_gen = 'https://bestmanikyur.ru/'
            url_links.append(url_gen)
        else:
            url_gen = URL + page_part + str(i) + '/'
            url_links.append(url_gen)
    return url_links

# Основная функция запуска
def get_page_data():
    all_hash_link = []

    def get_img_file(url):
        rImg = requests.get(url, stream=True)
        return rImg

    def save_image(name_folder, file_object):

        with open(name_folder, 'bw') as f:
            for chunk in file_object.iter_content(8192):
                f.write(chunk)

    pages = url_page()

    for i in pages:
        n = 0
        soup = BeautifulSoup(get_html(i).content, 'html.parser')
        find_all_links = soup.find('div', class_='catalog__list').find_all('div', class_='catalog__item')

        for all_links in find_all_links:
            n = n + 1

            links = all_links.find('div', class_='catalog__itemWrap')
            if n != 5:
                def get_hash_links(link, name, img_name, img_folder, img_folder_y, img_folder_y_m):
                    all_hash_list = []
                    all_hash_list.clear()

                    try:
                        tagsFind = link.find('div', class_='catalog__tags')
                        tags = tagsFind.find_all('a', class_='catalog__tag')
                        for tag in tags:
                            hash_tag = tag.get('href')
                            hash_value = tag.text.strip()
                            hash_data = {
                                hash_value: hash_tag
                            }
                            all_hash_list.append(hash_data)
                            if not hash_value in all_hash_link:
                                all_hash_link.append(hash_value)
                    except AttributeError:
                        print(AttributeError)

                    data = {
                        'name': name,
                        'img_name': img_name,
                        'img_folder': img_folder,
                        'img_folder_y': img_folder_y,
                        'img_folder_y_m': img_folder_y_m,
                        'hash': all_hash_list
                    }

                    write_csv(data)
                    all_hash_list.clear()

                def get_img_link(link):
                    img_full_path = ''
                    img_full_name = ''
                    path_img = ''
                    img_name = ''
                    img_folder = ''
                    img_folder_y = ''
                    img_folder_y_m = ''
                    try:
                        img_links = link.find('div', class_='catalog__img')
                        img_full_name = img_links.find('a').get('href').split('/')[-2]
                        img_full_path = img_links.find('img').get('src')

                        find_img = img_full_path.split('/')

                        img_name = find_img[-1]

                        img_folder = find_img[4]

                        img_folder_y = find_img[5]

                        img_folder_y_m = find_img[6]

                        path_img = img_folder + '/' + img_folder_y + '/' + img_folder_y_m + '/'
                    except AttributeError:
                        print(AttributeError)

                    if not os.path.exists(path_img):
                        os.makedirs(path_img)

                    path = os.path.abspath(path_img) + '/' + img_name

                    save_image(path, get_img_file(img_full_path))
                    get_hash_links(link, img_full_name, img_name, img_folder, img_folder_y, img_folder_y_m)

                get_img_link(links)
    write_csv_link(all_hash_link)
    print(len(all_hash_link))

def main():
    get_page_data()


if __name__ == '__main__':
    main()
