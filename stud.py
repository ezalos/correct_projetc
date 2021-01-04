from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import login
from selenium.webdriver.common.action_chains import ActionChains

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
	xpath_date = lambda day: "/html/body/div[4]/div[2]/div/div[2]/div/div[2]/div/table/thead/tr/td/div/table/thead/tr/th[" + str(day + 2) + "]"
	xpath_hour = lambda hour: "/html/body/div[4]/div[2]/div/div[2]/div/div[2]/div/table/tbody/tr/td/div/div/div[2]/table/tbody/tr[" + str(hour) + "]"
	xpath_slot = lambda day, slot: "/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[" + str(day + 2) + "]/div/div[2]/a[" + str(slot) + "]/div[1]/div[1]"
								   # "/html/body/div[4]/div[2]/div/div[2]/div[1]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td["                  "]/div/div[2]/a[2]"
	xpath_slot_time = lambda day, slot: "/html/body/div[4]/div[2]/div/div[2]/div/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[" + str(day + 2) + "]/div/div[2]/a[2]/div[1]/div[1]"
	slots_tab = [[None for day in range(7 + 1)] for hour in range(48 + 1)]
	for day in range(7):
		for d in driver.find_elements_by_xpath(xpath_date(day)):
			slots_tab[0][day + 1] = str(d.get_attribute("data-date")) + " " + d.text[:3]
		for h in range(1, 48 + 1):
			try:
				for hh in driver.find_elements_by_xpath(xpath_hour(h)):
					slots_tab[h][0] = str(hh.get_attribute("data-time"))
				for slot in driver.find_elements_by_xpath(xpath_slot(day, h)):
					print(slot)
					print(slot.text)
					slots_tab[h][day + 1] = slot
			except Exception as e:
				print("Exception occured!")
				print("\tDay: ", day)
				print("\th: ", h)
				print(e)
				break
	fancy_print(slots_tab)
	return(slots_tab)

# 2 first slots on the 7th day, in my user calendar slots (Not clickable, i guess)
# /html/body/div[4]/div[2]/div/div[2]/div/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[8]/div/div[2]/a[2]/div[1]/div[1]
# /html/body/div[4]/div[2]/div/div[2]/div/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[8]/div/div[2]/a[3]/div[1]/div[1]

def subscribe_to_slot(driver, slot):
	try:
		slot.click()
	except Exception as e:
		print(e)
		try:
			actions = ActionChains(driver)
			actions.click(slot).perform()
		except Exception as e:
			print(e)
			return False
	#Button to click
	#/html/body/div[4]/div[3]/div/div[2]/div[3]/div/div/div[3]/button[2]
	for validation in driver.find_elements_by_xpath("/html/body/div[4]/div[3]/div/div[2]/div[3]/div/div/div[3]/button[2]"):
		validation.click()
	return True

def race_slots(driver):
	xpath_date = lambda day: "/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]/div/table/thead/tr/td/div/table/thead/tr/th[" + str(day + 2) + "]"
	xpath_slot = lambda day, slot:      "/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[" + str(day + 2) + "]/div/div[2]/a[" + str(slot) + "]/div[1]/div[1]"
	xpath_slot_time = lambda day, slot: "/html/body/div[4]/div[3]/div/div[2]/div/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[" + str(day + 2) + "]/div/div[2]/a[" + str(slot + 2) + "]/div[1]/div[1]"
	# for e in driver.find_elements_by_xpath("/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]"):
	# 	driver.execute_script("scroll(0, 250);", e)
	for day in range(7):
		for d in driver.find_elements_by_xpath(xpath_date(day)):
			date = str(d.get_attribute("data-date")) + " " + d.text[:3]
			print("Looking at date: ", date)
		for i in range(50):
			over = 1
			for slot_time in driver.find_elements_by_xpath(xpath_slot_time(day, i)):
				found = str(slot_time.get_attribute("data-start"))
				found += "  --  "
				found += str(slot_time.get_attribute("data-full"))
				print("\t", found)
				over = 0
				actions = ActionChains(driver)
				actions.move_to_element(slot_time)
				actions.perform()
			for slot in driver.find_elements_by_xpath(xpath_slot(day, i)):
				print(slot)
				if subscribe_to_slot(driver, slot):
					return True
				over = 0
			if over and i > 5:
				print("\t", "None")
				break
	return False

def fancy_print(slots_tab):
	msg = ""
	for line in range(len(slots_tab)):
		if line == 0:
			for col in range(len(slots_tab[0])):
				if col == 0:
					msg += 20 * ' '
				else:
					msg += slots_tab[line][col] + 9 * ' '
				msg += ' '
		else:
			for col in range(len(slots_tab[line])):
				if col == 0:
					msg += "{:<20}".format(slots_tab[line][col])
				else:
					if slots_tab[line][col]:
						msg += 'X'
					else:
						msg += ' '
				msg += ' ' * 10
		msg += '\n'
	# msg += '\n'
	print(msg)
	return msg



def my_slots(driver):
	driver.get("https://profile.intra.42.fr/slots")


#find_element(driver)
# driver.close()
import sys

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: ", sys.argv[0] + " " + "link_to_project")
	else:
		driver = init_session()
		site_login(driver)
		# access_calendar(driver, sys.argv[1])
		# my_slots(driver)
		driver.get("https://projects.intra.42.fr/projects/42cursus-boot2root/slots?team_id=3418937")
		while True:
			if race_slots(driver):
				break
			driver.refresh()
