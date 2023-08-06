import requests
from lxml import etree
import json
import time
import os
import glob
from datetime import datetime
import pandas as pd
username='prasanth'
password='83f799-3821f9-837e75-2560c3-c63db3'
proxy = {
    'http': 'http://'+username+':'+password+'@global.rotating.proxyrack.net:9000',
    'https': 'http://'+username+':'+password+'@global.rotating.proxyrack.net:9000'
}
current_date = datetime.now().strftime('%d-%m-%Y')
folder_name =f"jsons//{current_date}"
json_path = f"{folder_name}"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}

with open('dogo_production.json', "r") as file:
    urls = json.load(file)
output_json = []
for url in urls:
    product_index = urls.index(url)
    p_cd = url['url'].split("p_cd=")[-1]
    file_path = f"jsons//{current_date}//{p_cd}.json"
    product_url = f'https://www.pokemoncenter-online.com/?p_cd={p_cd}'
    if not os.path.isfile(file_path):
        params = {
            'p_cd': f'{p_cd}',
        }
        print(product_index,product_url)
        response = requests.get('https://www.pokemoncenter-online.com/', params=params, headers=headers,proxies = proxy)
        if response.status_code!=200:
            print("server down , so sleep for 5 minutes")
            print(response.text)
            time.sleep(300)
            response = requests.get('https://www.pokemoncenter-online.com/', params=params, headers=headers,proxies = proxy)
        
        parser = etree.HTMLParser()
        tree = etree.fromstring(response.content, parser)
        error =  tree.xpath('//div[@class="not_found_wrap"]')
        data = {
            "url":product_url,"images": "","price": "","title": "","have_stock": False
        }
        if not error:
            data = {}
            product_details = tree.xpath('//div[@class="item_detail"]')[0]
            images =[]
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
        time.sleep(10)
    else:
        print("Already completed",product_index,product_url)

json_files = glob.glob(f"{folder_name}//*.json")
for json_file in json_files:
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    output_json.append(data)
with open("output_json", "w", encoding="utf-8") as json_file:
    json.dump(output_json,json_file,ensure_ascii=False, indent=2)
print("output json file created")
df = pd.DataFrame(output_json)
excel_filename = 'output.xlsx'
df.to_excel(excel_filename, index=False)

print(f"Data successfully exported to {excel_filename}.")
