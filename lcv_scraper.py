import requests
from bs4 import BeautifulSoup


def get_lcv_data():
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
                member['Name'] = span.text
                for a in span.find_all('a'):
                    member['LCV Link'] = url_base + a['href']
            elif "mocParty" in str(span):
                member["Party"] = span.text
            elif "mocState" in str(span):
                if len(span.text) == 2:
                    member["Congress"] = "Senate"
                    member["District"] = None
                else:
                    member["Congress"] = "House"
                    member["District"] = span.text[-2:]
                member["State"] = span.text[:2]
            elif "mocRating" in str(span):
                member["Rating"] = span.text
            if member not in congress and member:
                congress.append(member)

    return congress


def get_current_senators():
    senate_url = "https://www.senate.gov/senators/"
    r = requests.get(senate_url)
    soup = BeautifulSoup(r.content)

    current_sens = []
    for a in soup.find_all('a'):
        if "senate.gov" in str(a) and " " in str(a.text):
            current_sens.append(a.text)

    return current_sens


def get_current_representatives():
    house_url = "https://www.house.gov/representatives"
    r = requests.get(house_url)
    soup = BeautifulSoup(r.content)

    current_reps = []
    for a in soup.find_all('a'):
        if "house.gov" in str(a) and "house.gov" not in str(a.text) and a.text not in current_reps:
            current_reps.append(a.text)
    
    return current_reps
