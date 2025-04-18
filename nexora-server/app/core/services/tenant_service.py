import json
import os
from typing import Dict, List, Optional
from app.core.database.pocketbase_client import pb
from app.shared.exceptions import ConflictException, InternalServerException


class TenantService:
    def __init__(self):
        self.pb = pb  # Use the PocketBase client instance

    def create_tenant(self, tenant_type: str, tenant_data: dict) -> dict:
        """
        Create a new tenant in the 'tenants' collection.

        Args:
            tenant_type: 'individual' or 'business'
            tenant_data: Dictionary containing tenant details (e.g., name, company_name)

        Returns:
            Dictionary with the created tenant's data
        """
        try:
            tenant_data = {
                'type': tenant_type,
                'name': tenant_data.get('name', ''),
                'company_name': tenant_data.get('company_name', ''),
                'tax_id': tenant_data.get('tax_id', ''),
                'contact_phone': tenant_data.get('contact_phone', ''),
                'status': 'active',
                'address': tenant_data.get('address', ''),
                'metadata': tenant_data.get('metadata', {})
            }
            tenant = self.pb.collection('tenants').create(tenant_data)
            # Initialize tenant-specific collections
            self._initialize_tenant_collections(tenant['id'])
            return tenant
        except Exception as e:
            if "already exists" in str(e).lower():
                raise ConflictException("Tenant already exists")
            raise InternalServerException(f"Failed to create tenant: {str(e)}")

    def _initialize_tenant_collections(self, tenant_id: str):
        """
        Create default collections for a new tenant (e.g., vms_[tenant_id]_rooms).

        Args:
            tenant_id: ID of the tenant
        """
        collections = ['rooms', 'departments', 'users']
        for col in collections:
            collection_name = f"vms_{tenant_id}_{col}"
            try:
                # Check if collection exists; if not, create it
                # PocketBase doesn't provide a direct API to check collection existence,
                # so you may need to attempt creation or use admin API
                # For simplicity, assume creation is handled elsewhere or manually for now
                pass
            except Exception as e:
                raise InternalServerException(
                    f"Failed to initialize collection {collection_name}: {str(e)}")

    def clean_field(self, field: Dict) -> Dict:
        """Remove unsupported field properties for the PocketBase client."""
        supported_keys = ["name", "type", "required",
                          "presentable", "unique", "options"]
        if field["type"] == "autodate":
            field["type"] = "date"  # Convert autodate to date
        return {key: field[key] for key in supported_keys if key in field}

    def is_relation_field(self, field: Dict) -> bool:
        """Check if a field is a relation field."""
        return field["type"] == "relation" and "options" in field and "collectionId" in field["options"]

    def get_non_relation_fields(self, collection: Dict) -> List[Dict]:
        """Extract non-relation fields from a collection schema."""
        if "schema" not in collection:
            return []

        return [
            self.clean_field(field)
            for field in collection["schema"]
            if not self.is_relation_field(field)
        ]

    def get_relation_fields(self, collection: Dict) -> List[Dict]:
        """Extract relation fields from a collection schema."""
        if "schema" not in collection:
            return []

        return [
            self.clean_field(field)
            for field in collection["schema"]
            if self.is_relation_field(field)
        ]

    def create_tenant_configuration(self, tenant_id: str) -> Optional[Dict]:
        """Create a complete tenant configuration"""

        # Calculate path to pb_schema.json
        current_dir = os.path.dirname(
            os.path.abspath(__file__))
        app_dir = os.path.dirname(current_dir)
        schema_path = os.path.join(
            app_dir, 'database' 'schema-collections', 'v1', 'pb_schema.json')

        try:
            # Load schema template
            with open(schema_path, 'r') as f:
                schema = json.load(f)

            # Dictionary to store original ID to new ID mapping
            id_mapping = {}
            app_prefix = "vms"

            # First pass - create all collections with non-relation fields
            for collection in schema:
                original_name = collection["name"]
                base_name = original_name.split('_')[-1]
                collection_name = f"{app_prefix}_{tenant_id}_{base_name}"
                # Get non-relation fields
                non_relation_fields = self.get_non_relation_fields(collection)

                # If no non-relation fields exist, add a dummy field
                if not non_relation_fields and "schema" in collection:
                    non_relation_fields = [{
                        "name": "dummy_field",
                        "type": "text",
                        "required": False,
                        "options": {}
                    }]
                    print(
                        f"Added dummy field to {collection_name} for initial creation")

                # Create the collection with non-relation fields
                collection_data = {
                    "name": collection_name,
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
                    created_collection = self.pb.create_collection(
                        collection_data)
                    print(f"{collection_name} created successfully!")
                    id_mapping[collection["id"]] = created_collection["id"]
                except Exception as e:
                    print(f"Error creating {collection_name}: {e}")
                    continue

            # Second pass - update collections to add relation fields
            for collection in schema:
                original_name = collection["name"]
                collection_id = id_mapping.get(collection["id"])
                base_name = original_name.split('_')[-1]
                collection_name = f"{app_prefix}_{tenant_id}_{base_name}"

                if not collection_id:
                    print(
                        f"Skipping {collection_name} - not created in first pass")
                    continue

                # Get all fields including relations (with updated collection IDs)
                all_fields = []
                if "schema" in collection:
                    for field in collection["schema"]:
                        cleaned_field = self.clean_field(field)

                        # Handle relation fields
                        if self.is_relation_field(field):
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
                if any(f["name"] == "dummy_field" for f in all_fields):
                    all_fields = [
                        f for f in all_fields if f["name"] != "dummy_field"]
                    print(f"Removed dummy field from {collection_name}")

                # Update the collection with all fields
                try:
                    update_data = {"schema": all_fields}
                    self.pb.update_collection(collection_id, update_data)
                    print(
                        f"Updated {collection_name} with all fields and relations")
                except Exception as e:
                    print(f"Error updating {collection_name}: {e}")

        except FileNotFoundError:
            print(f"Schema file not found at {schema_path}")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON in schema file at {schema_path}")
            return None
        except Exception as e:
            print(f"Unexpected error during tenant configuration: {e}")
            return None


# Create singleton instance
tenant_service = TenantService()
