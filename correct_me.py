from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import argparse

import re

from config import login

PURPLE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

url = "https://signin.intra.42.fr/users/sign_in"
url_log = "https://stud42.fr/users/auth/marvin"

class SweetAutomation():
	def __init__(self, args):
		self.args = args
		self.driver = webdriver.Firefox()
		self.driver.get(url)
		self.site_login()
		self.links = []
		if args.link:
			self.access_calendar(args.link)
		else:
			self.fetch_started_projects()
		print("List of links: ", self.links)

	def site_login(self):
		self.driver.get(url)
		self.driver.find_element_by_id('user_login').send_keys(login["user"])
		self.driver.find_element_by_id ('user_password').send_keys(login["password"])
		self.driver.find_elements_by_xpath("//input[@class='btn btn-login' and @value='Sign in']")[0].click()
		print("User " + BLUE + login["user"] + RESET + " has been logged!")

	def fetch_started_projects(self):
		# From https://profile.intra.42.fr/
		# List of subscribed projects
		# /html/body/div[4]/div[2]/div/div[2]/div/div[2]/div/div[5]/div/div/a[2]
		links_to_try = []
		xpath_projects = lambda project: "/html/body/div[4]/div[2]/div/div[2]/div/div[2]/div/div[5]/div/div/a[" + str(project + 1) + "]"
		for i in range(100):
			over = 1
			for project in self.driver.find_elements_by_xpath(xpath_projects(i)):
				link = str(project.get_attribute("href"))
				if self.args.regex:
					reg = re.compile(self.args.regex)
					match = re.search(reg, link)
					if match:
						links_to_try.append(link)
				else:
					links_to_try.append(link)
				over = 0
			if over:
				break
		for link in links_to_try:
			self.access_calendar(link)

	def access_calendar(self, link):
		self.driver.get(link)
		try:
			calendar = self.driver.find_element_by_link_text('Subscribe to defense')
			self.links.append(str(calendar.get_attribute("href")))
		except:
			pass

	def loop(self):
		correction_took = 0
		while True:
			for link in self.links:
				self.driver.get(link)
				if self.race_slots():
					correction_took += 1
					if correction_took >= self.args.multi:
						break
			# self.driver.refresh()
			if not self.args.silent:
				print("Refresh!\n")
		self.driver.close()

	def subscribe_to_slot(self, slot):
		slot.click()
		if self.args.validation:
			if "y" != input(BLUE + "If you would you like to subscribe input 'y': " + RESET):
				print(RED + "Slot ignored :(" + RESET)
				return False
		# Selector: /html/body/div[4]/div[3]/div/div[2]/div[3]/div/div/div[2]/select
		# Options:  /html/body/div[4]/div[3]/div/div[2]/div[3]/div/div/div[2]/select/option[1]
		# <select>
		# 	<option value="0"> From 7:00 AM to 7:30 AM </option>
		# 	<option value="1"> From 7:15 AM to 7:45 AM </option>
		# 	<option value="2"> From 7:30 AM to 8:00 AM </option>
		# 	<option value="3"> From 7:45 AM to 8:15 AM </option>
		# </select>
		xpath_validation = "/html/body/div[4]/div[3]/div/div[2]/div[3]/div/div/div[3]/button[2]"
		for validation in self.driver.find_elements_by_xpath(xpath_validation):
			validation.click()
		print(GREEN + "Slot succesfully took!" + RESET)
		return True

	def time_fit(self, slot, date):
		time_start = str(slot.get_attribute("data-start"))
		time_full = str(slot.get_attribute("data-full"))
		if self.args.silent:
			print("\t" + YELLOW + "Date: " + RESET + date)
		print("\t" + BLUE + "SLOT FOUND !" + RESET + " Time: " + PURPLE + time_full + RESET)
		if self.args.time:
			#s: '15h30-24h00'
			reg_s = re.compile(r"(\d+)h(\d+)-(\d+)h(\d+)")
			#c: '5:15 PM - 6:30 PM'
			reg_c = re.compile(r"(\d+):(\d+) ([AP])M - (\d+):(\d+) ([AP])M")
			match_s = re.search(reg_s, self.args.time)
			match_c = re.search(reg_c, time_full)
			if match_s and match_c:
				is_match = False
				start_add = 0 if match_c.group(3) == 'A' else 12
				end_add = 0 if match_c.group(6) == 'A' else 12
				s_hour = [int(match_s.group(1)), int(match_s.group(3))]
				c_hour = [int(match_c.group(1)) + start_add, int(match_c.group(4)) + end_add]
				if s_hour[0] < c_hour[0] < s_hour[1]:
					is_match = True
				elif s_hour[0] == c_hour[0] == s_hour[1]:
					s_min = [int(match_s.group(2)), int(match_s.group(4))]
					c_min = [int(match_c.group(2)), int(match_c.group(5))]
					if s_min[0] <= c_min[0] <= s_min[1]:
						is_match = True
				if is_match == False:
					print("\t" + RED + "Slot ignored: " + RESET + self.args.time)
				return is_match
			else:
				print("Regex error: ", match_s, match_c)
				print(YELLOW + "Will default to True." + RESET)
		return True

	def race_slots(self):
		xpath_date = lambda day: "/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]/div/table/thead/tr/td/div/table/thead/tr/th[" + str(day + 2) + "]"
		xpath_slot = lambda day, slot:      "/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[" + str(day + 2) + "]/div/div[2]/a[" + str(slot + 1) + "]/div[1]/div[1]"
		for day in range(7):
			for d in self.driver.find_elements_by_xpath(xpath_date(day)):
				date = str(d.get_attribute("data-date")) + " " + RED + d.text[:3] + RESET
				if not self.args.silent:
					print(YELLOW + "Looking at date: " + RESET + date)
			for i in range(50):
				over = 1
				for slot in self.driver.find_elements_by_xpath(xpath_slot(day, i)):
					if self.time_fit(slot, date):
						if self.subscribe_to_slot(slot):
							return True
					over = 0
				if over:
					if not self.args.silent:
						print("\t", "None")
					break
		return False

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser = argparse.ArgumentParser(description='Here to help you find corrections without losing your precious time!', epilog="Any help to get it better is appreciated!\nIf needed here is my slack: @ldevelle")

	parser.add_argument("-t", "--time", help="/!\\ ONLY HOURS ARE USED. Allows you to specify an inclusive time range to subscribe to corrections. Example: 15h30-24h00 -> correction can start at 15h30, included, until end of day, included.")
	# parser.add_argument("-d", "--date", help="Allows you to specify an inclusive date range to subscribe to corrections, default to the current week. Example: 2021-01-28/2021-01-30")
	# parser.add_argument("-n", "--now", help="Only looks for correction today", default=False, action='store_true')
	parser.add_argument("-m", "--multi", help="Will take more n correction. Default is 1", type=int, default=1)
	parser.add_argument("-s", "--silent", help="Will reduce verbose to minimum", default=False, action='store_true')
	parser.add_argument("-v", "--validation", help="Ask for manual validation before subscribing to slot", default=False, action='store_true')
	parser.add_argument("-l", "--link", help="Link to your project, ex:\thttps://projects.intra.42.fr/42cursus-malloc/ldevelle")
	parser.add_argument("-r", "--regex", help="Regex for project selection")
	args = parser.parse_args()

	correc_impec = SweetAutomation(args)
	correc_impec.loop()
