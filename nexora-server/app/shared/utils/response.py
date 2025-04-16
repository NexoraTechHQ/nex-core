def success_response(message: str, data=None, status_code=200):
    from flask import jsonify
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code


def error_response(message: str, status_code=400):
    from flask import jsonify
    response = {
        "success": False,
        "message": message,
        "data": None
    }
    return jsonify(response), status_code


def sanitize_record(record):
    """Remove PocketBase internal fields from a single record."""
    blacklist = {"collectionId", "collectionName"}
    return {k: v for k, v in record.items() if k not in blacklist}


def sanitize_response(response):
    """Remove internal fields from PocketBase list response."""
    if "items" in response:
        response["items"] = [sanitize_record(r) for r in response["items"]]
    else:
        response = sanitize_record(response)
    return response
