import requests
from bs4 import BeautifulSoup
import pandas as pd

# تابع برای استخراج تعداد کل صفحات
def get_total_pages(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    pagination = soup.find('div', class_='paginationParent')
    if pagination:
        pages = pagination.find_all('a')
        total_pages = max([int(page.text) for page in pages if page.text.isdigit()])
        return total_pages
    return 1

# تابع برای استخراج داده‌ها از یک صفحه خاص
def extract_data_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    links = []
    for row in rows:
        if 'حاجی دلیگانی' in row.text:
            link = row.find('a', href=True)
            if link:
                links.append(link['href'])
    return links

# تابع برای پیمایش صفحات مختلف
def get_all_links(base_url):
    total_pages = get_total_pages(base_url)
    all_links = []
    for page in range(0, total_pages):
        url = f"{base_url}?p={page}"
        links = extract_data_from_page(url)
        all_links.extend(links)
    return all_links

# تابع برای استخراج اطلاعات از لینک‌ها و ذخیره در یک فایل اکسل
def extract_and_save_data(links):
    data = []
    for link in links:
        for page in range(0,6) :
            response = requests.get(f"{link}?p={page}")
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) > 1 and not ('نماینده' in cells[1].text):
                    name = cells[1].text.strip()
                    city = cells[2].text.strip() if len(cells) > 2 else ''
                    status = cells[3].text.strip() if len(cells) > 3 else ''
                    vote = cells[4].text.strip() if len(cells) > 4 else ''
                    data.append({'Name': name, 'City': city, 'vote': vote})

    # ایجاد یک دیتافریم پانداس
    df = pd.DataFrame(data)
    # شمارش تعداد موافق، مخالف و عدم مشارکت برای هر اسم
    summary = df.groupby(['Name', 'City','vote']).size().unstack(fill_value=0)
    summary.to_excel('summary.xlsx')
    

        

# آدرس پایه صفحه مورد نظر
base_url = "https://shafanama.ir/%D9%85%D8%B5%D9%88%D8%A8%D8%A7%D8%AA-%D9%85%D8%AC%D9%84%D8%B3"
all_links = get_all_links(base_url)
print(f"count of fonded tarh : {len(all_links)}")
# extract_and_save_data(all_links)
