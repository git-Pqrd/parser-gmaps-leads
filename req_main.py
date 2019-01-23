from bs4 import BeautifulSoup
import time
# import requests
import csv
# import sys

from selenium import webdriver
from selenium.webdriver import FirefoxOptions


# Here, we're just importing both Beautiful Soup and the Requests library
opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(firefox_options=opts)
driver.get("http://www.uvcw.be/communes/liste-communes.htm")
time.sleep(0.5)
page_response = driver.page_source

# this is the url that we've already determined is safe and legal to scrape from.


# here, we fetch the content from the url, using the requests library

page_content = BeautifulSoup(page_response, "html.parser")
#we use the html parser to parse the url content and store it in a variable.


commune = []
table_exp = page_content.find_all("div", class_="list")[0]

list_exp = table_exp.find_all("div", class_="list-item")

coms = []
for i in list_exp:
    try : name_ent = i.find_all("p", class_="title")[0].text
    except : pass

    try : address = i.find_all("p", class_="desc")[0].text.replace("\n", "|").replace(" ", "")
    except : pass

    try : phone = i.find_all("p", class_="date")[0].text.replace(" ", "").split("\n")[0]
    except : pass

    try : email = i.find_all("p", class_="date")[0].find_all("a")[0].text
    except : pass

    try : website = email.split("@")[1]
    except : pass

    coms.append({"name_ent":name_ent,"address":address,"phone":phone,"email":email,"website":website})


print("done now creating the file")
with open('entreprisesEXPOWEST.csv', 'w', newline='') as csvfile:
    fieldnames=["name_ent", "address", "phone", "email", "website"]
    writer = csv.DictWriter(csvfile, delimiter=";", fieldnames=fieldnames)
    writer.writeheader()
    for n in coms :
        print (n)
        writer.writerow(n)
