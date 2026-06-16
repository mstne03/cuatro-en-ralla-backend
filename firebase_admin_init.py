import json
import firebase_admin
from firebase_admin import credentials
from config import settings


def _build_credentials() -> credentials.Base:
    if settings.firebase_service_account_json:
        return credentials.Certificate(json.loads(settings.firebase_service_account_json))
    return credentials.Certificate(settings.firebase_service_account_path)


def get_firebase_app() -> firebase_admin.App:
    try:
        return firebase_admin.get_app()
    except ValueError:
        return firebase_admin.initialize_app(_build_credentials())
