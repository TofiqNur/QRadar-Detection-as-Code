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

def get_custom_rules():
    # Bizə ancaq istifadəçinin yaratdığı (custom) rule-lar lazımdır
    url = f"https://{QRADAR_IP}/api/analytics/custom_rules"
    res = requests.get(url, headers=headers, verify=False)
    return res.json() if res.status_code == 200 else []

def update_custom_rule(rule_id, payload):
    # Custom rule-ları yeniləmək üçün xüsusi endpoint
    url = f"https://{QRADAR_IP}/api/analytics/custom_rules/{rule_id}"
    
    # QRadar-ın PUT zamanı qəbul etmədiyi bütün texniki sahələri təmizləyirik
    forbidden = [
        'id', 'identifier', 'owner', 'creation_date', 'modification_date', 
        'origin', 'average_capacity', 'base_capacity', 'base_host_id', 
        'capacity_timestamp', 'linked_rule_identifier'
    ]
    clean_payload = {k: v for k, v in payload.items() if k not in forbidden}
    
    res = requests.put(url, headers=headers, data=json.dumps(clean_payload), verify=False)
    return res.status_code

print("--- QRadar Final Sync Mode ---")

# 1. QRadar-dan bütün custom rule-ları gətiririk
all_custom_rules = get_custom_rules()

for filename in os.listdir(RULES_PATH):
    if filename.endswith(".json"):
        with open(os.path.join(RULES_PATH, filename), 'r') as f:
            try:
                github_data = json.load(f)
                github_name = github_data.get('name')
                
                # 2. GitHub-dakı adı QRadar-dakılarla tam uyğunlaşdırırıq
                match = next((r for r in all_custom_rules if r['name'].strip() == github_name.strip()), None)
                
                if match:
                    real_id = match.get('id')
                    print(f"Yenilənir: '{github_name}' (ID: {real_id})...")
                    status = update_custom_rule(real_id, github_data)
                    
                    if status == 200:
                        print("  [OK] Uğurla yeniləndi!")
                    else:
                        print(f"  [XƏTA] Status: {status}. QRadar yeniləməni rədd etdi.")
                else:
                    print(f"  [XƏTA] '{github_name}' adlı qayda QRadar-da tapılmadı. Adları yoxla!")
            except Exception as e:
                print(f"  [KRİTİK] {filename} oxunarkən xəta: {e}")

print("--- Proses Bitdi ---")
