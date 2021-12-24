from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.action_chains import ActionChains

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
		options = Options()
		# options.log.level = "fatal"    # Debug - TRACE
		options.headless = True
		service = Service("./geckodriver")
		self.driver = webdriver.Firefox(service=service, options=options)

		self.driver.get(url)
		self.site_login()
		self.links = []
		if args.physical_slots:
			self.subscribe_to_slots_to_go_to_school()
		if args.link:
			self.access_calendar(args.link)
		else:
			self.fetch_started_projects()
		print(BLUE + "List of links: " + RESET, self.links)

	def site_login(self):
		self.driver.get(url)
		self.driver.find_element(By.ID, 'user_login').send_keys(login["user"])
		self.driver.find_element(By.ID, 'user_password').send_keys(login["password"])
		self.driver.find_elements(By.XPATH, "//input[@class='btn btn-login' and @value='Sign in']")[0].click()
		print("User " + BLUE + login["user"] + RESET + " has been logged!")

	def subscribe_to_slots_to_go_to_school(self):
		from time import sleep
		url = "https://reservation.42network.org/signin"
		print("First url: " + url)
		self.driver.get(url)
		url = "https://reservation.42network.org/static/#/"
		print("Secon url: " + url)
		self.driver.get(url)
		# /html/body/div/div[2]/section/div[2]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[3]/div/div[2]/a[4]/div/div[1]
		# 03/23 12h -> E1
		# /html/body/div/div[2]/section/div[2]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[3]/div/div[2]/a[15]/div/div[1]
		# 	E2
		# /html/body/div/div[2]/section/div[2]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[3]/div/div[2]/a[16]/div/div[1]
		# 	TDM
		# /html/body/div/div[2]/section/div[2]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[3]/div/div[2]/a[17]/div/div[1]
		# E1 next hour
		# /html/body/div/div[2]/section/div[2]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[3]/div/div[2]/a[18]/div/div[1]
		#
		# E1 next day:
		# /html/body/div/div[2]/section/div[2]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[4]/div/div[2]/a[16]/div/div[1]
		xpath_slot = lambda day, hour, cluster: "/html/body/div/div[2]/section/div[2]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[" + str(day + 1) + "]/div/div[2]/a["+ str((hour * 3) + cluster) + "]/div/div[1]"
		xpath_nb_slots = "/html/body/div/div[2]/div/div[2]/div/header/div/div/span[2]/span[2]"
		xpath_cancel = "/html/body/div/div[2]/div/div[2]/div/footer/button"
		xpath_subscribe = "/html/body/div/div[2]/div/div[2]/div/footer/div/button/span"
		xpath_subscribe_button = "/html/body/div/div[2]/div/div[2]/div/footer/div/button/span"
		xpath_already_a_slot = "/html/body/div/div[2]/div/div[2]/div/section/div/div[2]/div/footer/button"
		xpath_quit_modal = "/html/body/div/div[2]/div/div[2]/button"

		# 0 is monday
		days = [2]
		hours = [i for i in range(12, 16)]
		clusters = [i for i in range(3)]
		while len(hours):
			for d in range(0, 7):
				if d not in days:
					continue
				for h in range(8, 18):
					if h not in hours:
						continue
					for c in range(0, 3):
						if c not in clusters:
							continue
						print(f"For Day {d} at {h}h00 in cluster {c}:")
						# self.driver.implicitly_wait(2)
						for slot in self.driver.find_elements(By.XPATH, xpath_slot(d + 1, h - 8 + 1, c)):
							print("Opened")
							for _ in range(10):
								try:
									slot.click()
									break
								except:
									print("Waiting...")
									sleep(1)
							exit_modal = True
							# for _ in range(10):
							# 	try:
							#		slot.click()
							#	except:
							#		print("Waiting...")
							# 		sleep(1)
							for nb in self.driver.find_elements(By.XPATH, xpath_nb_slots):
								vals = []
								while len(vals) < 2:
									vals = nb.text.split('/')
									print("Wait nb places")
									sleep(1)
								print("\t{}{}/{}{}".format(YELLOW, vals[0], vals[1], RESET))
								if int(vals[0]) < int(vals[1]):
									# print("Starting sleep")
									# sleep(10)
									for subscribe in self.driver.find_elements(By.XPATH, xpath_subscribe):
										print(subscribe.text)
										if subscribe.text != "unsubscribe":
											for subscribe_button in self.driver.find_elements(By.XPATH, xpath_subscribe_button):
												subscribe_button.click()
											try:
												self.driver.find_elements(By.XPATH, xpath_already_a_slot)[0].click()
												print("Already another cluster registered at same day and hour")
											except:
												print("Has been subscribed !!!!!!!")
												exit_modal = False
											hours.remove(h)
										else:
											for cancel in self.driver.find_elements(By.XPATH, xpath_cancel):
												cancel.click()
								# except:
								# 	sleep(1000)
							if exit_modal:
								for chaos in range(10):
									print("Chaos: ", chaos)
									try:
										self.driver.find_elements(By.XPATH, xpath_quit_modal)[0].click()
										break
									except:
										print("Error when quitting non available slot")
										sleep(1)






	def fetch_started_projects(self):
		links_to_try = []
		xpath_projects = lambda project: "/html/body/div[4]/div[2]/div/div[2]/div/div[2]/div/div[5]/div/div/a[" + str(project + 1) + "]"
		for i in range(100):
			over = 1
			for project in self.driver.find_elements(By.XPATH, xpath_projects(i)):
				link = str(project.get_attribute("href"))
				if self.args.regex:
					reg = re.compile(self.args.regex)
					match = re.search(reg, link)
					if match:
						print(self.args.regex + GREEN + " did match     " + PURPLE + link + RESET)
						links_to_try.append(link)
					else:
						print(self.args.regex + RED + " did not match " + PURPLE + link + RESET)
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
			calendar = self.driver.find_element(By.LINK_TEXT, 'Subscribe to defense')
			self.links.append(str(calendar.get_attribute("href")))
		except:
			pass

	def loop(self):
		correction_took = 0
		if self.links:
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
				for cancel in self.driver.find_elements(By.XPATH, "/html/body/div[4]/div[3]/div/div[2]/div[3]/div/div/div[3]/button[1]"):
					cancel.click()
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
		for validation in self.driver.find_elements(By.XPATH, xpath_validation):
			validation.click()
		print(GREEN + "Slot succesfully took!" + RESET)
		return True

	def date_fit(self, date):
		if not self.args.silent:
			print(YELLOW + "Looking at date: " + RESET + date)
		is_match = True
		if self.args.date:
			#self:   '2021-01-14/2021-01-15'
			reg_s = re.compile(r"(\d+)-(\d+)-(\d+)/(\d+)-(\d+)-(\d+)")
			#correc: '2021-01-14 Thu'
			reg_c = re.compile(r"(\d+)-(\d+)-(\d+)")
			match_s = re.search(reg_s, self.args.date)
			match_c = re.search(reg_c, date)
			if match_s and match_c:
				s_date = [None, None]
				s_date[0] = [int(match_s.group(1)), int(match_s.group(2)), int(match_s.group(3))]
				s_date[1] = [int(match_s.group(4)), int(match_s.group(5)), int(match_s.group(6))]
				c_date = [int(match_c.group(1)), int(match_c.group(2)), int(match_c.group(3))]
				is_match = False
				for i in range(3):
					if s_date[0][i] <= c_date[i] <= s_date[1][i]:
						if i == 2:
							is_match = True
						continue
					else:
						break
				if not self.args.silent:
					if is_match == False:
						print("\t" + RED + "Date ignored: " + RESET + self.args.date)
					else:
						print("\t" + GREEN + "Date valid: " + RESET + self.args.date)
			else:
				print("Regex error: ", match_s, match_c)
				print(YELLOW + "Will default to True." + RESET)
		return is_match

	def time_fit(self, slot, date):
		time_start = str(slot.get_attribute("data-start"))
		time_full = str(slot.get_attribute("data-full"))
		if self.args.silent:
			print("\t" + YELLOW + "Date: " + RESET + date)
		print("\t" + BLUE + "SLOT FOUND !" + RESET + " Time: " + PURPLE + time_full + RESET)
		if self.args.time:
			#self:   '15h30-24h00'
			reg_s = re.compile(r"(\d+)h(\d+)-(\d+)h(\d+)")
			#correc: '5:15 PM - 6:30 PM'
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
		import time
		time.sleep(2)
		xpath_date = lambda day: "/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]/div/table/thead/tr/td/div/table/thead/tr/th[" + str(day + 2) + "]"
		xpath_slot = lambda day, slot:      "/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[" + str(day + 2) + "]/div/div[2]/a[" + str(slot + 1) + "]/div[1]/div[1]"
		for day in range(7):
			for d in self.driver.find_elements(By.XPATH, xpath_date(day)):
				date = str(d.get_attribute("data-date")) + " " + RED + d.text[:3] + RESET
				if self.date_fit(date):
					for i in range(50):
						over = 1
						for slot in self.driver.find_elements(By.XPATH, xpath_slot(day, i)):
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

	parser.add_argument("-t", "--time", help="Allows you to specify an inclusive time range to subscribe to corrections. Example: 15h30-24h00 -> correction can start at 15h30, included, until end of day, included.")
	parser.add_argument("-d", "--date", help="Allows you to specify an inclusive date range in the current week to subscribe to corrections, default to the current week. Example: 2021-01-28/2021-01-30")
	# parser.add_argument("-n", "--now", help="Only looks for correction today", default=False, action='store_true')
	parser.add_argument("-m", "--multi", help="Will take n corrections. Default is 1", type=int, default=1)
	parser.add_argument("-s", "--silent", help="Will reduce verbose to minimum", default=False, action='store_true')
	parser.add_argument("-v", "--validation", help="Ask for manual validation before subscribing to slot", default=False, action='store_true')
	parser.add_argument("-l", "--link", help="Link to your project, ex:\thttps://projects.intra.42.fr/42cursus-malloc/ldevelle")
	parser.add_argument("-p", "--physical_slots", help="Reseve slots to physically go to school")
	parser.add_argument("-r", "--regex", help="Regex for project selection")
	args = parser.parse_args()

	correc_impec = SweetAutomation(args)
	correc_impec.loop()
