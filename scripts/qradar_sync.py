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
    'Version': '12.0'
}

def get_standard_rules():
    url = f"https://{QRADAR_IP}/api/analytics/rules"
    res = requests.get(url, headers=headers, verify=False)
    return res.json() if res.status_code == 200 else []

def update_rule(rule_id, payload):
    url = f"https://{QRADAR_IP}/api/analytics/rules/{rule_id}"
    
    clean_payload = {k: v for k, v in payload.items() if k not in ['id', 'identifier', 'owner', 'creation_date', 'modification_date', 'origin', 'average_capacity', 'base_capacity']}
    
    # -------------------------------------------------------------
    # BÜTÜN PROBLEM BURADA İDİ: requests.put yox, requests.post !
    # -------------------------------------------------------------
    res = requests.post(url, headers=headers, data=json.dumps(clean_payload), verify=False)
    return res.status_code, res.text

print("--- QRadar Final POST Fix Başladı ---")

standard_rules = get_standard_rules()

for filename in os.listdir(RULES_PATH):
    if filename.endswith(".json"):
        with open(os.path.join(RULES_PATH, filename), 'r') as f:
            github_rule = json.load(f)
            name = github_rule.get('name').strip()
            
            found = next((r for r in standard_rules if r['name'].strip() == name), None)
            
            if found:
                r_id = found['id'] 
                print(f"Yenilənir: '{name}' (Rəqəmli ID: {r_id})...")
                
                # POST sorğusu göndərilir
                status, text = update_rule(r_id, github_rule)
                
                # QRadar uğurlu POST üçün 200, 201 və ya 202 qaytara bilər
                if status in [200, 201, 202]:
                    print("  [OK] UĞURLA YENİLƏNDİ!")
                else:
                    print(f"  [XƏTA] Status: {status}. Cavab: {text[:60]}")
            else:
                print(f"'{name}' -> QRadar-da tapılmadı.")

print("--- Proses Bitdi ---")
