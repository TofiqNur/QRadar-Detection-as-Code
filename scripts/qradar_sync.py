import requests
import json
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_IP = os.getenv('QRADAR_IP')
SEC_TOKEN = os.getenv('QRADAR_TOKEN')
RULES_PATH = "rules/qradar/"

headers = {
    'SEC': SEC_TOKEN,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Version': '15.0'
}

def get_all_rules_from_qradar():
    url = f"https://{QRADAR_IP}/api/analytics/rules"
    res = requests.get(url, headers=headers, verify=False)
    return res.json() if res.status_code == 200 else []

def update_rule(rule_id, payload):
    url = f"https://{QRADAR_IP}/api/analytics/rules/{rule_id}"
    # QRadar-ın sevmədiyi sahələri təmizləyirik
    clean_payload = {k: v for k, v in payload.items() if k not in ['id', 'identifier', 'owner', 'creation_date', 'modification_date', 'origin']}
    res = requests.put(url, headers=headers, data=json.dumps(clean_payload), verify=False)
    return res.status_code

print("--- QRadar Intelligent Sync Başladı ---")

# 1. QRadar-da olan bütün qaydaları çəkirik
qradar_rules = get_all_rules_from_qradar()

for filename in os.listdir(RULES_PATH):
    if filename.endswith(".json"):
        with open(os.path.join(RULES_PATH, filename), 'r') as f:
            github_rule = json.load(f)
            rule_name = github_rule.get('name')
            
            # 2. GitHub-dakı qaydanı QRadar-da adına görə axtarırıq
            found_rule = next((r for r in qradar_rules if r['name'] == rule_name), None)
            
            if found_rule:
                actual_id = found_rule.get('identifier')
                print(f"Tapıldı: '{rule_name}' -> ID: {actual_id}")
                
                # 3. Tapılan real ID (UUID) ilə yeniləyirik
                status = update_rule(actual_id, github_rule)
                if status == 200:
                    print(f"  [UĞURLU] QRadar yeniləndi!")
                else:
                    print(f"  [XƏTA] Status: {status}")
            else:
                print(f"  [XƏTA] QRadar-da '{rule_name}' adlı qayda tapılmadı!")

print("--- Proses Bitdi ---")
