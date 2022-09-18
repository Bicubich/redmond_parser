from bs4 import BeautifulSoup
import requests
import pandas as pd

url = "https://redmondsale.com/"
folder = "catalog/"
additional_url = "?PAGEN_1="
no_photo_image = "https://redmondsale.com/bitrix/templates/capitalim_s1/images/noimg/noimg_minquadro.jpg"

data = {'Категория': [], 'Модель': [], 'Название': [], 'Цена': [], 'Фото': []}

request = requests.get(url + folder)

soup = BeautifulSoup(request.text, 'lxml')

# получаем кол-во страниц каталога
count_pages_catalog = int(soup.find("div", class_="bx_pagination_page").find_all("a")[-2].text)

# перелистываем страницы каталога
for i in range(1, count_pages_catalog + 1):
    request = requests.get(url + folder + additional_url + str(i))
    soup = BeautifulSoup(request.text, 'lxml')

    # берем список всех товаров на странице
    items_catalog = soup.find_all("div", class_="one_section_product_cells")
    for item_catalog in items_catalog:
        number_product = item_catalog.find("a")['href'][9:]
        request = requests.get(url + folder + number_product)

        soup = BeautifulSoup(request.text, 'lxml')

        # берем кол-во страниц на странице товара (может не быть страниц)
        try:
            count_pages_product = int(soup.find("div", class_="bx_pagination_page").find_all("a")[-2].text)
        except:
            count_pages_product = 1
        
        # берем каждую страницу на странице товара
        for i in range(1, count_pages_product + 1):
            request = requests.get(url + folder + number_product + additional_url + str(i))
            soup = BeautifulSoup(request.text, 'lxml')

            # сохраняем модель
            model = soup.find("h1", class_="header_grey").text
            # сохраняем категория
            category = soup.find("ul", class_="breadcrumb-navigation").find_all('a')[-1].text
            # нет категории
            if category == "Каталог":
                category = ""

            # запчасти товара
            items_product = soup.find("div", class_="bg_table").find_all('tr')
            for item_product in items_product:
                try:
                    photo = url + item_product.find("td", class_="td_photo").find('img').get('src').replace('resize_cache/', '').replace('100_100_1/', '')
                    if photo == no_photo_image:
                        photo = "Нет фото"
                    name = item_product.find("td", class_="td_name").find("a", class_="link_element").text.strip()
                    price = item_product.find("td", class_="td_price").text.replace('*', '').replace('руб.', '').strip()

                    # сохраняем в словарь
                    data['Категория'].append(category if category else "")
                    data['Модель'].append(model if model else "")
                    data['Название'].append(name if name else "")
                    data['Цена'].append(price if price else "")
                    data['Фото'].append(photo if photo else "")

                    # вывод в консоль
                    print(f"Фото: {photo}\nНазвание: {name}\nЦена: {price}\nМодель: {model}\nКатегория: {category}\n")
                except:
                    continue

# запись в excel
df = pd.DataFrame(data)
df.to_excel('result.xlsx', sheet_name='page_1', index=False)

answer = input("Парсинг закончен...Нажмите любую кнопку")

