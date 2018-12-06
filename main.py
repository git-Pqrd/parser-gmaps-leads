import csv 
import argparse , time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException ,ElementClickInterceptedException, ElementNotInteractableException #StaleElementReferenceException, 
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# import subprocess
# subprocess.call("export DISPLAY=:0.0", shell=True)
global output_file

# parsing the arg and defining if url or keywords
parser = argparse.ArgumentParser()
parser.add_argument('-o', type=str , help='output file name without .csv at the end')# getting the mandatory output file
parser.add_argument('-p', type=str , default='' ,  nargs='+' , help='location to look')
parser.add_argument('-b', type=str , default='' , nargs='+' , help='business to search')
parser.add_argument('-u', type=str , default='' , nargs='+' , help='business to search')
args = parser.parse_args()
url_tolook = args.p + args.b
url_tolook = '+'.join(url_tolook)
url_tolook = 'https://www.google.com/maps/search/' + "+".join(args.p) + "+" +  "+".join(args.b) 
if (args.u) : 
    url_tolook = args.u[0] 

output_file = str(args.o + '.csv')


opts = FirefoxOptions()
# optsadd_argument("--headless")
driver = webdriver.Firefox(firefox_options=opts)
driver.get(url_tolook) 
WebDriverWait(driver, 5 ).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-result-details-container")))#the  is ok shit can be startedAAA

def extract_info(soup):
    name = soup.find_all( 'h1' , class_='section-hero-header-title')[0].text
    add_l = soup.find_all('span' , class_='maps-sprite-pane-info-address')
    web_l = soup.find_all('span' , class_='maps-sprite-pane-info-website')
    pho_l = soup.find_all('span' , class_='maps-sprite-pane-info-phone')
    try : 
        address  = add_l[0].parent.text #.encode("utf-8")
        website = web_l[0].parent.text #.encode("utf-8")
        phone = pho_l[0].parent.text #.encode("utf-8")
    except :
        return 

    if not "." in website :
        return

    if website in web_seen:
        return 
    web_seen.append(website)

    print (address + '  ' + website + '  ' + phone)
    with open(output_file , 'a' , newline = '') as f:
        write_in_csv  = csv.writer(f)
        write_in_csv.writerow([name, website , address , phone  ])

def click_and_go(link):
    time.sleep(1)
    try :
        link.click()
    except ElementNotInteractableException : 
        time.sleep(3)
        link.click()

    WebDriverWait(driver, 10 ).until(EC.presence_of_element_located((By.CLASS_NAME, "section-hero-header-title")))
    html = driver.page_source
    soup = BeautifulSoup (html , 'html.parser')
    extract_info(soup)
    time.sleep(2)#software work even I do not wait just no risk ban
    back_btn = driver.find_elements_by_class_name("section-back-to-list-button.blue-link.noprint")[0]
    back_btn.click()
    WebDriverWait(driver, 10 ).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-result-details-container")))#the  is ok shit can be startedAAA

web_seen = []
while True : 
    business_links = driver.find_elements_by_class_name('section-result')
    for i in range(len(business_links)):
        freshBL = driver.find_elements_by_class_name('section-result')
        click_and_go(freshBL[i])

    next_btn = driver.find_elements(By.XPATH,"//*[contains(@id,'section-pagination-button-next')]")[0]
    print(driver.find_elements(By.XPATH,"//*[@id='pane']/div/div[1]/div/div/div[3]/div/div[2]/span/span[1]")[0].text)
    try :
        time.sleep(1)
        next_btn.click()
        print(driver.find_elements(By.XPATH,"//*[@id='pane']/div/div[1]/div/div/div[3]/div/div[2]/span/span[1]")[0].text)

    except ElementClickInterceptedException : 
        driver.find_elements(By.XPATH,'//*[@id="consent-bump"]/div/div[2]/span/button[1]')[0].click()
        time.sleep(2)
        next_btn.click()

    except NoSuchElementException :
        print("Done")
        break 

driver.close()
