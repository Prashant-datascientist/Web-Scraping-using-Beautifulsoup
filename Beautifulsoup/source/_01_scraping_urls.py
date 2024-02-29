# Importing Required libraries
import requests
from bs4 import BeautifulSoup
from csv import DictWriter

# Creating a google search engine with custom Query


med_names = list()

# Passing the medicines name
with open('/tmp/med_names.txt', 'r') as f:
    med_names = f.readlines()


def google_search(query, api_key, cx):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cx
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            search_results = data["items"]
            return search_results
        else:
            return []
    else:
        print("Error: Unable to perform the search.")
        return []

# Replace these variables with your actual API key and custom search engine ID (cx)
api_key = "AIzaSyDn7Mxf9Jy_Pjvk9i3oNHARh2wjNVdZzkQ"
cx = "d06be8dbe6a4c4c97"

# getting the result from goole search fun
google_results = dict()
for name in med_names:
    results = google_search(name, api_key, cx)

    if results:
        for result in results:
            title = result["title"]
            link = result["link"]
            print(f"Title: {title}")
            print(f"Link: {link}")
            print("---")
        google_results[name] = results
    else:
        print("No results found.")
        

## filtering site result available in search reasult or not?
keyword_site_urls = dict()
for name in google_results:
    site_urls = dict()
    for result in google_results[name]:
        if 'pharmeasy'in result['link']:
            site_urls['pharmeasy'] = result['link']
        elif 'apollopharmacy'in result['link']:
            site_urls['apollopharmacy'] = result['link']
        elif 'netmeds'in result['link']:
            site_urls['netmeds'] = result['link']
        elif '1mg'in result['link']:
            site_urls['1mg'] = result['link']
    keyword_site_urls[name] = site_urls


site_urls_list = []

for keyword in keyword_site_urls:
    site_urls_list.append({
        'keyword': keyword,
        'source1': keyword_site_urls[keyword].get('1mg', ''),
        'source2': keyword_site_urls[keyword].get('netmeds', ''),
        'source3': keyword_site_urls[keyword].get('apollopharmacy', ''),
    })

with open('/data/keyword_urls.csv', 'w', newline='') as f:
    writer = DictWriter(f, fieldnames=site_urls_list[0].keys())
    writer.writeheader()
    writer.writerows(site_urls_list)
