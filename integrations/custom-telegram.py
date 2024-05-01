#!/usr/bin/env python

import sys
import json
import requests
from requests.auth import HTTPBasicAuth

# CHAT_ID="xxxx"
CHAT_ID = ""

# Read configuration parameters
alert_file = open(sys.argv[1])
hook_url = sys.argv[3]

# Read the alert file
alert_json = json.loads(alert_file.read())
alert_file.close()

# Extract data fields
alert_level = alert_json['rule']['level'] if 'level' in alert_json['rule'] else "N/A"
description = alert_json['rule']['description'] if 'description' in alert_json['rule'] else "N/A"
agent = alert_json['agent']['name'] if 'name' in alert_json['agent'] else "N/A"

# Generate message text
message_text = f"Alert Level: {alert_level}\nDescription: {description}\nAgent: {agent}"

# Generate request
msg_data = {
    'chat_id': CHAT_ID,
    'text': message_text
}

headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

# Send the request
requests.post(hook_url, headers=headers, data=json.dumps(msg_data))

sys.exit(0)
