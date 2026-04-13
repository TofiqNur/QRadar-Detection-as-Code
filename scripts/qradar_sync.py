import requests
import json
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_IP = os.getenv('QRADAR_IP')
SEC_TOKEN = os.getenv('QRADAR_TOKEN')
RULES_PATH = "rules/qradar/"

# Versiyanı 12.0 edirik, çünki bu versiya daha çox "tolerantdır"
headers = {
    'SEC': SEC_TOKEN,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Version': '12.0' 
}

def try_update(rule_id, payload, rule_name):
    # Bu endpoint ən stabil olanıdır
    url = f"https://{QRADAR_IP}/api/analytics/rules/{rule_id}"
    response = requests.put(url, headers=headers, data=json.dumps(payload), verify=False)
    return response.status_code, response.text

print("--- QRadar Professional Sync v3 Başladı ---")

for filename in os.listdir(RULES_PATH):
    if filename.endswith(".json"):
        with open(os.path.join(RULES_PATH, filename), 'r') as f:
            try:
                data = json.load(f)
                rule_name = data.get('name')
                
                # QRadar-ın "hirslənməməsi" üçün sabit sahələri silirik
                forbidden = ['id', 'identifier', 'creation_date', 'modification_date', 'owner', 'origin', 'average_capacity', 'base_capacity']
                payload = {k: v for k, v in data.items() if k not in forbidden}

                # STRATEGIYA: Əvvəl rəqəmli ID ilə yoxlayırıq (məs: 100679)
                r_id = data.get('id')
                print(f"Yenilənir: {rule_name} (ID: {r_id})...")
                
                status, res_text = try_update(r_id, payload, rule_name)
                
                if status == 200:
                    print(f"  [SUCCESS] QRadar qaydanı qəbul etdi!")
                else:
                    print(f"  [REJECTED] Status: {status}. Cavab: {res_text[:100]}")

            except Exception as e:
                print(f"  [CRITICAL ERROR] {filename}: {str(e)}")

print("--- Proses Bitdi ---")
