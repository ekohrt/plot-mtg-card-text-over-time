# -*- coding: utf-8 -*-
"""
Created on Sat Oct  2 14:26:43 2021

@author: Ethan

https://deckstats.net/sets/?lng=en -> for making a json file mapping set abbrevs to dates

Project: given a piece of card text, plot its usage in cards over time.

Next project: plot the average and maximum (power)/cmc over time
"""
import json
import re
from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker


#get a dict of all card data
with open('AtomicCards_Small.json', 'r', encoding="utf-8") as f:
    cards_dict = json.load(f)['data']
    #now you can search card entries by cards_dict[cardname]
    
    
#open file of set codes and dates into a dict
with open('SetList.json', 'r', encoding='utf-8') as f2:
    setlist = json.load(f2)['data']
    # construct a dict with {set_code: {name, date}, ...}
    sets_dict = {cs.get('code', None): {"name": cs.get('name', None), 
                                        "date": cs.get('releaseDate', None)}
                 for cs in setlist if 'code' in cs }
   
#since the mtgJson file is missing some, get that data from another file 
with open('mtg_sets_dates_deckstats.json', 'r', encoding='utf-8') as f3:
    setSupplement_dict = json.load(f3)['data']
    #if sets_dict is missing a set code, get the data from this other file I made
    missing = set(setSupplement_dict.keys()) - set(sets_dict.keys())
    for code in missing:
        sets_dict[code] = {"name": setSupplement_dict[code], "date": setSupplement_dict.get('releaseDate', None)}
    
    

"""
converts a date string like '1993-12-01' to a datetime object
"""
def convertStringToDate(dateString):
    return datetime.strptime(dateString.replace("-"," "), '%Y %m %d')


# make sure to exclude the set "Magic Online Promos (PRM)" since it causes inaccuracies.
excludedSets = {"PRM"}
"""
given a card name (string), get all of its printing dates (as datetime objects)
"""
def getAllDates(cardname):
    #get all the printings of this card
    printing_dates = []
    for face in cards_dict[cardname]:
        printing_dates.extend( [convertStringToDate(sets_dict[setCode]['date']) 
                                for setCode in face.get('printings', [])
                                if sets_dict[setCode]['date'] != None and setCode not in excludedSets] )
    #return list of datetime object 
    return printing_dates


def getEarliestDate(cardname):
    #get all the printings of this card
    printing_dates = getAllDates(cardname)
    #sort dates in ascending order (earliest to latest)
    printing_dates.sort()
    #return first datetime object, unless it's empty
    if len(printing_dates) == 0: 
        return None
    else: 
        return printing_dates[0]


"""
Searches all MtG cards for ones whose text matches a given regular expression.
@param regexPattern is a compiled regex, like p = re.compile( r'(.*)[Ff]lying(.*)')
@return list of card names (strings)
"""
def searchCardsForMatches(regexPattern):
    matching_cards = []
    for name in cards_dict:
        for face in cards_dict[name]: #some cards have multiple faces
            text = face.get('text', "").lower() #lowercase
            if regexPattern.search(text) != None:
                matching_cards.append(name)
    return matching_cards


 
"""
"""
def getAllEarliestDates(card_matches_list):
    allDates = []
    for cardname in card_matches_list:
        d = getEarliestDate(cardname)
        if d != None:
            allDates.append(d)
    return allDates

     
"""
Take a list of datetime objects, group by year, and return 1 coord per year
The x coord is the year, and the y coord is how many occurrences that year.
@return two lists of int counts: x_data and y_data
"""
def constructData(datetime_list):   
    yearCounts = {year:0 for year in range(1993, 2022)}
    for dt in datetime_list:
        year = dt.year #int
        yearCounts[year] = yearCounts[year]+1
            
    #convert dict to list; 
    x_data, y_data = [], []
    for year in yearCounts:
        x_data.append(year)
        y_data.append(yearCounts[year])
    
    return x_data, y_data



def plotDates(dates, regex_string):
    #For each year since 1993, count up the matching cards released that year
    x_data, y_data = constructData(dates)

    #plot the # of cards over time
    plt.title('New MtG cards whose text contains the expression:\n {}'.format(regex_string))
    plt.xlabel('year')
    plt.ylabel('# of cards')
    plt.locator_params(axis="both", integer=True)
    plt.plot(x_data, y_data)
    plt.show()
      

def main():          
    #search for cards that contain this expression
    regex = r'(.*)living weapon(.*)'
    regex = r'(.*)face down(.*)'
    pattern = re.compile(regex)
    matches = searchCardsForMatches(pattern)
    
    # get all cards with text that matches this regex
    allDates = getAllEarliestDates(matches)
    
    #matplotlib tutorial: https://www.youtube.com/watch?v=UO98lJQ3QGI
    #plot the stuff 
    plotDates(allDates, regex)

            
if __name__ == "__main__":
    main()