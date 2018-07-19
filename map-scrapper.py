import csv , argparse , urllib.request, sys  , time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  
from selenium.common.exceptions import NoSuchElementException , StaleElementReferenceException
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


# here iam handling the args parsing for the command line
parser = argparse.ArgumentParser()
parser.add_argument('-p', type=str , default='' ,  nargs='+' , help='location to look')
parser.add_argument('-b', type=str , default='' , nargs='+' , help='business to search')
parser.add_argument('-o', type=str , help='output file name without .csv at the end')
args = parser.parse_args()
global output_file
output_file = str(args.o + '.csv')

# here i am creating a string to look to for info
url_tolook = args.p + args.b
url_tolook = '+'.join(url_tolook)
url_tolook = 'https://www.google.com/maps/search/' + url_tolook
 
 # iam loading the driver and looking it up
options = Options()
driver = webdriver.Firefox( firefox_options=options)
driver.get(url_tolook)  


driver_home = driver.title
global done
global only_one
global count 
count = 0
only_one = False

# difference between seen and seen companies is that seen is for troubleshooting
# where as seen_companies is to avoid having two succursales
seen = []
seen_companies = []
done = False
# verify if the list of infos is loaded
def verify_len( ):
    global business_links
    global on_list
    global count
    global done 
    global only_one
    business_links = driver.find_elements_by_class_name('section-result')
    try :
        on_list = int(driver.find_element_by_xpath("//div[@class='section-pagination-right']/span/span[last()]").text)
    except (NoSuchElementException):
        only_one = True
        html = driver.page_source
        soup = BeautifulSoup (html , 'html.parser')
        extract_info(soup)
        
    remaining = on_list % 20
    if remaining == 0 :
        remaining = 20
    for i in business_links:
        if done == True : 
            print ('breaking')
            sys.exit()
        if (len(business_links) != remaining ) :
            time.sleep(1)   

            verify_len( )
        else :
            main(business_links )
    
# verify if we truly are on the good page
# because selenium verification system is massively retarded
def verify_one_on_page(class_name, elem_to_go):
    elem_to_check = driver.find_elements_by_class_name(class_name)
    if len(elem_to_check) != 1 :
        if home_page():
            # print('on home')
            go_business(elem_to_go)
        time.sleep(.5)
        print('not on home can\'t find back') 
        verify_one_on_page(class_name, elem_to_go)


def verify_all_on_page(class_name):
    global on_list
    global business_links

    remaining = on_list % 20
    if remaining == 0 :
        remaining = 20
    if ( len(business_links)  != remaining )  :
        time.sleep(.5)
        verify_all_on_page(class_name)


def ready_info(elem_to_go):
    if home_page():
        go_business(elem_to_go)
    html = driver.page_source
    soup = BeautifulSoup( html , 'html.parser')
    name = soup.find_all( 'h1' , class_='section-hero-header-title')
    if len(name) > 0:
        extract_info(soup)
    else :
        time.sleep(1)
        ready_info(elem_to_go)


def extract_info(soup):
    global only_one
    global seen_companies
    name = soup.find_all( 'h1' , class_='section-hero-header-title')[0].text
    html = driver.page_source
    soup = BeautifulSoup( html , 'html.parser')
    if name not in seen_companies:
        seen_companies.append(name)
        
        # finding the description of the company and making sure the soup has loaded all neces
        desc_l = soup.find_all('div' , class_='section-editorial-quote')
        if len(desc_l) == 0:
            time.sleep(.5)
            extract_info(soup)
        else : 
            desc_l = soup.find_all('div' , class_='section-editorial-quote')[0].text
         
        # finding all the list of cat to see if already loaded
        cat_l = soup.find_all('span' , class_='section-rating-term')
        if  len(cat_l) == 0:
            time.sleep(.5)
            extract_info(soup)

        else : 
            category = soup.find_all('span' , class_='section-rating-term')[0].text

        add_l = soup.find_all('span' , class_='maps-sprite-pane-info-address')
        web_l = soup.find_all('span' , class_='maps-sprite-pane-info-website')
        pho_l = soup.find_all('span' , class_='maps-sprite-pane-info-phone')
        if  len(web_l) + len(add_l) + len(pho_l) == 0:
            time.sleep(.5)
            extract_info(soup)
        else : 
            address  = add_l[0].parent.text.encode("utf-8")
            website = web_l[0].parent.text.encode("utf-8")
            phone = pho_l[0].parent.text.encode("utf-8")
            
        with open(output_file , 'a' , newline = '') as f:
            write_in_csv  = csv.writer(f)
            write_in_csv.writerow([name , category , website , address , phone ])
    if only_one :
        sys.exit()

def home_page() : 
    if driver.title == driver_home:
        return True
    else : 
        return False


def go_back(elem_to_go):
    
    try :
        back_btn = driver.find_element_by_class_name('section-back-to-list-button')
        back_btn.send_keys('\n')
    except (NoSuchElementException,  StaleElementReferenceException) :
        print('not there ... trying redefine we at : ' + driver.title)
        time.sleep(1)
        go_back(elem_to_go)


def go_business(elem_to_go):
    global seen
    global business_links
    global count
    if elem_to_go in  seen:
        main (business_links )
    else : 
        seen.append(elem_to_go) 
        try :
            elem_to_go.send_keys('\n') 
        except (NoSuchElementException, StaleElementReferenceException) :
            business_links = driver.find_elements_by_class_name('section-result')
            time.sleep(1)
            main(business_links )


def next_page( ):
    global count
    try :
        page_to_go = driver.find_element_by_class_name('section-pagination-button-next')
        page_to_go.click()
        verify_len( )
    except (NoSuchElementException,  StaleElementReferenceException) :
        print ('wait next page available')
        time.sleep(1)
        next_page( )

    before_page_num = int(driver.find_element_by_xpath("//div[@class='section-pagination-right']/span/span[last()]").text)
    after_page_num = int(driver.find_element_by_xpath("//div[@class='section-pagination-right']/span/span[last()]").text)
    if before_page_num == after_page_num :
        time.sleep(2)
        if before_page_num == after_page_num  :
            next_page( )


# go to the page for every business
def main(business_links):
    global count
    global done
    verify_all_on_page('section-result')
# wating and doing op to load all the info taking the html and clearing the driver   
    out_of_range = False

    while out_of_range == False :
        try :
            elem_to_go = business_links[count]
            out_of_range = True
        except IndexError : 
            time.sleep(3)
  

    go_business(elem_to_go)
    ready_info(elem_to_go)
    verify_one_on_page('section-back-to-list-button' , elem_to_go)
    go_back(elem_to_go)
    count = count + 1
    print ('--loop nmbr :' + str(count) + ' out of ' + str(len(business_links)) )
    if count ==  len(business_links) :
        count = 0
        if (on_list % 20) != 0 :
            print ('Done !!!')
            done = True 
            verify_len()
        next_page()
        
        
verify_len()

driver.close()  
