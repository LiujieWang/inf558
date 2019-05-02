from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import json

def find_in_list_of_list(mylist, char):
    for sub_list in mylist:
        if char in sub_list:
            return (mylist.index(sub_list), sub_list.index(char))
    raise ValueError("'{char}' is not in list".format(char = char))

LOAD_MORE_BUTTON_XPATH = '//*[@id="loadMore"]/span'

option = webdriver.ChromeOptions()
option.add_argument(" — incognito")

browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=option)
browser.get("https://www.pokemon.com/us/pokedex/")


# Wait 20 seconds for page to load
timeout = 20
try:
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[4]/section[6]/ul/li[12]/figure/a/img")))

except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()

loadmore = browser.find_element_by_id("loadMore")

action = webdriver.common.action_chains.ActionChains(browser)
action.move_to_element(loadmore)
action.click()
action.perform()
loadmore.click()

SCROLL_PAUSE_TIME = 2

# Get scroll height
last_height = browser.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = browser.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

titles_element = browser.find_elements_by_xpath("/html/body/div[4]/section[6]/ul/li[*]/figure/a")
titles = [x.get_attribute("href") for x in titles_element]

print("number of pokemon",len(titles_element))

filename_json ="/Users/liujiewang/Desktop/pokemon_info.json"

for url in titles:
    browser.get(url)
    soup = BeautifulSoup(browser.page_source)
    base_url = 'https://www.pokemon.com'
    evolution = None
    #title
    name_number = soup.select("div.pokedex-pokemon-pagination-title div")[0].getText().split()
    name = name_number[0]
    number = name_number[1]

    #attribute
    attribute = soup.find_all("span",{"class":"attribute-value"})
    height =attribute[0].getText()
    weight = attribute[1].getText()
    category =attribute[3].getText()
    abilities = attribute[4].getText()

    #type
    type = soup.select("div.pokedex-pokemon-attributes.active div.dtm-type a")
    type_list = [x.getText() for x in type]

    #weakness
    weaknesses = soup.select("div.pokedex-pokemon-attributes.active div.dtm-weaknesses a")
    weaknesses_list =[x.getText().strip() for x in weaknesses]

    #evolution
    select_evolution = soup.select("section.section.pokedex-pokemon-evolution")
    first_list=[]
    middle_list=[]
    last_list=[]
    if select_evolution:
        first = select_evolution[0].select("div ul li.first a")
        middle = select_evolution[0].select("div ul li.middle a")
        last = select_evolution[0].select("div ul li.last a")
        if first: first_list = [base_url+x.attrs['href'] for x in first]
        if middle: middle_list = [base_url+x.attrs['href'] for x in middle]
        if last: last_list = [base_url+x.attrs['href'] for x in last]

    if url in first_list:
        if middle_list:
            evolution = middle_list
        elif last_list:
            evolution = last_list
        else:
            evolution = None
    if url in middle_list:
        if last_list:
            if len(middle_list) == 1:
                evolution = last_list
            else:
                i = middle_list.index(url)
                evolution = last_list[i]

    if url in last_list:
        evolution = None

    json_output ={
    "name":name,
    "number":number,
    "height":height,
    "weight":weight,
    "category":category,
    "abilities":abilities,
    "type":type_list,
    "weaknesses":weaknesses_list,
    "url":url,
    "evolution":evolution
    }

    json_output_str =json.dumps(json_output,indent=4)

    print("current",url)
    print(json_output)

    with open(filename_json, 'a+') as f:
        f.write(json_output_str)
        f.write("\n")


