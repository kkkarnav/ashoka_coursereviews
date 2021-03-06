from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import os
from dotenv import load_dotenv
from time import sleep


class AMSScraper:
    def __init__(self):
        load_dotenv()
        # needs a geckodriver.exe in the same folder as a script,
        # as well as a firefox exe in the specified location
        options = Options()
        options.binary_location = (
            "C:\\Users\\KARNAV\\AppData\\Local\\Firefox Developer Edition\\firefox.exe"
        )

        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)

        # for convenience, runs fine in headless too
        self.driver.maximize_window()

    # engine function to submit text to an input field
    def fill_text(self, findby_criteria, find_parameter, fill_parameter):
        text_area = wait(self.driver, 10).until(
            EC.element_to_be_clickable((findby_criteria, find_parameter))
        )
        text_area.send_keys(fill_parameter)
        text_area.send_keys(Keys.RETURN)
        sleep(2)

    # logs into the ashoka website with your email and password
    def login(self):

        USERNAME = os.getenv("EMAIL")
        PASSWORD = os.getenv("PASSWORD")

        self.fill_text(By.ID, "identifierId", USERNAME)
        self.fill_text(By.NAME, "password", PASSWORD)

    # starting from the home page, locates the specified menu and submenu and clicks on it
    def navigate_to_page_from_navbar(self, menu_number, submenu_name):

        sleep(10)

        link = self.driver.find_elements(By.CLASS_NAME, "dropdown-toggle")[menu_number]
        wait(self.driver, 20).until(EC.element_to_be_clickable(link))

        open_menu = ActionChains(self.driver)
        open_menu.move_to_element(link).perform()

        click_submenu = wait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, submenu_name))
        )
        click_submenu.click()

    # starting from the home page, locates the specified page tile and clicks on it
    def navigate_to_page_from_tile(self, tile_icon):
        link = self.driver.find_elements(By.CLASS_NAME, tile_icon)[0]
        wait(self.driver, 20).until(EC.element_to_be_clickable(link))
        link.click()

    # WARNING: this function is prone to failing because the page arbitrarily async loads, just retry
    # clicks the get button, then switches pagesize to all to get all the data
    def grab_table_data(self):

        # i am completely aware how hacky this is
        # but there doesn't seem to be a way around it, the dropdown is very messy
        # if you want a semester other than the current one, run the scraper in fullscreen, NOT headless
        # once the page loads, use this sleep to manually select the semester

        get_button = self.driver.find_element(By.CLASS_NAME, "blue")
        wait(self.driver, 20).until(EC.element_to_be_clickable(get_button))
        get_button.click()

        select = Select(self.driver.find_element(By.CLASS_NAME, "pagesize"))
        wait(self.driver, 20).until(EC.element_to_be_clickable(select))
        select.select_by_index(5)

        wait(self.driver, 20).until(EC.element_to_be_clickable(get_button))
        return self.driver.page_source

    # scrapes course details from the view modal for a given course entry
    def grab_course_detail(self, view_number):
        while True:
            try:
                view_button = self.driver.find_elements(By.LINK_TEXT, "view")[
                    view_number
                ]
                view_button.click()
                sleep(1)
                break
            except Exception:
                continue

        html_data = self.driver.find_elements(By.ID, "divdata")[0].get_attribute(
            "innerHTML"
        )

        while True:
            try:
                close_button = self.driver.find_elements(By.TAG_NAME, "button")[11]
                close_button.click()
                sleep(1)
                break
            except Exception:
                continue

        return html_data

    # goes through course catalogue table and scrapes modal data for each course
    def grab_course_catalogue_details(self):

        sleep(10)

        course_detail_htmls = []
        view_count = len(self.driver.find_elements(By.LINK_TEXT, "view"))

        for view_number in range(view_count):
            course_detail_htmls.append(self.grab_course_detail(view_number))

        return course_detail_htmls

    def grab_major_minor_rows(self):

        sleep(5)

        get_button = wait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "blue"))
        )
        get_button.click()

        sleep(10)

        select = Select(self.driver.find_element(By.CLASS_NAME, "pagesize"))
        sleep(5)
        select.select_by_index(5)

        wait(self.driver, 10).until(EC.element_to_be_clickable(get_button))
        html_data = self.driver.page_source.split(
            "TableAdvanceSearch pagerDisabled tablesorter tablesorter-bootstrap "
            "table table-bordered table-striped hasFilters"
        )[1]
        html_data = html_data.split("1 - 7283 / 7283 (7283)")[0]
        html_data = html_data.split("tbody")[1]

        return html_data

    # converts course catalogue page html data into lists
    def process_course_catalogue(self, raw_data):

        raw_data = raw_data.split("<tbody")[1]
        row_count = len(raw_data.split("</tr>")) - 4
        data = [[[None] for column in range(6)] for row in range(row_count - 1)]

        for i in range(row_count - 1):
            start_location = raw_data.find("<tr")
            one_row = raw_data[start_location:]

            for j in range(1, 6):
                cell_start = one_row.find("<td")
                cell_end = one_row.find("</td>")
                data[i][j] = (
                    one_row[cell_start:cell_end]
                    .replace("<br>", " ")
                    .split(">")[1]
                    .split("<")[0]
                )
                one_row = one_row.split("</td>", 1)[1]
            raw_data = raw_data.split("</tr>", 1)[1]

        # with open('./new.json', 'w') as f:
        #    json.dump(data, f, indent=4)

        return data

    # converts major minor report page html data into lists
    def process_major_minor(self, raw_data):

        row_count = len(raw_data.split("</tr>"))
        data = [[[None] for column in range(6)] for row in range(row_count - 1)]

        for i in range(row_count - 1):
            start_location = raw_data.find("<tr")
            one_row = raw_data[start_location:]

            for j in range(1, 7):
                cell_start = one_row.find("<td")
                cell_end = one_row.find("</td>")
                data[i][j - 1] = (
                    one_row[cell_start:cell_end]
                    .replace("<br>", " ")
                    .split(">")[1]
                    .split("<")[0]
                )
                one_row = one_row.split("</td>", 1)[1]
            raw_data = raw_data.split("</tr>", 1)[1]

        return data

    def scrape(self, page_namestring):

        html_table, ams_data = "", [None]

        # base url
        self.driver.get("https://ams.ashoka.edu.in/")

        # log into AMS if not already logged in
        self.login() if self.driver.find_elements(By.ID, "identifierId") else print(
            "already logged in"
        )

        if page_namestring == "View Course Catalogue":

            # retrieved data at course.txt and coursedetails.txt

            self.navigate_to_page_from_tile("fa-users")
            html_table = self.grab_table_data()
            course_details = self.grab_course_catalogue_details()
            ams_data = self.process_course_catalogue(html_table)

        if page_namestring == "Major Minor Report":

            # retrieved data at major.txt

            self.navigate_to_page_from_navbar(8, page_namestring)
            html_table = self.grab_major_minor_rows()

            with open("./students_html.txt", "w") as file:
                file.write(str(html_table))

            ams_data = self.process_major_minor(html_table)

        return html_table, ams_data

    def raw_data(self):
        return self.scrape("Major Minor Report")[1]


if __name__ == "__main__":
    scraper = AMSScraper()

    # scrape AMS for students with academic details
    string_data, data = scraper.scrape("Major Minor Report")
    with open("./students.txt", "w") as file:
        file.write(str(data))

    # OR use pre-retrieved data
    # with open("./students.txt", "r") as file:
    #    data = file.read()
