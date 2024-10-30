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

def get_markers(start_times):
    # determine markers for the thread for when to start finding travel times
    
    # create list of start times
    start_times_str = sorted(start_times.split(","))
    # Convert each time string into a datetime object for today
    today = datetime.now().date()
    desired_start = [
        datetime.combine(today, datetime.strptime(time_str.strip(), "%H:%M").time())
        for time_str in start_times_str
    ]
    # Create desired_end list by adding 8 hours to each start time
    desired_end = [
        start_time + timedelta(hours=8)
        for start_time in desired_start
    ]

    return (desired_start, desired_end)

def get_data(home, work, markers):
    WAIT_TIME_SECONDS = 10 * 60  # 10 minutes in seconds
    # target start time is 1 hour before first desired start time
    target_start = datetime.combine(datetime.now().date(), datetime.strptime(markers[0][0], "%H:%M").time()) - timedelta(hours=1)

    # wait until the target start time
    while datetime.now() < target_start:
        time.sleep(1)

    # calculate travel time from home to work every 10 minutes
    for start_time_str in markers[0]:
        start_time = datetime.combine(datetime.now().date(), datetime.strptime(start_time_str, "%H:%M").time())
        # only start calculations if within 1 hour of the start time
        while datetime.now() < start_time:
            if datetime.now() >= start_time - timedelta(hours=1):
                travel_data = get_travel_time(home, work)
                arrival_time = travel_data[2]
                # assuming arrival_time is in "HH:MM" format
                if arrival_time < start_time_str:
                    write_to_csv(travel_data)
                time.sleep(WAIT_TIME_SECONDS)

    # calculate travel time from work to home for each desired end time
    for end_time_str in markers[1]:
        end_time = datetime.combine(datetime.now().date(), datetime.strptime(end_time_str, "%H:%M").time())
        # wait until the desired leave time
        while datetime.now() < end_time:
            time.sleep(1)
        # calculate travel time and write to CSV
        travel_data = get_travel_time(work, home)
        write_to_csv(travel_data)

def main():
    home = input("Enter location of home: ")
    work = input("Enter location of work: ")
    start_times = input("Possible times to start a work shift (e.g. 7:00,7:30,8:00): ")
    markers = get_markers(start_times)
    get_data(home, work, markers)

if __name__ == "__main__":
    # remove existing csv file
    if os.path.exists(FILENAME):
        os.remove(FILENAME)
    main()
