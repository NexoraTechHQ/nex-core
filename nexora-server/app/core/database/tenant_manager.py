def resolve_collection(base: str, tenant_id: str) -> str:
    return f"vms_{tenant_id}_{base}"
