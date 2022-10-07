"""
API to connect to OpenStates.
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
        Constructor.
        :param state: (str) name of state
        :param keywords: list of keywords to filter by
        :param loop_num: (int) number of loops to retrieve all bills
        """
        self.state = state.replace(" ", "%20")
        self.keywords = keywords
        self.loop_num = 0
        self.build_keyword_path()

    def build_keyword_path(self):
        """
        Update the query_path to filter by the keywords given.
        """
        for keyword in self.keywords:
            self.query_path += "&q=" + keyword.replace(" ", "%20")

    def get_loop_num(self):
        """
        Determine how many API calls are required to get all data.
        :return: (int) number of loops required
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
        :return: (list) bill dictionaries
        """
        bills_list = []
        loop_num = self.get_loop_num()

        for page in range(1, loop_num + 1):
            url = self.base_path + self.state + self.query_path + self.page_path + str(page) + self.end_path
            r = requests.get(url)
            if r.status_code != 200:
                return bills_list
                #raise ValueError("API call failed. " + r.reason)
                # this happens a lot due to call number limits and restricts the ways in which we can make the calls
                # will need to rethink how we store data and make API calls

            result = r.text.encode()
            json_data = json.loads(result.decode())
            bills_list.append(json_data['results'])

            print(str(page) + " of " + str(self.loop_num) + " calls complete.")
            # added in to try to get around API call limits
            time.sleep(1)

        return bills_list


def get_data_for_state_and_topic(state, keywords):
    """
    Function to make an API call to Open States based on the state and keywords given.
    :param state: (str) state
    :param keywords: list of keywords
    :return: list of all bill dictionaries
    """
    all_bills = []

    api_call = OpenStatesAPI(state, keywords)
    bills = api_call.get_data()
    all_bills += bills

    return all_bills
