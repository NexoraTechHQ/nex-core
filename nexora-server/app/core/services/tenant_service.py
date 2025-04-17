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
                raise InternalServerException(f"Failed to initialize collection {collection_name}: {str(e)}")

# Create singleton instance
tenant_service = TenantService()