import json, os, time, urllib.parse, urllib.request, urllib.error, winreg
TENANT='eb4005a6-4bc1-41d0-93be-6595f1a5bc80'; ENV='BCDemoG'; COMPANY='G7'; BASE='https://api.businesscentral.dynamics.com'; PUBLIC='14d82eec-204b-4c2f-b7e8-296a70dab67e'
key=winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment')
def env(name):
    try: return winreg.QueryValueEx(key, name)[0]
    except FileNotFoundError: return os.environ.get(name)
CLIENT=env('BC_CLIENT_ID')
def form(url, data):
    req=urllib.request.Request(url,data=urllib.parse.urlencode(data).encode(),headers={'Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req,timeout=60) as r: return json.loads(r.read().decode())
def device_token():
    d=form(f'https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/devicecode', {'client_id':PUBLIC,'scope':f'{BASE}/user_impersonation offline_access'})
    print(f"Business Central device code: {d['user_code']}", flush=True); print(d['message'], flush=True)
    deadline=time.time()+int(d.get('expires_in',900)); interval=int(d.get('interval',5))
    while time.time()<deadline:
        time.sleep(interval)
        try: return form(f'https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token', {'grant_type':'urn:ietf:params:oauth:grant-type:device_code','client_id':PUBLIC,'device_code':d['device_code']})['access_token']
        except urllib.error.HTTPError as e:
            body=json.loads(e.read().decode())
            if body.get('error') in ('authorization_pending','slow_down'):
                if body.get('error')=='slow_down': interval+=5
                continue
            raise
    raise SystemExit('expired')
def http(method,url,token,payload=None):
    headers={'Authorization':f'Bearer {token}','Accept':'application/json'}; data=None
    if payload is not None: headers['Content-Type']='application/json'; data=json.dumps(payload).encode()
    req=urllib.request.Request(url,data=data,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            raw=r.read().decode(); return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        print('HTTP_ERROR',method,url,e.code); print(e.read().decode('utf-8',errors='replace')); raise SystemExit(1)
tok=device_token()
query=urllib.parse.urlencode({'$filter':f"name eq '{COMPANY}'"}, safe="'")
cid=http('GET',f'{BASE}/v2.0/{TENANT}/{ENV}/api/v2.0/companies?{query}',tok)['value'][0]['id']
root=f'{BASE}/v2.0/{TENANT}/{ENV}/api/codex/automation/v1.0/companies({cid})'
apps=http('GET',f'{root}/codexAadApplications',tok).get('value',[])
app=next(a for a in apps if str(a.get('clientId','')).lower()==CLIENT.lower())
uid=app['userId']
existing=http('GET',f'{root}/codexAccessControls',tok).get('value',[])
result=[]
for role in ['D365 BUS FULL ACCESS','SUSTAINABILITY READ']:
    if any(str(a.get('userSecurityId','')).lower()==str(uid).lower() and str(a.get('roleId','')).upper()==role and (a.get('companyName') or '')=='' for a in existing):
        result.append({'role':role,'status':'alreadyAssigned'}); continue
    http('POST',f'{root}/codexAccessControls',tok,{'userSecurityId':uid,'roleId':role,'companyName':''})
    result.append({'role':role,'status':'assigned'})
print(json.dumps({'result':result}, indent=2), flush=True)
