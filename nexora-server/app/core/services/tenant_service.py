# app/core/services/tenant_service.py
from typing import Dict, List, Optional
from app.core.database.pocketbase_client import pb
from app.core.database.tenant_manager import resolve_collection

class TenantService:
    def __init__(self):
        self.tenant_collection = "tenants"
        self.tenant_cache = {}  # Simple in-memory cache
    
    def get_tenant_by_id(self, tenant_id: str) -> Optional[Dict]:
        """Get tenant information by ID"""
        # Check cache first
        if tenant_id in self.tenant_cache:
            return self.tenant_cache[tenant_id]
        
        try:
            tenant = pb.collection(self.tenant_collection).get_one(tenant_id)
            # Cache the tenant
            self.tenant_cache[tenant_id] = tenant
            return tenant
        except Exception:
            return None
    
    def get_all_tenants(self) -> List[Dict]:
        """Get all active tenants"""
        try:
            tenants = pb.collection(self.tenant_collection).get_full_list()
            
            # Update cache with fetched tenants
            for tenant in tenants:
                self.tenant_cache[tenant.get('id')] = tenant
                
            return tenants
        except Exception:
            return []
    
    def create_tenant(self, tenant_data: Dict) -> Dict:
        """Create a new tenant"""
        tenant = pb.collection(self.tenant_collection).create(tenant_data)
        
        # Initialize tenant-specific collections
        self._initialize_tenant_collections(tenant.get('id'))
        
        # Update cache
        self.tenant_cache[tenant.get('id')] = tenant
        return tenant
    
    def update_tenant(self, tenant_id: str, tenant_data: Dict) -> Dict:
        """Update an existing tenant"""
        tenant = pb.collection(self.tenant_collection).update(tenant_id, tenant_data)
        
        # Update cache
        self.tenant_cache[tenant_id] = tenant
        return tenant
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant (soft delete recommended)"""
        try:
            pb.collection(self.tenant_collection).update(
                tenant_id, 
                {"isActive": False}
            )
            
            # Remove from cache
            if tenant_id in self.tenant_cache:
                del self.tenant_cache[tenant_id]
                
            return True
        except Exception:
            return False
    
    def _initialize_tenant_collections(self, tenant_id: str):
        """Initialize required collections for a new tenant"""
        # This would create any necessary collections or records
        # for the new tenant in your database
        base_collections = [
            "roles", "departments", "permissions", 
            "tags", "rooms", "users", "visitors"
        ]
        
        # This is just a placeholder - actual implementation would
        # depend on how you're setting up collections in PocketBase
        for collection in base_collections:
            tenant_collection = resolve_collection(collection, tenant_id)
            # Initialize collection if needed


# Singleton instance
tenant_service = TenantService()

# Export commonly used functions
get_tenant_by_id = tenant_service.get_tenant_by_id
get_all_tenants = tenant_service.get_all_tenants
create_tenant = tenant_service.create_tenant
update_tenant = tenant_service.update_tenant
delete_tenant = tenant_service.delete_tenant