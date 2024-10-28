# download chromedriver: https://googlechromelabs.github.io/chrome-for-testing/
# add location of chromedriver to Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time, csv, os, threading

travel_csv = "travel_times.csv"

def get_travel_time(start, end):
    # open WebDriver
    driver = webdriver.Chrome()
    # format url for Google Maps search
    url = "https://www.google.com/maps/dir/" + start.replace(" ","+") + "/" + end.replace(" ","+")
    driver.get(url)
    # wait for page to fully load
    time.sleep(5)
    # parse page source for fastest time
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    # get time of fastest route
    fastest_time = soup.find("div", class_="Fk3sm fontHeadlineSmall delay-light")
    # close WebDriver
    driver.quit()
    # return time of fastest route
    return fastest_time.get_text(strip=True)

def write_to_csv():
    # create csv if does not exist
    if not os.path.exists(travel_csv):
        with open('travel_times.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["curr_time", "arr_time"])


def main():
    #home = input("Enter location of home: ")
    #work = input("Enter location of work: ")
    #curr_time = time.strftime("%H:%M:%S", time.localtime())
    #print(curr_time)
    write_to_csv()
    #print(get_travel_time(home, work))


if __name__ == "__main__":
    # remove existing csv file
    if os.path.exists(travel_csv):
        os.remove(travel_csv)
    main()
