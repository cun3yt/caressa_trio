import os
from google.oauth2 import service_account
import json
from caressa.settings import GOOGLE_APPLICATION_CREDENTIALS_RAW

_service_account_info = json.loads(GOOGLE_APPLICATION_CREDENTIALS_RAW)
credentials = service_account.Credentials.from_service_account_info(_service_account_info)
