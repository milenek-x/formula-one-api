# api/update_data.py
from update_firestore_data import update_all

def handler(request):
    update_all()
    return {
        "statusCode": 200,
        "body": "Firestore updated successfully."
    }
