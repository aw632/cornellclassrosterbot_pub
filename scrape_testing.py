import requests
import re
from bs4 import BeautifulSoup

dep = 'MATH'
num = 3360

def main():
    url = 'https://classes.cornell.edu/browse/roster/SP21/class/' + f'{dep}/{num}'
    r = requests.get(url)
    content = r.content

    soup = BeautifulSoup(content, 'html.parser')

    full_class_name = soup.find(class_='title-coursedescr').get_text()

    full_class_descr = soup.find(class_='catalog-descr').get_text().strip()
    trun_class_descr = (full_class_descr[:168] + '..') if len(full_class_descr) > 168 else full_class_descr

    spans = soup.find_all('span', {'class' : 'tooltip-iws'})
    prof_name_netid = spans[6]['data-content']

    credit_num = soup.find('span', {'class' : 'credit-val'}).get_text()

    distr_req = soup.find('span', {'class' : 'catalog-distr'}).get_text().replace('Distribution Category', 'Satified Requirements:')

    when_offered = soup.find('span', {'class' : 'catalog-when-offered'}).get_text().replace('When Offered', '').strip().replace('.', '')
    prereq = soup.find('span', {'class' : 'catalog-prereq'}).get_text().replace(' Prerequisite', '').strip().replace('.', '')

    # print(full_class_name)
    # print(full_class_descr)
    # print(prof_name_netid)
    #print(credit_num)
    # print(distr_req)
    # print(trun_class_descr)
    # print(soup)
    # print(when_offered)
    print(prereq)

if __name__ == '__main__':
    main()
