import requests
import json

class SimulationJob():
    #every call will connect to this base URL
    BASE_URL = 'https://develop.buildsimhub.net/'

    def __init__(self, userKey, mk):
        self._userKey = userKey
        self._modelKey = mk
        self._trackToken = ""
        self._trackStatus = "No simulation is running or completed in this Job - please start simulation using create_run_model method."
        self._model_action_list = list()

    @property
    def trackStatus(self):
        return self._trackStatus

    @property
    def trackToken(self):
        return self._trackToken

    @property
    def modelKey(self):
        return self._modelKey

    @trackToken.setter
    def trackToken(self, value):
        self._trackToken = value

    def add_model_action(self, action):
        if action.get_num_value()>0:
            return "Cannot process more than one value for a single simulation job. Try parametric study."
        self._model_action_list.append(action)

    def get_simulation_results(self, resultType="html"):
        if(self._trackToken == ""):
            return self._trackStatus

        url = SimulationJob.BASE_URL + 'GetSimulationResult_API'
        payload = {
            'user_api_key': self._userKey,
            'result_type': resultType,
            'track_token': self._trackToken
        }

        r = requests.post(url, params=payload, stream=True)

        f = ""
        if r.status_code == 200:
            f = r.text
        return f

    def track_simulation(self):
        if(self._trackToken == ""):
            return self._trackStatus

        url = SimulationJob.BASE_URL + 'TrackSimulation_API'
        payload = {
            'user_api_key': self._userKey,
            'track_token': self._trackToken
        }
        r = requests.get(url, params=payload)
        resp_json = r.json()

        if 'has_more' not in resp_json:
            if 'error_msg' in resp_json:
                self._trackStatus = resp_json['error_msg']
                return False
            else:
                self._trackStatus = 'Finished'
                return False

        if resp_json['has_more']:
            self._trackStatus = resp_json['doing'] + " " + str(resp_json['percent']) + "%"
            return resp_json['has_more']
        else:
            self._trackStatus = resp_json['error_msg']        
            return resp_json['has_more']

    def run(self, file_dir, wea_dir, unit='ip', agent=1, simulationType='regular'):
        url = SimulationJob.BASE_URL + 'RunSimulationCustomize_API'
        payload = {
            'user_api_key':self._userKey,
            'simulation_type': simulationType,
            'agents': agent,
            'unit': unit
        }

        files = {
            'model': open(file_dir, 'rb'),
            'weather_file': open(wea_dir,'rb')
        }

        r= requests.post(url, data=payload, files = files)
        resp_json = r.json()
        if resp_json['status'] == 'success':
            self._trackToken = resp_json['tracking']
            return resp_json['status']
        else:
            return resp_json['error_msg']

    def run_model_simulation(self, unit='ip', agent=1, simulationType = "regular"):
        url = SimulationJob.BASE_URL + 'RunSimulation_API'

        if self._trackToken == "":
            return 'error: no model is created in this simulation job. Please create a model use create_model method.'

        payload = {
            'user_api_key': self._userKey,
            'track_token': self._trackToken,
            'simulation_type': simulationType,
            'agents': agent,
            'unit': unit
        }

        r = requests.post(url, data=payload)
        resp_json = r.json()
        if resp_json['status'] == 'success':
            return resp_json['status']
        else:
            return resp_json['error_msg']

    def create_run_model(self, file_dir,  unit='ip', agent = 1, comment = "Upload through Python API", simulationType ="regular"):
        url = SimulationJob.BASE_URL + 'CreateModel_API'
        payload = {
            'user_api_key': self._userKey,
            'folder_api_key': self._modelKey,
            'comment': comment,
            'simulation_type': simulationType,
            'agents': agent,
            'unit': unit
        }
        files = {
            'file': open(file_dir, 'rb')
        }

        r = requests.post(url, data=payload, files = files)
        resp_json = r.json()

        if resp_json['status'] == 'success':
            self._trackToken = resp_json['tracking']
            return resp_json['status']
        else:
            return resp_json['error_msg']

    def create_model(self, file_dir, comment = "Upload through Python API"):
        url = SimulationJob.BASE_URL + 'CreateModel_API'
        payload = {
            'user_api_key': self._userKey,
            'folder_api_key': self._modelKey,
            'comment': comment,
            'simulation_type': '',
            'agents': 1
        }

        files = {
            'file': open(file_dir, 'rb')
        }
        
        r = requests.post(url, data=payload, files=files)
        
        resp_json = r.json()

        if resp_json['status'] == 'success':
            self._trackToken = resp_json['tracking']
            return resp_json['status']
        else:
            return resp_json['error_msg']

