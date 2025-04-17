# app/gateway/service_discovery.py
import json
import os
from typing import Dict, List, Optional

class ServiceRegistry:
    """Simple service registry for managing service endpoints"""
    
    def __init__(self):
        self.services = {}
        self._load_from_env()
    
    def _load_from_env(self):
        """Load service configuration from environment variables or config file"""
        # Try to load from JSON config file
        config_path = os.environ.get('SERVICE_REGISTRY_CONFIG', 'services.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.services = json.load(f)
        else:
            # Default configuration if no file exists
            self.services = {
                'inventory': {
                    'instances': ['http://inventory-service:5001'],
                    'prefix': '/inventory'
                },
                'vms': {
                    'instances': ['http://vms-service:5010'],
                    'prefix': '/vms'
                },
                'access-control': {
                    'instances': ['http://access-control-service:5020'],
                    'prefix': '/access-control'
                }
            }
    
    def register_service(self, name: str, url: str, prefix: str = None):
        """Register a new service instance"""
        if name not in self.services:
            self.services[name] = {
                'instances': [url],
                'prefix': prefix or f'/{name}'
            }
        else:
            if url not in self.services[name]['instances']:
                self.services[name]['instances'].append(url)
    
    def deregister_service(self, name: str, url: str):
        """Remove a service instance"""
        if name in self.services and url in self.services[name]['instances']:
            self.services[name]['instances'].remove(url)
            
            # Remove the service entry if no instances remain
            if not self.services[name]['instances']:
                del self.services[name]
    
    def get_service_instances(self, name: str) -> List[str]:
        """Get all instances of a service"""
        if name not in self.services:
            return []
        return self.services[name]['instances']
    
    def get_service_prefix(self, name: str) -> Optional[str]:
        """Get the URL prefix for a service"""
        if name not in self.services:
            return None
        return self.services[name]['prefix']
    
    def get_all_services(self) -> Dict:
        """Get all registered services"""
        return self.services


# Create a singleton instance
service_registry = ServiceRegistry()