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
parser.add_argument('-o', type=str , help='output file name without .csv at the end')# getting the mandatory output file
parser.add_argument('-p', type=str , default='' ,  nargs='+' , help='location to look')
parser.add_argument('-b', type=str , default='' , nargs='+' , help='business to search')
parser.add_argument('-u', type=str , default='' , nargs='+' , help='business to search')
parser.add_argument('-n', type=str , default='' , nargs='+' , help='pagination to next')
parser.add_argument('-c', type=str , default='web' , nargs='+' , help='carac not to double')# or name
args = parser.parse_args()
url_tolook = args.p + args.b
url_tolook = '+'.join(url_tolook)
url_tolook = 'https://www.google.com/maps/search/' + "+".join(args.p) + "+" +  "+".join(args.b)
if (args.u) :
    url_tolook = args.u[0]

if (args.n) :
    n = int(args.n[0])
else :
    n = 0

output_file = str(args.o + '.csv')
carac_seen = []
if os.path.isfile(output_file):
    print("file present adding")
    with open(output_file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            if (args.c[0] == "web"): 
                print(row[1])
                carac_seen.append(row[1])
            else : 
                carac_seen.append(row[0])
                print(row[0])


opts = FirefoxOptions()
# opts.add_argument("--headless") #export DISPLAY=:0.0
driver = webdriver.Firefox(firefox_options=opts)
driver.get(url_tolook)
WebDriverWait(driver, 5 ).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-result-details-container")))#the  is ok shit can be startedAAA

def extract_info(soup):
    add_l = soup.find_all('span' , class_='maps-sprite-pane-info-address')
    web_l = soup.find_all('span' , class_='maps-sprite-pane-info-website')
    pho_l = soup.find_all('span' , class_='maps-sprite-pane-info-phone')
    try :
        name = soup.find_all( 'h1' , class_='section-hero-header-title')[0].text
        address  = add_l[0].parent.text #.encode("utf-8")
        website = web_l[0].parent.text #.encode("utf-8")
        phone = pho_l[0].parent.text #.encode("utf-8")
    except :
        return
    
    if (args.c[0] == "web"):
        if not "." in website : return
        if website in carac_seen : return
        carac_seen.append(website)
    else : 
        if name in carac_seen : return
        carac_seen.append(name)

    print (address + '  ' + website + '  ' + phone)
    with open(output_file , 'a' , newline = '') as f:
        write_in_csv  = csv.writer(f)
        write_in_csv.writerow([name, website , address , phone  ])

def click_and_go(link):
    time.sleep(1)
    try : link.click()
    except ElementNotInteractableException :
        time.sleep(3)
        link.click()

    except ElementClickInterceptedException :
        time.sleep(2)
        link.click()

    time.sleep(1)
    # WebDriverWait(driver, 10 ).until(EC.presence_of_element_located((By.CLASS_NAME, "section-hero-header-title")))
    html = driver.page_source
    soup = BeautifulSoup (html , 'html.parser')
    extract_info(soup)
    #time.sleep(2)software work even I do not wait just no risk ban
    try : back_btn = driver.find_elements_by_class_name("section-back-to-list-button")[0]
    except :
        time.sleep(1)
        back_btn = driver.find_elements_by_class_name("section-back-to-list-button")[0]
        
    back_btn.click()
    WebDriverWait(driver, 10 ).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-result-details-container")))


def next_page():
    time.sleep(2)
    try : driver.find_elements(By.XPATH,'//*[@id="consent-bump"]/div/div[2]/span/button[1]')[0].click()
    except : pass
    try: next_btn = driver.find_elements(By.XPATH,"//*[contains(@id,'section-pagination-button-next')]")[0]
    except : next_btn = driver.find_element(By.XPATH,"//*[contains(@id,'section-pagination-button-next')]")
    try :
        next_btn.click()
        print("changing page")
    except ElementClickInterceptedException : next_page()
    except NoSuchElementException as e :
        print("over")
        driver.close()
        raise e


while True :
    for i in range(n) : next_page()
    n = 0

    business_links = driver.find_elements_by_class_name('section-result')
    for i in range(len(business_links)):
        freshBL = driver.find_elements_by_class_name('section-result')
        try : click_and_go(freshBL[i])
        except : continue


    try :
        number_left = int(driver.find_element(By.XPATH,"//*[@id='pane']/div/div[1]/div/div/div[4]/div/div[2]/span/span[2]").text)
        if number_left % 20 != 0 : break
    except : pass

    next_page()



driver.close()
