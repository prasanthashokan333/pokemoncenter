from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import json
from lxml import etree
import json
import time
import os
import glob
from datetime import datetime
import pandas as pd

current_date = datetime.now().strftime('%d-%m-%Y')
folder_name =f"jsons//{current_date}"
json_path = f"{folder_name}"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
with open('dogo_production.json', "r") as file:
    urls = json.load(file)
output_json = []
for url in urls[:5]:
    product_index = urls.index(url)
    p_cd = url['url'].split("p_cd=")[-1]
    file_path = f"jsons//{current_date}//{p_cd}.json"
    product_url = f'https://www.pokemoncenter-online.com/?p_cd={p_cd}'
    print(product_index,product_url)
    if not os.path.isfile(file_path):
        product_url = f'https://www.pokemoncenter-online.com/?p_cd={p_cd}'
        driver_path = 'chromedriver.exe' #change depend on your chrome driver path
        service = Service(executable_path=driver_path)
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument('--headless') 
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--blink-settings=imagesEnabled=false');chrome_options.add_argument("--disable-web-security");chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process");chrome_options.add_argument('--log-level=1')
        driver = webdriver.Chrome(service=service,options=chrome_options)
        driver.get(product_url)
        driver.maximize_window()
        time.sleep(10)
        page_source = driver.page_source 
        driver.quit() 
        parser = etree.HTMLParser()
        tree = etree.fromstring(page_source, parser)

        error =  tree.xpath('//div[@class="not_found_wrap"]')
        data = {
                "url":product_url,"images": "","price": "","title": "","have_stock": False
            }
        if not error:
            data = {};images =[]
            product_details = tree.xpath('//div[@class="item_detail"]')[0]
                
            for image_url in product_details.xpath('.//ul[@id="tmb"]//img'):
                src = image_url.get('src') 
                if 'http' not in src:
                    src  = 'https://www.pokemoncenter-online.com/'+src
                images.append(src.strip())
            data['url'] = product_url
            data['images'] = images
            data['title'] =   tree.xpath('//title/text()')[0].split(" : ポケモンセンターオンライン")[0].strip() #//article/h1/text()')[0]
            data['price'] = tree.xpath("//meta[@name='twitter:data1']")[0].get('content').strip()
            data['have_stock'] = True if len(product_details.xpath('//article//img[@class="add_cart_btn"]'))==1 else False  
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file)
    else:
        print("Already completed",product_index,product_url)
with open("output_json", "w", encoding="utf-8") as json_file:
    json.dump(output_json,json_file,ensure_ascii=False, indent=2)
print("output json file created")
df = pd.DataFrame(output_json)
excel_filename = 'output.xlsx'
df.to_excel(excel_filename, index=False)

print(f"Data successfully exported to {excel_filename}.")