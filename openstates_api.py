"""
API to connect to OpenStates.

Running into issue with call limits on the API (lines 84-85) and may need to 
    rethink how we store the data and make the API calls.
"""

import json
import math
import time
import requests


class OpenStatesAPI:
    """
    Class to connect to Open States via API.
    """
    base_path = "https://v3.openstates.org/bills?jurisdiction="
    query_path = "&sort=updated_desc&include=abstracts&include=actions&include=votes"
    page_path = "&page="
    end_path = "&per_page=20&apikey=4a087065-961f-4547-b32e-f29ebf328083"

    def __init__(self, state, keywords):
        """
        Initializes an instance of the `OpenStatesAPI` class.

        Inputs:
            - state: (str) name of state
            - keywords: list of keywords to filter by
            - loop_num: (int) number of loops to retrieve all bills
        """
        self.state = state.replace(" ", "%20")
        self.keywords = keywords
        self.loop_num = 0
        self.build_keyword_path()

    def build_keyword_path(self):
        """
        Updates the query_path to filter by the given keywords.

        Inputs: None

        Returns: Nothing
        """
        for keyword in self.keywords:
            self.query_path += "&q=" + keyword.replace(" ", "%20")

    def get_loop_num(self):
        """
        Determines how many API calls are required to get all data.
        Raises an error if unable to connect to the API.

        Inputs: None

        Returns: (int) number of loops
        """
        url = self.base_path + self.state + self.query_path + self.page_path + '1' + self.end_path
        r = requests.get(url)
        if r.status_code != 200:
            raise ValueError("API call failed")

        result = r.text.encode()
        json_data = json.loads(result.decode())
        count = json_data['pagination']['total_items']
        loop_num = math.ceil(count / 20)
        self.loop_num = loop_num

        return loop_num

    def get_data(self):
        """
        Makes the API call and retrieves the data as JSON.

        Inputs: None

        Returns: (list of dicts) list of bill information
        """
        bills_list = []
        loop_num = self.get_loop_num()

        for page in range(1, loop_num + 1):
            url = self.base_path + self.state + self.query_path + self.page_path + str(page) + self.end_path
            r = requests.get(url)
            if r.status_code != 200:
                return bills_list

            result = r.text.encode()
            json_data = json.loads(result.decode())
            bills_list.append(json_data['results'])

            print(str(page) + " of " + str(self.loop_num) + " calls complete.")
            # added in to try to get around API call limits
            time.sleep(1)

        return bills_list


def get_data_for_state_and_topic(state, keywords):
    """
    Makes an API call to Open States based on the state and keywords given.

    Inputs:
        - state: (str) state
        - keywords: list of keywords
    
    Returns: (list of dicts) list of bill information
    """
    all_bills = []

    api_call = OpenStatesAPI(state, keywords)
    bills = api_call.get_data()
    all_bills += bills

    return all_bills
