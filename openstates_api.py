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
    pages_path = "&sort=updated_desc&include=abstracts&include=actions&page="
    end_path = "&per_page=20&apikey=4a087065-961f-4547-b32e-f29ebf328083"

    def __init__(self, state):
        """
        Constructor.
        :param state: (str) name of state
        :param subjects: (list) list of subjects to filter by
        """
        self.state = state.replace(" ", "%20")
        self.loop_num = 0

    def get_loop_num(self):
        """
        Determine how many API calls are required to get all data.
        :return: (int) number of loops required
        """
        r = requests.get(self.base_path + self.state + self.pages_path + '1' + self.end_path)
        if r.status_code != 200:
            raise ValueError("API call failed")

        result = r.text.encode("iso-8859-1")
        json_data = json.loads(result.decode('latin-1'))
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
        count = 0

        for page in range(1, loop_num + 1):
            count += 1
            url = self.base_path + self.state + self.pages_path + str(page) + self.end_path
            r = requests.get(url)
            if r.status_code != 200:
                raise ValueError("API call failed")
                # this happens a lot due to call number limits and restricts the ways in which we can make the calls
                # will need to rethink how we store data and make API calls

            result = r.text.encode("iso-8859-1")
            json_data = json.loads(result.decode('latin-1'))
            bills_list.append(json_data['results'])

            print(str(count) + "of" + str(self.loop_num) + "loops complete.")
            # added in to try to get around API call limits
            time.sleep(1)

        return bills_list


def get_data_for_all_states(states):
    """
    Function to make an API call to Open States
    and get data for every state passed in.
    :param states: list of states
    :return: list of all bill dictionaries
    """
    all_bills = []

    for state in states:
        api_call = OpenStatesAPI(state)
        bills = api_call.get_data()
        all_bills += bills

    return all_bills

