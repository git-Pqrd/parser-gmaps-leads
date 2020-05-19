import csv
import argparse , time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException ,ElementClickInterceptedException, ElementNotInteractableException #StaleElementReferenceException,
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os.path
global output_file

# parsing the arg and defining if url or keywords
parser = argparse.ArgumentParser()
parser.add_argument('-n', type=str , default='' , nargs='+' , help='pagination to next')
parser.add_argument('-o', type=str , default='' , nargs='+' , help='output file')
args = parser.parse_args()
n = 1
if (args.n) : n = args.n[0]
url_tolook = 'https://ideta.be/annuaire/page/' + str(n)
all_seen = []
output_file = str("idetajustine" + '.csv')



opts = FirefoxOptions()
# opts.add_argument("--headless") 
driver = webdriver.Firefox(firefox_options=opts)
driver.get(url_tolook)
WebDriverWait(driver, 10 ).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.fouc")))#the  is ok shit can be startedAAA

def extract_info(soup):
    sidebar = soup.find_all("aside", class_="person entreprise")[0]
    try : sb = sidebar.find_all("div", class_="content")[0]
    except : return
    try : adds = sidebar.find_all("div", class_="additional")[0]
    except : pass

    ##general
    #name 
    try : name_gen = soup.find_all("div", class_="wysiwyg")[0].find_all("h1", class_="title")[0].text.strip().replace("\xa0", " ")
    except : return
    #addresse
    try : add_gen = sb.find_all("div", class_="address")[0].text.strip().replace("\xa0", " ")
    except : return
    #phone
    try : phone_gen = sb.find_all("div", class_="content")[0].text.strip().replace("\xa0", " ")
    except : phone_gen = "0000000000"
    #tva
    try : tva_gen = sb.find_all("div", class_="address")[-1].text.strip().replace("\xa0", " ")
    except : tva_gen = "000.000.000.0"
    #email
    try : email_gen = sb.find_all("div", class_="item fouc")[0].find_all("a")[0].text.strip().replace("\xa0", " ")
    except : return

    ##perso
    #addresse
    try :
        for add in sidebar.find_all("div", class_="additional") :
            try : name_perso = add.find_all("div", class_="name")[0].text.strip().replace("\xa0", " ")
            except : name_perso = "foo bar"
            print(name_perso)
            #phone
            try : position_perso = add.find_all("p", class_="titre")[0].text.strip().replace("\xa0", " ")
            except : position_perso = "not known"
            print(position_perso)
            #email
            try : email_perso = sb.find_all("div", class_="item fouc")[0].find_all("a")[0].text.strip().replace("\xa0", " ")
            except : email_perso = "b@b.com"
            print(email_perso)

            with open(output_file , 'a' , newline = '', encoding="utf-16") as f:
                write_in_csv  = csv.writer(f)
                print([name_gen, add_gen , phone_gen , tva_gen, email_gen, name_perso, position_perso, email_perso, ])
                write_in_csv.writerow([name_gen, add_gen , phone_gen , tva_gen, email_gen, name_perso, position_perso, email_perso, ])

    except : #no businesss rep
        with open(output_file , 'a' , newline = '') as f:
            write_in_csv  = csv.writer(f)
            print([name_gen, add_gen , phone_gen , tva_gen, email_gen])
            write_in_csv.writerow([name_gen, add_gen , phone_gen , tva_gen, email_gen])


def click_and_go(link):
    time.sleep(1)
    try : link.click()
    except ElementNotInteractableException :
        time.sleep(1)
        link.click()

    except ElementClickInterceptedException :
        time.sleep(1)
        link.click()

    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup (html , 'html.parser')
    extract_info(soup)
    driver.back()

def next_page():
    try : pagination_btn = driver.find_elements_by_class_name("pagination")[0].find_elements_by_tag_name("li")
    except : 
        driver.back()
        pagination_btn = driver.find_elements_by_class_name("pagination")[0].find_elements_by_tag_name("li")

    for btn in pagination_btn : if btn.text == "›" : next_btn = btn 
    next_btn.click()


page = 1
while True :
    try : 
        driver.find_elements_by_class_name("mkCookieBanner")[0].find_elements_by_class_name("cookie__accept")[0].click()
        time.sleep(1)
    except : pass

    business_links = driver.find_elements_by_tag_name('article')
    for i in range(len(business_links)):
        bl = driver.find_elements_by_tag_name('article')
        src_thumbn = bl[i].find_elements_by_class_name('hide-for-print')[0].get_attribute("src")
        print(src_thumbn)
        if "placeholder" in src_thumbn : continue
        if src_thumbn in all_seen : continue
        all_seen.append(src_thumbn)
        click_and_go(bl[i])

    page += 1
    next_page()
    print("Nous sommes à la page : " + str(page))



driver.close()
