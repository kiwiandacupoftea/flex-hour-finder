# download chromedriver: https://googlechromelabs.github.io/chrome-for-testing/
# add location of chromedriver to Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time, csv, os, re, threading

FILENAME = "travel_times.csv"

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
    # return tuple of current time, arrival time, and time of fastest route
    travel_minutes = convert_to_min(fastest_time.get_text(strip=True))
    curr_time = datetime.now()
    arr_time = curr_time + timedelta(minutes=travel_minutes)
    return (curr_time.strftime("%H:%M"), travel_minutes, arr_time.strftime("%H:%M"))

def convert_to_min(time_str):
    # convert the time from Google maps 
    # possible formats: x hr x min, x hr, x min
    
    # regular expressions to match formats
    hours_match = re.search(r"(\d+)\s*hr", time_str)
    minutes_match = re.search(r"(\d+)\s*min", time_str)
    # extract hours and minutes, default to 0 if not found
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    # convert to total time in minutes
    total_minutes = hours * 60 + minutes
    return total_minutes

def write_to_csv(tup):
    headers = ['CurrentTime', 'DurationMinutes', 'ArrivalTime']
    # create csv if does not exist
    if not os.path.exists(FILENAME):
        with open(FILENAME, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
    # append new row to file
    with open(FILENAME, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        new_row = {
            headers[0]: tup[0],
            headers[1]: tup[1],
            headers[2]: tup[2]
        }
        writer.writerow(new_row)

def find_markers(start_times):
    # determine markers for the thread for when to start finding travel times
    
    # create list of start times
    split_starts = start_times.split(",")
    # convert to list of ints
    int_split_starts = [int(i) for i in split_starts]
    # markers for start time are 1 hour prior (assume travel will be maximum of 1 hour)
    start_markers = [x - 1 for x in int_split_starts]
    # markers for end time are 8 hours after start time
    end_markers = [x + 8 for x in int_split_starts]

    print(start_markers)
    print(end_markers)


def main():
    home = input("Enter location of home: ")
    work = input("Enter location of work: ")
    #start_times = input("Possible times to start a work shift (e.g. 7,8,9): ")
    travel_data = get_travel_time(home, work)
    #find_markers("7,8,9")
    write_to_csv(travel_data)
    #print(convert_to_min("1 hr 23 min"))
    #print(get_travel_time(home, work))


if __name__ == "__main__":
    # remove existing csv file
    if os.path.exists(FILENAME):
        os.remove(FILENAME)
    main()
