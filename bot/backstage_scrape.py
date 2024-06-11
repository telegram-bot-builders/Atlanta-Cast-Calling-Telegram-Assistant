import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

BACKSTAGE_AI_API_KEY = os.getenv("BACKSTAGE_AI_API_KEY")
ROBOT_ID = "dc3999b2-df0d-4254-bf07-7d5c63cd33fc"

class BrowseAIApi:
    def __init__(self, api_key, base_url="https://api.browse.ai/v2"):
        self.base_url = base_url
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

    def retrieve_task(self, robot_id, task_id):
        url = f"{self.base_url}/robots/{robot_id}/tasks/{task_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_all_tasks(self, page=1, page_size=10, status=None, robot_bulk_run_id=None, sort=None, include_retried=None, from_date=None, to_date=None):
        url = f"{self.base_url}/robots/{ROBOT_ID}/tasks"
        params = {
            "page": page,
            "pageSize": page_size,
            "status": status,
            "robotBulkRunId": robot_bulk_run_id,
            "sort": sort,
            "includeRetried": include_retried,
            "fromDate": from_date,
            "toDate": to_date
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def run_robot(self, record_video=False, input_parameters=None):
        url = f"{self.base_url}/robots/{ROBOT_ID}/tasks"
        payload = json.dumps({
            "recordVideo": record_video,
            "inputParameters": input_parameters
        })
        self.headers['Content-Type'] = 'application/json'
        response = requests.post(url, headers=self.headers, data=payload)
        return response.json()

browse_ai = BrowseAIApi(BACKSTAGE_AI_API_KEY)
