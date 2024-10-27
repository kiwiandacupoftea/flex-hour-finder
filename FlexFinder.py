# download chromedriver: https://googlechromelabs.github.io/chrome-for-testing/
# add location of chromedriver to Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

def get_travel_time(home, work):
    driver = webdriver.Chrome()

    driver.get("https://www.google.com/maps/dir/")

    time.sleep(5)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    fastest_time = soup.find("div", class_="Fk3sm fontHeadlineSmall delay-light")
    print(fastest_time.get_text(strip=True))

    driver.quit()


def main():
    get_travel_time(1, 2)

if __name__ == "__main__":
    main()
