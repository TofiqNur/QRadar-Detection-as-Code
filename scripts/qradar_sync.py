import requests
import json
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_IP = os.getenv('QRADAR_IP')
SEC_TOKEN = os.getenv('QRADAR_TOKEN')
RULES_PATH = "rules/qradar/"

# QRadar API-nin mütləq tələb etdiyi versiya və təhlükəsizlik başlıqları
headers = {
    'SEC': SEC_TOKEN,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Version': '15.0'  # Bu versiya 404 xətasını həll etmək üçün mütləqdir
}

def update_qradar_rule(rule_id, rule_data):
    # Əsas qayda: Sənin yaratdığın qaydalar adətən bu ünvanda olur
    url = f"https://{QRADAR_IP}/api/analytics/rules/{rule_id}"
    
    # QRadar-ın "Update" zamanı qəbul etmədiyi (Read-only) sahələri təmizləyirik
    forbidden_keys = [
        'id', 'identifier', 'creation_date', 'modification_date', 
        'owner', 'average_capacity', 'base_capacity', 
        'base_host_id', 'capacity_timestamp', 'origin'
    ]
    payload = {k: v for k, v in rule_data.items() if k not in forbidden_keys}
    
    # PUT metodu ilə məlumatı göndəririk
    response = requests.put(url, headers=headers, data=json.dumps(payload), verify=False)
    return response.status_code, response.text

print("--- QRadar Rule Sync Başladı ---")

for filename in sorted(os.listdir(RULES_PATH)):
    if filename.endswith(".json"):
        with open(os.path.join(RULES_PATH, filename), 'r') as f:
            try:
                data = json.load(f)
                # QRadar qaydaları mütləq UUID (identifier) ilə yenilənməlidir
                rule_uuid = data.get('identifier')
                rule_name = data.get('name')
                
                print(f"Yenilənir: {rule_name}...")
                status, response_text = update_qradar_rule(rule_uuid, data)
                
                if status == 200:
                    print(f"  [OK] Uğurla yeniləndi!")
                elif status == 404:
                    print(f"  [XƏTA] 404: QRadar bu ID-ni tapmadı: {rule_uuid}. API bölməsini yoxla.")
                else:
                    print(f"  [XƏTA] Status: {status}. Cavab: {response_text[:100]}")
            except Exception as e:
                print(f"  [XƏTA] Fayl oxunarkən problem: {e}")

print("--- Sync Prosesi Bitdi ---")
