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
    'Accept': 'application/json'
}

def update_qradar_rule(rule_id, rule_data):
    # DİQQƏT: Sənin yazdığın rule-lar üçün 'custom_rules' istifadə olunmalıdır
    url = f"https://{QRADAR_IP}/api/analytics/custom_rules/{rule_id}"
    
    # Professional SOC fəaliyyəti: Read-only sahələri təmizləyirik
    # QRadar bu sahələrin PUT ilə göndərilməsini sevmir
    readonly_fields = ['id', 'identifier', 'creation_date', 'modification_date', 'owner', 'average_capacity', 'base_capacity', 'base_host_id', 'capacity_timestamp']
    payload = {k: v for k, v in rule_data.items() if k not in readonly_fields}
    
    response = requests.put(url, headers=headers, data=json.dumps(payload), verify=False)
    return response.status_code, response.text

for filename in os.listdir(RULES_PATH):
    if filename.endswith(".json"):
        with open(os.path.join(RULES_PATH, filename), 'r') as f:
            try:
                data = json.load(f)
                # Buraya rəqəmli ID-ni (məs: 100679) geri qaytarırıq, 
                # çünki custom_rules endpoint-i rəqəmli ID ilə işləyir
                rule_id = data.get('id') 
                
                print(f"Yenilənir: {data.get('name')} (ID: {rule_id})...")
                status, text = update_qradar_rule(rule_id, data)
                
                if status == 200:
                    print(f"Uğurla yeniləndi! (Status: 200)")
                else:
                    print(f"Xəta! Status: {status}. Cavab: {text[:100]}")
            except Exception as e:
                print(f"Fayl oxunarkən xəta ({filename}): {e}")
