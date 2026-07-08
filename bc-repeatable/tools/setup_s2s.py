#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

TENANT_ID = "eb4005a6-4bc1-41d0-93be-6595f1a5bc80"
ENVIRONMENT = "BCDemoG"
COMPANY = "G7"
BASE_URI = "https://api.businesscentral.dynamics.com"
GRAPH = "https://graph.microsoft.com/v1.0"
PUBLIC_CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"  # Microsoft Graph PowerShell
BC_RESOURCE_APP_ID = "996def3d-b36c-4153-8607-a6fd3c01b89f"
APP_NAME = "Codex BC Automation API"


def form_request(url, data):
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=encoded, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def device_token(scopes, label):
    device = form_request(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode",
        {"client_id": PUBLIC_CLIENT_ID, "scope": " ".join(scopes)},
    )
    print(f"{label} device code: {device['user_code']}", flush=True)
    print(device["message"], flush=True)
    deadline = time.time() + int(device.get("expires_in", 900))
    interval = int(device.get("interval", 5))
    while time.time() < deadline:
        time.sleep(interval)
        try:
            return form_request(
                f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
                {
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "client_id": PUBLIC_CLIENT_ID,
                    "device_code": device["device_code"],
                },
            )["access_token"]
        except urllib.error.HTTPError as exc:
            body = json.loads(exc.read().decode("utf-8"))
            if body.get("error") in ("authorization_pending", "slow_down"):
                if body.get("error") == "slow_down":
                    interval += 5
                continue
            raise SystemExit(f"{label} auth failed: {body}") from exc
    raise SystemExit(f"{label} device login expired.")


def request(method, url, token, payload=None, headers=None):
    hdrs = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"{method} {url} failed: HTTP {exc.code}\n{body}") from exc


def graph_filter(value):
    return urllib.parse.quote(value, safe="'")


def get_graph_app(token, display_name):
    flt = graph_filter(f"displayName eq '{display_name}'")
    rows = request("GET", f"{GRAPH}/applications?$filter={flt}", token).get("value", [])
    return rows[0] if rows else None


def ensure_graph_application(token):
    bc_filter = graph_filter(f"appId eq '{BC_RESOURCE_APP_ID}'")
    bc_sps = request("GET", f"{GRAPH}/servicePrincipals?$filter={bc_filter}", token).get("value", [])
    if not bc_sps:
        raise SystemExit("Dynamics 365 Business Central service principal was not found in this tenant.")
    bc_sp = bc_sps[0]
    roles = {r["value"]: r for r in bc_sp.get("appRoles", []) if r.get("isEnabled")}
    missing = [r for r in ("API.ReadWrite.All", "Automation.ReadWrite.All") if r not in roles]
    if missing:
        raise SystemExit(f"Missing Business Central app roles: {', '.join(missing)}")

    app = get_graph_app(token, APP_NAME)
    if not app:
        app = request(
            "POST",
            f"{GRAPH}/applications",
            token,
            {
                "displayName": APP_NAME,
                "signInAudience": "AzureADMyOrg",
                "requiredResourceAccess": [
                    {
                        "resourceAppId": BC_RESOURCE_APP_ID,
                        "resourceAccess": [
                            {"id": roles["API.ReadWrite.All"]["id"], "type": "Role"},
                            {"id": roles["Automation.ReadWrite.All"]["id"], "type": "Role"},
                        ],
                    }
                ],
            },
        )

    secret = request(
        "POST",
        f"{GRAPH}/applications/{app['id']}/addPassword",
        token,
        {
            "passwordCredential": {
                "displayName": "Codex local automation",
                "endDateTime": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            }
        },
    )["secretText"]

    sp_filter = graph_filter(f"appId eq '{app['appId']}'")
    sp_rows = request("GET", f"{GRAPH}/servicePrincipals?$filter={sp_filter}", token).get("value", [])
    sp = sp_rows[0] if sp_rows else request("POST", f"{GRAPH}/servicePrincipals", token, {"appId": app["appId"]})

    existing_assignments = request("GET", f"{GRAPH}/servicePrincipals/{sp['id']}/appRoleAssignments", token).get("value", [])
    existing_role_ids = {a.get("appRoleId") for a in existing_assignments}
    for role_name in ("API.ReadWrite.All", "Automation.ReadWrite.All"):
        role_id = roles[role_name]["id"]
        if role_id in existing_role_ids:
            continue
        request(
            "POST",
            f"{GRAPH}/servicePrincipals/{sp['id']}/appRoleAssignments",
            token,
            {"principalId": sp["id"], "resourceId": bc_sp["id"], "appRoleId": role_id},
        )

    return app["appId"], secret


def api_root():
    return f"{BASE_URI}/v2.0/{TENANT_ID}/{ENVIRONMENT}/api/v2.0"


def custom_root():
    return f"{BASE_URI}/v2.0/{TENANT_ID}/{ENVIRONMENT}/api/codex/automation/v1.0"


def odata_quote(value):
    return "'" + value.replace("'", "''") + "'"


def company_id(token):
    filter_text = f"name eq {odata_quote(COMPANY)}"
    query = urllib.parse.urlencode({"$filter": filter_text}, safe="'")
    url = f"{api_root()}/companies?{query}"
    rows = request("GET", url, token).get("value", [])
    if not rows:
        raise SystemExit(f"Company not found: {COMPANY}")
    return rows[0]["id"]


def get_all(token, url):
    rows = []
    while url:
        data = request("GET", url, token)
        rows.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
    return rows


def ensure_bc_application(token, client_id):
    cid = company_id(token)
    apps_url = f"{custom_root()}/companies({cid})/codexAadApplications"
    apps = get_all(token, apps_url)
    app = next((a for a in apps if str(a.get("clientId", "")).lower() == client_id.lower()), None)
    payload = {
        "clientId": client_id,
        "description": "Codex BC Automation",
        "contactInformation": "Codex local automation",
    }
    if app:
        if app.get("state") != "Disabled":
            app = request("PATCH", f"{apps_url}({app['id']})", token, {"state": "Disabled"}, headers={"If-Match": "*"})
        app = request("PATCH", f"{apps_url}({app['id']})", token, payload, headers={"If-Match": "*"})
    else:
        app = request("POST", apps_url, token, payload)
    app = request("PATCH", f"{apps_url}({app['id']})", token, {"state": "Enabled"}, headers={"If-Match": "*"})
    user_id = app.get("userId")
    if not user_id:
        apps = get_all(token, apps_url)
        app = next((a for a in apps if str(a.get("clientId", "")).lower() == client_id.lower()), app)
        user_id = app.get("userId")
    if not user_id:
        raise SystemExit(f"BC AAD application was created but no userId was returned:\n{json.dumps(app, indent=2)}")

    ac_url = f"{custom_root()}/companies({cid})/codexAccessControls"
    existing = get_all(token, ac_url)
    for role_id in ("LOGIN", "D365 AUTOMATION", "CODEX AUTOMATION"):
        found = any(
            str(a.get("userSecurityId", "")).lower() == user_id.lower()
            and a.get("roleId") == role_id
            and (a.get("companyName") or "") == ""
            for a in existing
        )
        if found:
            continue
        request("POST", ac_url, token, {"userSecurityId": user_id, "roleId": role_id, "companyName": ""})


def set_user_env(name, value):
    if os.name == "nt":
        import winreg

        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Environment")
        try:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        finally:
            winreg.CloseKey(key)
    else:
        subprocess.run(
            ["sh", "-lc", f"export {name}=\"$1\"", "_", value],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    os.environ[name] = value


def test_s2s(client_id, secret):
    token = form_request(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": secret,
            "scope": f"{BASE_URI}/.default",
        },
    )["access_token"]
    cid = company_id(token)
    data = request("GET", f"{custom_root()}/companies({cid})/codexItems?$top=1", token)
    return len(data.get("value", []))


def main():
    skip_bc_registration = "--skip-bc-registration" in sys.argv[1:]
    graph_token = device_token(
        [
            "https://graph.microsoft.com/Application.ReadWrite.All",
            "https://graph.microsoft.com/AppRoleAssignment.ReadWrite.All",
            "https://graph.microsoft.com/Directory.Read.All",
        ],
        "Graph",
    )
    client_id, secret = ensure_graph_application(graph_token)
    print(f"Created or updated Entra app: {client_id}", flush=True)

    if not skip_bc_registration:
        bc_token = device_token([f"{BASE_URI}/user_impersonation", "offline_access"], "Business Central")
        ensure_bc_application(bc_token, client_id)

    set_user_env("BC_TENANT_ID", TENANT_ID)
    set_user_env("BC_ENVIRONMENT", ENVIRONMENT)
    set_user_env("BC_COMPANY", COMPANY)
    set_user_env("BC_CLIENT_ID", client_id)
    set_user_env("BC_CLIENT_SECRET", secret)

    test_s2s(client_id, secret)
    print(json.dumps({"clientId": client_id, "tenantId": TENANT_ID, "environment": ENVIRONMENT, "company": COMPANY, "s2sTest": "ok"}, indent=2))


if __name__ == "__main__":
    sys.exit(main())
