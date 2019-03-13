import time
from random import randint
from warnings import warn
import re

import pandas as pd
import requests
from IPython.core.display import clear_output
from bs4 import BeautifulSoup

import DataCleaner as hlp

# Initial Scrape data
ids=[]
names = []
durations = []
years = []
ratings = []

votes = []


# Monitor time
start_time = time.time()
request = 1
movie_no = 1

no_loops=input('please enter no of loops (one loop will retreive 50 Movies data)  : ')


start_date=str(raw_input('please enter a start date (yyyy-mm-dd) :')).strip()

end_data=str(raw_input('please enter a end date (yyyy-mm-dd) : ')).strip()

print('searching for the  first {} movies from {} to {}').format(no_loops*50, start_date,end_data)

#2018-12-26
for i in range(0, no_loops):
    # Generate the page
    page = i * 50 + 1

    # Url change the from date and to date to retreive movies
    print(start_date,end_data)
    url = "https://www.imdb.com/search/title?release_date={},{}&sort=num_votes," \
          "desc&start={}&ref_=adv_nxt".format(start_date,end_data,page)

    # Send the request and Get the response
    response = requests.get(url)

    # use vbeautifulsoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Fetch the data
    lister_items = soup.find_all("div", class_="lister-item")

    # Get the data
    for single_item in lister_items:


        single_item_content = single_item.find("div", class_="lister-item-content")

        # get data of single movie

        # get movie name and clean the string
        id = movie_no

        name = single_item_content.h3.a.get_text()
        name = name.strip()

        # get the total movie running time and clean the data
        duration = single_item_content.find("p", class_="text-muted").find("span", class_="runtime")
        if duration is not None:
            duration = duration.get_text()
            duration = re.findall(r"\d+", duration)[0]
            duration = int(duration)
        else:
            duration = "Unknown"

        # get the released year data and clean the data
        year = single_item_content.h3.find("span", class_="lister-item-year").get_text()
        year = re.findall(r"\d+", year)[0]
        year = int(year)

        # get the movie rating and clean the data
        rating = single_item_content.find("div", class_="ratings-imdb-rating")["data-value"]
        rating = float(rating.strip())


        #get no of votes and clean the data
        votes1 = single_item_content.find("p", class_="sort-num_votes-visible").find_all("span",attrs={"name": "nv"})
        vote = votes1[0]["data-value"]
        vote = int(vote.strip())


        # Add data to global array
        ids.append(id)
        names.append(name)
        durations.append(duration)
        years.append(year)
        ratings.append(rating)
        votes.append(vote)


        print("Movie No. #{}: {}  Rating: {}".format(movie_no, name.encode('utf-8'),rating))

        # Separate Every Movie
        print("---------------------------------------------------")

        # Increment Movie
        movie_no += 1

    # calculate the time for retreiving 50 movies data
    total_time = time.time() - start_time
    request_per_sec = total_time / request
    print("{} movies data has been read per sec".format(request_per_sec))

    # if not 200 status warn the user
    if response.status_code != 200:
        warn("{} no. has status code {}\n{}\n".format(request, response.status_code, url))


    request += 1

    #console formatting
    print("\n---------------------------------------------------")
    print ('Sleeping for 2 secs....')
    time.sleep(2)
    print("---------------------------------------------------\n")
    clear_output(wait=True)

# save the data to a data frame of pandas
data_frame = pd.DataFrame({
    "ID": ids,
    "Movie_Name": names,
    "Movie_Year": years,
    "Movie_Duration": durations,
    "Movie_Rating": ratings,
    "Movie_Vote": votes,

})

data_frame.to_csv("IMDB_Scrapped_data.csv", index=False, encoding='utf-8')
print("please check the CSV in outData folder ")