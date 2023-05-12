'''
API to scrape the League of Conservation Voters' website to
retrieve environment scores for each legislator.
'''
import requests
from bs4 import BeautifulSoup


def get_lcv_data():
    '''
    Scrapes the LCV website to get an environment score
    for every member of the U.S. Congress.

    Inputs: None

    Returns: (list of dicts) list of congress member information
    '''
    url = "https://scorecard.lcv.org/members-of-congress"
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    
    congress = []
    url_base = 'https://scorecard.lcv.org'
    for div in soup.find_all('div', class_="tableRow"):
        member = {}
        for span in div.find_all('span'):
            if "tableHeader" in str(span):
                continue
            if "mocName" in str(span):
                member['name'] = span.text
                for a in span.find_all('a'):
                    member['lcv_link'] = url_base + a['href']
            elif "mocParty" in str(span):
                member["party"] = span.text
            elif "mocState" in str(span):
                if len(span.text) == 2:
                    member["congress"] = "Senate"
                    member["district"] = None
                else:
                    member["congress"] = "House"
                    member["district"] = span.text[-2:]
                member["state"] = span.text[:2]
            elif "mocRating" in str(span):
                member["lcv_rating"] = span.text
            if member and member not in congress:
                congress.append(member)

    return congress


def get_current_senators():
    '''
    Scrapes the U.S. Senate website to determine the current senators.

    Inputs: None

    Returns: (list of str) the names of all current senators
    '''
    senate_url = "https://www.senate.gov/senators/"
    r = requests.get(senate_url)
    soup = BeautifulSoup(r.content)

    current_sens = []
    for a in soup.find_all('a'):
        if "senate.gov" in str(a) and " " in str(a.text):
            current_sens.append(a.text)

    return current_sens


def get_current_representatives():
    '''
    Scrapes the U.S. House of Representatives website 
    to determine the current representatives.

    Inputs: None

    Returns: (list of str) the names of all current representatives
    '''
    house_url = "https://www.house.gov/representatives"
    r = requests.get(house_url)
    soup = BeautifulSoup(r.content)

    current_reps = []
    for a in soup.find_all('a'):
        if ("house.gov" in str(a) 
            and "house.gov" not in str(a.text) 
            and a.text not in current_reps):
            current_reps.append(a.text)
    
    return current_reps
