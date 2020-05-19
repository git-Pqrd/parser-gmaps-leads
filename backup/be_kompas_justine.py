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
import re
global output_file

# parsing the arg and defining if url or keywords
parser = argparse.ArgumentParser()
parser.add_argument('-n', type=str , default='' , nargs='+' , help='pagination to next')
parser.add_argument('-u', type=str , default='' , nargs='+' , help='page to look')
args = parser.parse_args()
n = 1
if (args.n) : n = args.n[0]
url_tolook = args.u[0]
all_seen = []
output_file = str("kompas_justine" + '.csv')



opts = FirefoxOptions()
# opts.add_argument("--headless") 
driver = webdriver.Firefox(firefox_options=opts)
driver.get(url_tolook)
driver.get("https://be.kompass.com/login")
driver.find_element_by_id("username").send_keys("jordanpasinc@outlook.com")
driver.find_element_by_id("password").send_keys("1996Jordan")
driver.find_element_by_id("login_submit_button").click()
time.sleep(2)
driver.get(url_tolook)
time.sleep(2)
# WebDriverWait(driver, 10 ).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.fouc")))#the  is ok shit can be startedAAA
def proper (string) :
    return re.sub('\s+',' ',string)

def extract_info(soup):
    compagnies = {
            "name":"",
            "address":"",
            "Site web":"",
            "Forme juridique":"",
            "Fax":"",
            "Nummer van de vestigingseenheid":1,
            "position_perso":"",
            "Année de création":"",
            "Nature de l'établissement":""
    }
    try : 
        driver.find_element_by_id("companyMailbox").find_elements_by_class_name("close")[0].click()
        time.sleep(2)
    except : pass

    try : name = proper(soup.find_all("h1", {"itemprop" : "name"})[0].text)
    except : return
    compagnies["name"] = name 

    try : address = proper(soup.find_all("div", class_="addressCoordinates")[0].find_all("p")[0].text.strip())
    except : address = ""
    compagnies["address"] = address 

    caracs = soup.find_all("div", class_="infoGeneral")[0].find_all("tr")
    for carac in caracs: 
        compagnies[carac.find_all("td")[0].text.strip()] = carac.find_all("td")[1].text.strip()

    count_for_loop = 0
    done = False
    for exec_box in soup.find_all("div", class_="executiveInfo") :
        count_for_loop += 1
        if (count_for_loop == 3): break
        try : compagnies["name_exec"] = proper(exec_box.find_all("p", class_="name")[0].text)
        except : compagnies["name_exec"] = "Foo Bar"
        #phone
        try : compagnies["position_perso"] = proper(exec_box.find_all("p", class_="fonction")[0].text)
        except : compagnies["position_perso"]  = "Manager"
        #email
        try : compagnies["lg_perso"] = proper(exec_box.find_all("p", class_="language")[0].text)
        except : compagnies["lg_perso"] = "English"

        with open(output_file , 'a' , newline = '', encoding="utf-16") as f:
            write_in_csv  = csv.DictWriter(f, fieldnames=compagnies.keys())
            write_in_csv.writerow(compagnies)
            print(compagnies["name"])
        done = True

    if  not done : 
        with open(output_file , 'a' , newline = '', encoding="utf-16") as f:
            write_in_csv  = csv.DictWriter(f, fieldnames=compagnies.keys())
            write_in_csv.writerow(compagnies)
            print(compagnies["name"])


def click_and_go(link):
    time.sleep(1)
    try : link.find_elements_by_class_name("kompassImage ")[0].click()
    except ElementNotInteractableException :
        time.sleep(1)
        link.find_elements_by_class_name("kompassImage ")[0].click()

    except ElementClickInterceptedException :
        time.sleep(1)
        link.find_elements_by_class_name("kompassImage ")[0].click()

    html = driver.page_source
    soup = BeautifulSoup (html , 'html.parser')
    if ("Liste d'entreprises" in soup.title ) : 
        click_and_go(link)
    extract_info(soup)
    time.sleep(1)
    if driver.current_url != url_tolook : 
        driver.back()
        if driver.current_url == "https://be.kompass.com/login" or driver.current_url == "https://be.kompass.com/my-account/accountHome/"  :
            driver.forward()

def next_page(page):
    if "page" in url_tolook : 
        driver.get(url_tolook.split("page")[0]+ "page-" + str(page))
    else : 
        driver.get(url_tolook+"page-"+str(page)+"/")
    time.sleep(1)




page = 1
while True :
    try : driver.find_element_by_id("hideCookiesWarning").click()
    except : pass

    business_links = driver.find_elements_by_class_name('product-list-data')
    for i in range(len(business_links)):
        bl = driver.find_elements_by_class_name('product-list-data')
        click_and_go(bl[i])

    page = page + 1
    next_page(page)
    print("Nous sommes à la page : " + str(page))



driver.close()
