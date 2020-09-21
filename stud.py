from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import login

url = "https://signin.intra.42.fr/users/sign_in"
url_log = "https://stud42.fr/users/auth/marvin"

def init_session():
	driver = webdriver.Firefox()
	# option.add_argument(“ — incognito”)
	driver.get(url)
	return driver

def site_login(driver):
	driver.get(url)
	driver.find_element_by_id('user_login').send_keys(login["user"])
	driver.find_element_by_id ('user_password').send_keys(login["password"])
	print( driver.find_elements_by_xpath("//input[@class='btn btn-login']"))
	driver.find_elements_by_xpath("//input[@class='btn btn-login' and @value='Sign in']")[0].click()


def access_calendar(driver, link):
    driver.get(link)
    driver.find_element_by_link_text('Subscribe to defense').click()
    return None
    xpath_calendar = "/html/body/div[4]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div[5]/a"
    xpath_cal_doss = "/html/body/div[4]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div[5]/a"
    driver.find_elements_by_xpath(xpath_calendar).click()

def get_slots(driver):
    xpath_date = lambda day: "/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]/div/table/thead/tr/td/div/table/thead/tr/th[" + str(day) + "]"
    xpath_slot = lambda day, slot: "/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[" + str(day + 2) + "]/div/div[2]/a[" + str(slot) + "]/div[1]/div[1]"
    slots_tab = []
    for day in range(7):
        j = 1
        while 1:
            try:
                res = driver.find_elements_by_xpath(xpath_slot(day, j))
                print(res.getText())
                j += 1
            except:
                break

                


#find_element(driver)
# driver.close()
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ", sys.argv[0] + " " + "link_to_project")
    else:
        driver = init_session()
        site_login(driver)
        access_calendar(driver, sys.argv[1])
        get_slots(driver)

    
