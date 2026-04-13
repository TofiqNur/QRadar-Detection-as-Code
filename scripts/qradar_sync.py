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

def get_rules_from_endpoint(endpoint):
    url = f"https://{QRADAR_IP}/api/analytics/{endpoint}"
    res = requests.get(url, headers=headers, verify=False)
    return res.json() if res.status_code == 200 else []

def try_put(endpoint, rule_id, payload):
    url = f"https://{QRADAR_IP}/api/analytics/{endpoint}/{rule_id}"
    clean_payload = {k: v for k, v in payload.items() if k not in ['id', 'identifier', 'owner', 'creation_date', 'modification_date', 'origin', 'average_capacity', 'base_capacity']}
    res = requests.put(url, headers=headers, data=json.dumps(clean_payload), verify=False)
    return res.status_code, res.text

print("--- QRadar Discovery & Sync Başladı ---")

# 1. Hər iki bölmədən qaydaları çəkirik
standard_rules = get_rules_from_endpoint("rules")
custom_rules = get_rules_from_endpoint("custom_rules")

print(f"Sistemdə tapıldı: {len(standard_rules)} Standart, {len(custom_rules)} Custom qayda.\n")

for filename in os.listdir(RULES_PATH):
    if filename.endswith(".json"):
        with open(os.path.join(RULES_PATH, filename), 'r') as f:
            github_rule = json.load(f)
            name = github_rule.get('name').strip()
            
            # Adına görə axtarış (həm Standart, həm Custom daxilində)
            found_in_custom = next((r for r in custom_rules if r['name'].strip() == name), None)
            found_in_standard = next((r for r in standard_rules if r['name'].strip() == name), None)
            
            if found_in_custom:
                print(f"'{name}' -> Custom bölməsində tapıldı. Yenilənir...")
                status, text = try_put("custom_rules", found_in_custom['id'], github_rule)
            elif found_in_standard:
                print(f"'{name}' -> Standart bölməsində tapıldı. Yeniləmə sınanır...")
                status, text = try_put("rules", found_in_standard['identifier'], github_rule)
            else:
                print(f"'{name}' -> Tapılmadı! QRadar-dakı adla tam eyni olduğuna əmin ol.")
                continue

            if status == 200:
                print("  [OK] Uğurla yeniləndi!")
            else:
                print(f"  [XƏTA] Status: {status}. Cavab: {text[:50]}")

print("\n--- Proses Bitdi ---")
