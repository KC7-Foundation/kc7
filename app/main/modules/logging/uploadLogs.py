import json
import requests
import datetime
import hashlib
import hmac
import base64

from flask import current_app

## TODO: Remove secrets from code before uploading to GitHub

class LogUploader():
    """Upload json logs to Azure"""
    
    def __init__(self, log_type, data):
        
        self.log_type = log_type      # name of field in azure
        self.data = json.dumps(data)  # data should be a json blog

        # Update the customer ID to your Log Analytics workspace ID
        self.customer_id = current_app.config["CUSTOMER_ID"]

        # For the shared key, use either the primary or the secondary Connected Sources client authentication key   
        self.shared_key = current_app.config["SHARED_KEY"]

    
    # Build the API signature
    def _build_signature(self, customer_id, shared_key, date, content_length, method, content_type, resource):
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")  
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
        return authorization

    # Build and send a request to the POST API
    def _post_data(self, customer_id, shared_key, body, log_type):
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = self._build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
        uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': log_type,
            'x-ms-date': rfc1123date
        }

        response = requests.post(uri,data=body, headers=headers)
        if (response.status_code >= 200 and response.status_code <= 299):
            print('Uploaded table %s to Azure' % log_type)
        else:
            print("Response code: {}".format(response.status_code))

    def send_request(self):
        """Send a request to Azure to add data to the log-analytics"""

        if current_app.config["DEBUG_MODE"]:
            pass
            #print(f"WARNING: DEBUG MODE enabled! {len(json.loads(self.data))} rows will NOT be uploaded to table {self.log_type}!")
        else:
            self._post_data(self.customer_id, self.shared_key, self.data, self.log_type)