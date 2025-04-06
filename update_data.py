from update_firestore_data import update_all

def handler(request, response):
    try:
        update_all()
        return response.status(200).json({
            "message": "Firestore updated successfully."
        })
    except Exception as e:
        return response.status(500).json({
            "error": str(e)
        })
