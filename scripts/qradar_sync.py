import requests
import json
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Bu məlumatlar GitHub Secrets-dən gələcək (Təhlükəsizlik üçün)
QRADAR_IP = os.getenv('QRADAR_IP')
SEC_TOKEN = os.getenv('QRADAR_TOKEN')
RULES_PATH = "rules/qradar/"

headers = {
    'SEC': SEC_TOKEN,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def update_qradar_rule(rule_id, rule_data):
    # QRadar API-də rule-u update etmək üçün PUT metodundan istifadə olunur
    url = f"https://{QRADAR_IP}/api/analytics/rules/{rule_id}"
    response = requests.put(url, headers=headers, data=json.dumps(rule_data), verify=False)
    return response.status_code

# Qovluqdakı bütün .json fayllarını yoxla
for filename in os.listdir(RULES_PATH):
    if filename.endswith(".json"):
        with open(os.path.join(RULES_PATH, filename), 'r') as f:
            data = json.load(f)
            rule_id = data.get('id') # JSON daxilindəki ID-ni götürür
            
            print(f"Yenilənir: {data.get('name')} (ID: {rule_id})...")
            status = update_qradar_rule(rule_id, data)
            
            if status == 200:
                print(f"Uğurla yeniləndi!")
            else:
                print(f"Xəta baş verdi. Status kodu: {status}")
