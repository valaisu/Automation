from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from parse import *


"""
This code does not work by itself, see
https://www.youtube.com/watch?v=vUOtS6zU40A&t=75s
to find out what to put inside files cookies.json, credentials.json
This is done to grant access for the code to your google calendar.
takes maybe 5 mins
"""


# These are for development purposes, set both
# to False if you don't intend to run software
# multiple times
load_cookies, save_cookies = True, True


driver = webdriver.Chrome()  # Or Firefox, etc.
driver.get('https://sisu.aalto.fi/')

if load_cookies:
    # Load cookies
    with open('cookies.json', 'r') as file:
        cookies = json.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)
    # the cookies can't be loaded before we are not on the right website, reloading logs in
    driver.get('https://sisu.aalto.fi/')

input("Press Enter after you have logged in...")  # Wait for manual login

# Navigate to the page with the elements after logging in
driver.get('https://sisu.aalto.fi/student/calendar/enrolments')

# Wait for the 'button-box non-button' elements to be loaded
buttons = WebDriverWait(driver, 30).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "button-box.non-button"))
)

# Click each button to reveal the 'course-unit-enrolments'
for button in buttons:
    try:
        button.click()  # Click the first button
        time.sleep(1)
        # Wait for the corresponding 'course-unit-enrolments' to become visible
        course_unit = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "courseunit-realisation-bottom-row"))
        )
    except Exception as e:
        print(f"Error1: {e}")

# Open dropdowns containing "Harjoitus" - times
second_buttons = driver.find_elements(By.CLASS_NAME, "link-button.other-ssg")
for second_button in second_buttons:
    try:
        second_button.click()  # Click the second button if it exists
        # Optionally wait for some condition after the second click
    except Exception as e:
        print(f"Error2: {e}")

time.sleep(1)

course_units = driver.find_elements(By.CLASS_NAME, "courseunit-realisation-bottom-row")
# course_unit = kurssi
for course_unit in course_units:
    # event_group = laskarit|luonnot|tentit
    event_groups = course_unit.find_elements(By.CLASS_NAME, "event-groups")
    for event_group in event_groups:

        # Find the event-info row
        event_info_row = event_group.find_element(By.CLASS_NAME, "event-info")
        event_title = event_info_row.find_element(By.CLASS_NAME, "event-title").text

        # Check is the event is selected to be shown in sisu
        if event_title == "Harjoitus":
            selected = "input[type='checkbox']"
            if not event_group.find_element(By.CSS_SELECTOR, selected).is_selected():
                continue

        # Find the sibling element with class 'row single-group'
        single_group_rows = event_group.find_elements(By.CLASS_NAME, "row.single-group")
        for single_group_row in single_group_rows:

            event_dates = single_group_row.find_elements(By.CLASS_NAME, "link-button.event-date")
            for e in event_dates:
                event_date = e.get_attribute("aria-label")
                event_time = single_group_row.find_element(By.CLASS_NAME, "col-3").text
                event_loc = single_group_row.find_element(By.CLASS_NAME, "col-7.col-md-6.col-lg-7").text

                print(f"Event Type: {event_title}")
                print(f"Date: {event_date}")
                print(f"Time: {event_time}")
                print(f"Time: {event_loc}")
                print("--------")

                send_event(event_title, event_date, event_time, event_loc)

if save_cookies:
    # for development purposes
    cookies = driver.get_cookies()
    with open('cookies.json', 'w') as file:
        json.dump(cookies, file)

driver.quit()

print("Done.")
