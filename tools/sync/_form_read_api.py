"""Lê estrutura de Google Form via API (forms.body scope)."""
import sys, json
sys.path.insert(0, r"G:\O meu disco\AUTOMAÇÕES\tools\gws")
from gws_auth import get_credentials
from googleapiclient.discovery import build

FORM_ID = sys.argv[1]
creds = get_credentials()
svc = build("forms", "v1", credentials=creds)
form = svc.forms().get(formId=FORM_ID).execute()
print(json.dumps(form, ensure_ascii=False, indent=2))
