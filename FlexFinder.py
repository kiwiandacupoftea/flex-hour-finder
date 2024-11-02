# download chromedriver: https://googlechromelabs.github.io/chrome-for-testing/
# add location of chromedriver to Path

from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import csv
import os
import re

FILENAME = "travel_times.csv"

def get_travel_time(start, end):
    try:
        # open WebDriver
        driver = webdriver.Chrome()
        # format url for Google Maps search
        url = "https://www.google.com/maps/dir/" + start.replace(" ","+") + "/" + end.replace(" ","+")
        driver.get(url)
        # wait for page to fully load
        time.sleep(10)
        # parse page source for fastest time
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        # get time of fastest route
        fastest_time = soup.find("div", class_="Fk3sm fontHeadlineSmall delay-light")
        # close WebDriver
        driver.quit()
        # if request failed, return None
        if fastest_time is None:
            print("fastest_time found: is None")
            return None
        else:
            # return tuple of current time, arrival time, and time of fastest route
            travel_minutes = convert_to_min(fastest_time.get_text(strip=True))
            curr_time = datetime.now()
            arr_time = curr_time + timedelta(minutes=travel_minutes)
            if travel_minutes is None:
                print("travel_minutes is None")
            if curr_time is None:
                print("curr_time is None")
            if arr_time is None:
                print("arr_time is None")
            return (curr_time, travel_minutes, arr_time)
    except Exception as e:
            driver.quit()
            print(f"Error in get_travel_time: {e}")
            return None

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
        # convert datetime objects to strings
        new_row = {
            headers[0]: tup[0].strftime("%H:%M"),
            headers[1]: tup[1],
            headers[2]: tup[2].strftime("%H:%M")
        }
        writer.writerow(new_row)

def get_markers(start_times):
    # determine markers for when to start finding travel times
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
    target_start = markers[0][0] - timedelta(hours=1)
    # wait until the target start time
    while datetime.now() < target_start:
        time.sleep(1)
    print("Starting ticker...")
    # calculate travel time from home to work every 10 minutes
    for start_time in markers[0]:
        # only start calculations if within 1 hour of the start time
        while datetime.now() < start_time:
            if datetime.now() >= start_time - timedelta(hours=1):
                travel_data = get_travel_time(home, work)
                if travel_data is not None:
                    arrival_time = travel_data[2]
                    # assuming arrival_time is in "HH:MM" format
                    if arrival_time < start_time:
                        write_to_csv(travel_data)
                    else: # stop checking travel times if passed the desired start time
                        break 
                time.sleep(WAIT_TIME_SECONDS)
            else:
                time.sleep(1) # reduces CPU usage
    print("Calculated travel from home to work.")
    print("Calculating travel from work to home...")
    # calculate travel time from work to home for each desired end time
    for end_time in markers[1]:
        # wait until the desired leave time
        while datetime.now() < end_time:
            time.sleep(1)
        # calculate travel time and write to CSV
        travel_data = get_travel_time(work, home)
        if travel_data is not None:
            write_to_csv(travel_data)
    print("Ticker stopped.")

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
