import requests
from bs4 import BeautifulSoup
import pandas as pd

# Load URLs from CSV file
keyword_site_urls = pd.read_csv('D:\\ThinkByte_project\Medibuddy_project\data\med_urls.csv')

onemg_responses = dict()

headers = {
    'authority': 'www.1mg.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': 'VISITOR-ID=c042f201-ea11-4710-c7f5-680e8b432df4_acce55_1702704046',
    'dnt': '1',
    'referer': 'https://www.1mg.com/categories/vitamin-supplements/vitamin-d-121',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for index, row in keyword_site_urls.iterrows():
    url = row['source1']
    keyword = row.get('keyword', '')  # Get keyword if available, otherwise use empty string
    # Sending a GET request to the URL
    response = requests.get(url, headers=headers)
    # Checking if the request was successful
    if response.status_code == 200:
        onemg_responses[keyword] = response.text
        print("HTML content fetched and saved.")
    else:
        print(f"Failed to fetch webpage. Status code: {response.status_code}")

omemg_data = []
onemg_dict = dict()

for keyword in onemg_responses:
    try:
        soup = BeautifulSoup(onemg_responses[keyword], 'html.parser')
        
        drug_title = soup.find_all('h1', class_=lambda value: value and value.startswith('DrugHeader__title-content'))[0].get_text()
        drug_marketer = soup.find_all('div', class_=lambda value: value and value.startswith('DrugHeader__meta-value'))[0].get_text()
        salt_info = soup.find_all('div', 'saltInfo')[0].get_text()
        salt_synonms = soup.find_all('div', 'saltInfo')[1].get_text()
        try:
            storage = soup.find_all('div', 'saltInfo')[2].get_text()
        except:
            storage = salt_synonms
            salt_synonms = ''
        product_info = soup.find_all('div', class_=lambda value: value and value.startswith('DrugOverview__content'))[0].get_text()
        try:
            drug_uses_div = soup.find_all('ul', class_=lambda value: value and value.startswith('DrugOverview__list'))[0]
            drug_uses = '\n'.join(para.get_text() for para in drug_uses_div.find_all('li'))
            drug_benefits_children = soup.find_all('div', class_=lambda value: value and value.startswith('ShowMoreArray__tile'))[0]

            drug_benefits_div = drug_benefits_children.children
            drug_benefits = ''
            for child in drug_benefits_div:
                benefit = child.get_text()
                if benefit:
                    drug_benefits += benefit + '\n\n'
        except:
            drug_uses = ''
            drug_benefits = ''
        
        try:
            side_effects_div = soup.find('div', id='side_effects')
            side_effects_text = side_effects_div.find_all('div', class_=lambda value: value and value.startswith('DrugOverview__content'))[0].get_text()
            side_effects_list_div = side_effects_div.find_all('div', class_=lambda value: value and value.startswith('DrugOverview__content'))[1]
            side_effects_list = '\n'.join(para.get_text() for para in side_effects_list_div.find_all('li'))
        except:
            side_effects_text = ''
            side_effects_list = ''
            
        how_to_use = soup.find('div', id='how_to_use').get_text()
        how_drug_works = soup.find('div', id='how_drug_works').get_text()
        
        safety_advice_div = soup.find('div', id='safety_advice').find_all('div', class_=lambda value: value and value.startswith('DrugOverview__content'))[0]
        drug_overview_warnings_div = safety_advice_div.find_all('div', class_=lambda value: value and value.startswith('DrugOverview__warning-top'))
        drug_warnings_descs = safety_advice_div.find_all('div', class_=lambda value: value and value.startswith('DrugOverview__content'))
        
        safety_advice = ''
        for i, warning_div in enumerate(drug_overview_warnings_div):
            warning_title = warning_div.find('span').get_text()
            warning_tag = warning_div.find('div', class_=lambda value: value and value.startswith('DrugOverview__warning-tag')).get_text()
            warning_desc = drug_warnings_descs[i].get_text()
            safety_advice += 'Title:'+ warning_title + '\n' + 'Tag:' + warning_tag + 'Description:' + warning_desc
        try:
            missed_dose = soup.find('div', id='missed_dose').get_text()
        except:
            missed_dose = ''
        
        try:
            substitutes_div = soup.find('div', id='substitutes')
            substitutes =  substitutes_div.find_all('div', class_=lambda value: value and value.startswith('SubstituteItem__item'))
            substitutes_text = ''
            for row in substitutes:
                sub_name = row.find('div', class_=lambda value: value and value.startswith('SubstituteItem__name')).get_text()
                sub_manc_name = row.find('div', class_=lambda value: value and value.startswith('SubstituteItem__manufacturer-name')).get_text()
                substitutes_text += 'Substitute Name: '+ sub_name +'\n Manufacturer Name: '+ sub_manc_name + '\n\n'
        except:
            substitutes_text = ''
        
        quick_tips_arr = soup.find('div', id='expert_advice').find('ul')
        quick_tips = '\n'.join(para.get_text() for para in quick_tips_arr.find_all('li'))
        fact_box_left_arr = soup.find('div', id='fact_box').find_all('div', class_=lambda value: value and value.startswith('DrugFactBox__col-left'))
        fact_box_right_arr = soup.find('div', id='fact_box').find_all('div', class_=lambda value: value and value.startswith('DrugFactBox__col-right'))

        facts = ''
        for i, fact in enumerate(fact_box_left_arr):
            fact_tag = fact.get_text()
            fact_detail = fact_box_right_arr[i].get_text()
            facts += fact_tag + ':' + fact_detail + '\n'
        try:
            
            drug_interaction = soup.find('div', id='drug_interaction')
            drug_interaction_desc = drug_interaction.find_all('div', class_=lambda value: value and value.startswith('DrugInteraction__desc'))
            
            drug_interaction_content = drug_interaction.find('div', class_=lambda value: value and value.startswith('DrugInteraction__content'))
            drug_interaction_rows = drug_interaction_content.find_all('div', class_=lambda value: value and value.startswith('DrugInteraction__row'))

            drug_interactions_text = ''
            for di_row in drug_interaction_rows:
                di_drug = di_row.find('div', class_=lambda value: value and value.startswith('DrugInteraction__drug')).get_text()
                di_brands = di_row.find('div', class_=lambda value: value and value.startswith('DrugInteraction__brands')).get_text()
                di_interaction = di_row.find('div', class_=lambda value: value and value.startswith('DrugInteraction__interaction')).get_text()
                drug_interactions_text += 'Drug:' + di_drug + '\n Brands:' + di_brands + '\nInteraction:' + di_interaction + '\n\n'
        except:
            drug_interactions_text = ''
        
        faq_div = soup.find('div', id='faq')
        faq_ques_div = faq_div.find_all('h3', class_=lambda value: value and value.startswith('Faqs__ques'))
        faq_ans_div = faq_div.find_all('div', class_=lambda value: value and value.startswith('Faqs__ans'))
        faqs = ''
        for i, ques_block in enumerate(faq_ques_div):
            ques = ques_block.get_text()
            ans = faq_ans_div[i].get_text()
            faqs += ques + '\n' + ans + '\n\n'
        
        disclaimer = soup.find('div', class_=lambda value: value and value.startswith('DrugPage__auxiliary')).get_text()
        references_div = soup.find('ol', class_=lambda value: value and value.startswith('DrugPage__reference'))
        compliance_info =soup.find('div', class_=lambda value: value and value.startswith('DrugPage__compliance-info')).get_text()


        onemg_row = {
            'keyword': keyword,
            'drug_title': drug_title,
            'drug_marketer': drug_marketer,
            'salt_info': salt_info,
            'salt_synonms': salt_synonms,
            'storage': storage,
            'salt_synonms': salt_synonms,
            'product_info': product_info,
            'drug_uses':drug_uses,
            'drug_benefits': drug_benefits,
            'side_effects_text': side_effects_text,
            'side_effects_list': side_effects_list,
            'how_to_use': how_to_use,
            'how_drug_works': how_drug_works,
            'safety_advice': safety_advice,
            'missed_dose': missed_dose,
            'substitutes_text': substitutes_text,
            'quick_tips_arr': quick_tips,
            'facts': facts,
            'drug_interaction_text': drug_interactions_text,
            'faqs': faqs,
            'disclaimer': disclaimer,
            'references_div': references_div,
            'compliance_info':compliance_info,
            
        }
        omemg_data.append(onemg_row)
        onemg_dict[keyword] = onemg_row
        
    except Exception as e:
        print(e)

# Convert omemg_data to DataFrame
onemg_df = pd.DataFrame(omemg_data)

# Save DataFrame to CSV
onemg_df.to_csv('/data/onemg_data.csv', index=False)
        
# f = open('/tmp/omemg.csv', 'w')
# writer = DictWriter(f, fieldnames = omemg_data[0].keys())
# writer.writeheader()
# writer.writerows(omemg_data)
