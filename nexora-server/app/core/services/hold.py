import json
import httpx
import random
import string
from typing import Dict, List

# Initialize PocketBase client
PB_URL = "http://localhost:8090/"
http_client = httpx.Client(verify=False)

# Function to authenticate using REST API


def authenticate_admin():
    """Authenticate using REST API for admin login."""
    try:
        response = http_client.post(
            f"{PB_URL}api/users/auth-with-password",  # Endpoint for user auth
            json={
                "identity": "admin@example.com",  # Change to your admin email
                "password": "adminadmin11"  # Change to your admin password
            }
        )
        response.raise_for_status()  # Will raise an error if the status code is 4xx or 5xx
        auth_data = response.json()  # The token will be in the response
        print("Admin authenticated successfully!")
        return auth_data["token"]
    except httpx.HTTPStatusError as e:
        print(f"Authentication failed: {e}")
        print(f"Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"Unexpected error during authentication: {e}")
        return None

# Utility functions to clean fields and check relations


def clean_field(field: Dict) -> Dict:
    """Remove unsupported field properties for the Python client."""
    supported_keys = ["name", "type", "required",
                      "presentable", "unique", "options"]
    if field["type"] == "autodate":
        field["type"] = "date"  # Convert autodate to date
    return {key: field[key] for key in supported_keys if key in field}


def is_relation_field(field: Dict) -> bool:
    """Check if a field is a relation field."""
    return field["type"] == "relation" and "options" in field and "collectionId" in field["options"]


def is_tenant_id_unique(tenant_id: str) -> bool:
    """Check if tenant_id already exists in vms_tenants collection."""
    try:
        result = pb.collection('vms_tenants').get_list(
            1, 1, {'filter': f'tenant_id = "{tenant_id}"'})
        return len(result.items) == 0
    except Exception:
        return True


def create_tenant(tenant_name: str) -> str:
    """Create a new tenant with a unique 8-character tenant_id."""
    max_attempts = 10
    for _ in range(max_attempts):
        tenant_id = generate_tenant_id()
        if is_tenant_id_unique(tenant_id):
            try:
                tenant_data = {
                    "name": tenant_name,
                    "tenant_id": tenant_id
                }
                record = pb.collection('vms_tenants').create(tenant_data)
                print(
                    f"Tenant '{tenant_name}' created successfully with ID: {tenant_id}")
                return tenant_id
            except Exception as e:
                print(f"Error creating tenant: {e}")
                continue

    raise Exception(
        f"Failed to generate unique tenant_id after {max_attempts} attempts")


def get_non_relation_fields(collection: Dict) -> List[Dict]:
    """Extract non-relation fields from a collection schema."""
    if "schema" not in collection:
        return []
    return [clean_field(field) for field in collection["schema"] if not is_relation_field(field)]


def get_relation_fields(collection: Dict) -> List[Dict]:
    """Extract relation fields from a collection schema."""
    if "schema" not in collection:
        return []
    return [clean_field(field) for field in collection["schema"] if is_relation_field(field)]


def generate_tenant_id(length=8) -> str:
    """Generate a random alphanumeric tenant_id."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Main function for creating collections using JSON schema


def create_collections_from_json(tenant_name: str, tenant_id: str):
    # Step 1: Authenticate using the new REST API method
    token = authenticate_admin()
    if not token:
        return  # Exit if authentication fails

    # Step 2: Create tenant and get auto-generated tenant_id (assuming tenant exists)
    prefix = f"prefix_{tenant_id}_"
    print(f"Using prefix: {prefix}")

    # Step 3: Read the JSON schema
    with open('pb_schema.json', 'r') as f:
        schema = json.load(f)

    # Dictionary to store original ID to new ID mapping
    id_mapping: Dict[str, str] = {}

    # Step 4: First pass - create all collections with non-relation fields
    for collection in schema:
        original_name = collection["name"]
        prefixed_name = f"{prefix}{original_name}"

        # Get non-relation fields
        non_relation_fields = get_non_relation_fields(collection)

        # If no non-relation fields exist, add a dummy field
        if not non_relation_fields and "schema" in collection:
            non_relation_fields = [{
                "name": "dummy_field",
                "type": "text",
                "required": False,
                "options": {}
            }]
            print(f"Added dummy field to {prefixed_name} for initial creation")

        # Create the collection with non-relation fields
        collection_data = {
            "name": prefixed_name,
            "type": collection["type"],
            "schema": non_relation_fields,
            "listRule": collection.get("listRule"),
            "viewRule": collection.get("viewRule"),
            "createRule": collection.get("createRule"),
            "updateRule": collection.get("updateRule"),
            "deleteRule": collection.get("deleteRule"),
            "options": collection.get("options", {})
        }

        try:
            created_collection = pb.collections.create(collection_data)
            print(f"{prefixed_name} created successfully!")
            print(f"{prefixed_name} ID:", created_collection.id)
            id_mapping[collection["id"]] = created_collection.id
        except Exception as e:
            print(f"Error creating {prefixed_name}: {e}")
            continue

    # Step 5: Second pass - update collections to add relation fields
    for collection in schema:
        original_name = collection["name"]
        prefixed_name = f"{prefix}{original_name}"
        collection_id = id_mapping.get(collection["id"])

        if not collection_id:
            print(f"Skipping {prefixed_name} - not created in first pass")
            continue

        # Get all fields including relations (with updated collection IDs)
        all_fields = []
        if "schema" in collection:
            for field in collection["schema"]:
                cleaned_field = clean_field(field)

                # Handle relation fields
                if is_relation_field(field):
                    original_related_id = field["options"]["collectionId"]
                    if original_related_id in id_mapping:
                        cleaned_field["options"] = {
                            "collectionId": id_mapping[original_related_id],
                            "cascadeDelete": field["options"].get("cascadeDelete", False),
                            "minSelect": field["options"].get("minSelect"),
                            "maxSelect": field["options"].get("maxSelect"),
                            "displayFields": field["options"].get("displayFields")
                        }

                all_fields.append(cleaned_field)

        # For collections that had a dummy field, remove it now
        if "dummy_field" in [f["name"] for f in all_fields]:
            all_fields = [f for f in all_fields if f["name"] != "dummy_field"]
            print(f"Removed dummy field from {prefixed_name}")

        # Update the collection with all fields
        try:
            update_data = {"schema": all_fields}
            pb.collections.update(collection_id, update_data)
            print(f"Updated {prefixed_name} with all fields and relations")
        except Exception as e:
            print(f"Error updating {prefixed_name}: {e}")

    # Step 6: Verification
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = http_client.get(f"{PB_URL}api/collections", headers=headers)
        response.raise_for_status()
        collections = response.json()
        print("\nCurrent collections (raw API):")
        for collection in collections["items"]:
            if collection['name'].startswith(prefix):
                print(f"- {collection['name']} (ID: {collection['id']})")
    except Exception as e:
        print(f"\nError during verification: {e}")


# Example execution
if __name__ == "__main__":
    tenant_name = input("Enter tenant name: ")
    tenant_id = input("Enter tenant ID: ")
    create_collections_from_json(tenant_name, tenant_id)
