# scripts/scope_preflight_cloud_risks.py
import os

from dotenv import load_dotenv
from falconpy import CloudSecurity

load_dotenv()

client = CloudSecurity(
    client_id=os.getenv("FALCON_CLIENT_ID"),
    client_secret=os.getenv("FALCON_CLIENT_SECRET"),
    base_url=os.getenv("FALCON_BASE_URL"),
)

probes = [
    ("combined_cloud_risks", lambda: client.combined_cloud_risks(limit=1)),
    ("ListCloudGroupsExternal", lambda: client.ListCloudGroupsExternal(limit=1)),
    ("ListCloudGroupsByIDExternal", lambda: client.ListCloudGroupsByIDExternal(ids=["nonexistent"])),
]

all_pass = True
for name, probe in probes:
    resp = probe()
    status = resp.get("status_code") if isinstance(resp, dict) else 0
    if status == 403:
        print(f"FAIL {name}: HTTP 403 — scope MISSING. Add scope to API key.")
        all_pass = False
    elif status == 404:
        print(f"ERROR {name}: HTTP 404 — operation name wrong or endpoint does not exist.")
        all_pass = False
    else:
        print(f"OK   {name}: HTTP {status}")

if not all_pass:
    raise SystemExit("Scope preflight failed. Do not proceed to implementation.")
print("\nAll scopes confirmed. Proceed to implementation.")
