import csv
import requests
from bs4 import BeautifulSoup
from csv import DictWriter

# Step 1: Read URLs from CSV file
keyword_site_urls = dict()
with open('D:\\ThinkByte_project\Medibuddy_project\data\med_urls.csv', 'r') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        keyword = row['source2']  # 'source3' is the column containing URLs
        keyword_site_urls[keyword] = {'source2': row['source2']}  # Adjust as per your CSV structure

netmed_responses = dict()

# Step 2: Fetch data from each URL
for keyword in keyword_site_urls:
    url = keyword_site_urls[keyword]['source2']
    response = requests.get(url)
    if response.status_code == 200:
        netmed_responses[keyword] = response.text
        print(f"HTML content fetched for {keyword}.")
    else:
        print(f"Failed to fetch webpage for {keyword}. Status code: {response.status_code}")

# Step 3: Process fetched data
netmeds_data = []

def get_li_p_text(block):
    block_text = ''
    for ddesc in block.children:
        if ddesc.name == 'p':
            block_text += '\n' + ddesc.get_text() + '\n'
        elif ddesc.name == 'ul':
            block_text += '\n'.join(para.get_text() for para in ddesc.find_all('li'))
        elif ddesc.name == 'table':
            table_data = ddesc.find_all('tr')
            for i, data_point in enumerate(table_data):
                data_point = data_point.get_text()
                block_text += data_point + '\n'
    return block_text

for keyword in netmed_responses:
    try:
        soup = BeautifulSoup(netmed_responses[keyword], 'html.parser')
        prod_name = soup.find('div', class_='product-right-block').find('div', class_='prodName').find('h1').get_text()
        content = soup.find('div', class_='left-block').find_all('div', class_='inner-content')
        for block in content:
            try:
                block_title = block.find('h2').get_text()
                # print (block_title)
                if 'INTRODUCTION' in block_title:
                    introduction = '\n'.join(para.get_text() for para in block.find_all('p'))
                elif 'USES OF' in block_title:
                    uses_of = '\n'.join(para.get_text() for para in block.find_all('li'))
                elif 'TABLET WORKS' in block_title:
                    how_it_works = '\n'.join(para.get_text() for para in block.find_all('p'))
                elif 'DIRECTIONS FOR USE' in block_title:
                    dir_of_use = '\n'.join(para.get_text() for para in block.find_all('p'))
                elif 'UNCOMMON' in block_title:
                    uncommon_text = get_li_p_text(block)
                elif 'COMMON' in block_title:
                    common_text = get_li_p_text(block)                    
                elif 'RARE' in block_title:
                    rare_text = get_li_p_text(block)
                elif 'HOW TO MANAGE' in block_title:
                    how_to_manage = '\n'.join(para.get_text() for para in block.find_all('p'))
                elif 'WARNING' in block_title:
                    warning_text = ''
                    headers = block.find_all('h6')
                    content = block.find_all('p')
                    for i, header in enumerate(headers):
                        warning_text += header.get_text() + '\n' + content[i].get_text() + '\n'
                    # print(warning_text)
                elif 'OTHERS' in block_title:
                    others_text = get_li_p_text(block)
                elif 'INTERACTIONS' in block_title:
                    interactions = get_li_p_text(block)
                elif 'SYNOPSIS' in block_title:
                    synopsis = get_li_p_text(block)
                elif 'MORE INFORMATION' in block_title:
                    more_info = get_li_p_text(block)
                elif 'FAQs' in block_title:
                    faqs = get_li_p_text(block)
                elif 'REFERENCES' in block_title:
                    references = get_li_p_text(block)
                elif 'USEFUL DIAGNOSTIC TESTS' in block_title:
                    useful_diagnostic_tests = get_li_p_text(block)
            except Exception as e:
                print(e)
        
        prescript_content_div = soup.find('div', class_='left-block').find_all('div', class_='drug-content')[1].find('div', class_='prescript-txt')
        prescript_content_titles = prescript_content_div.find_all('div', class_='manufacturer_name')
        prescript_content_titles.extend(prescript_content_div.find_all('div', class_='manufacturer_address'))
        prescript_content_data = prescript_content_div.find_all('div', class_='manufacturer__name_value')
        prescript_content_data.extend(prescript_content_div.find_all('div', class_='manufacturer_address_value'))
        for i,t in enumerate(prescript_content_titles):
            continue
            # print (t.get_text())
            # print (prescript_content_data[i].get_text())
        netmeds_row = {
            'prod_name': prod_name,
            'introduction': introduction,
            'uses_of': uses_of,
            'how_it_works': how_it_works,
            'dir_of_use': dir_of_use,
            'uncommon_text': uncommon_text,
            'common_text': common_text,
            'rare_text': rare_text,
            'how_to_manage': how_to_manage,
            'warning_text': warning_text,
            'others_text': others_text,
            'interactions': interactions,
            'synopsis': synopsis, 
            'more_info': more_info,
            'faqs':faqs, 
            'references': references,
            'useful_diagnostic_tests': useful_diagnostic_tests
        }
        netmeds_data.append(netmeds_row)
        # netmeds_dict[keyword] = netmeds_row
    except Exception as e:
        print (e)

# Step 4: Save processed data into a new CSV file
with open('netmeds1_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['prod_name', 'introduction', 'uses_of','how_it_works','dir_of_use','uncommon_text','common_text','rare_text','how_to_manage','warning_text','others_text','warnings','interactions','synopsis','more_info','faqs','references','useful_diagnostic_tests']  # Update with your field names
    writer = DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(netmeds_data)

print("Data saved to netmeds_data.csv.")
