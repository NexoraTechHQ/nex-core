#app/core/database/pocketbase_client.py
import requests


class PocketBaseClient:
    def __init__(self, base_url="http://localhost:8090", auth_token=None):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json"
        }
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"

    def collection(self, collection_name):
        return PocketBaseCollection(self.base_url, collection_name, self.headers)
        
    def auth_with_password(self, username, password):
        """Authenticate user with email/username and password"""
        res = requests.post(
            f"{self.base_url}/api/collections/users/auth-with-password",
            json={"identity": username, "password": password}
        )
        
        if res.status_code == 200:
            auth_data = res.json()
            # Update client headers with the new token
            self.headers["Authorization"] = f"Bearer {auth_data['token']}"
            return auth_data
        return None
    
    def refresh_auth(self, token):
        """Refresh authentication token"""
        res = requests.post(
            f"{self.base_url}/api/collections/users/auth-refresh",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if res.status_code == 200:
            auth_data = res.json()
            self.headers["Authorization"] = f"Bearer {auth_data['token']}"
            return auth_data
        return None
        
    def get_auth_user(self, token):
        """Get the authenticated user information"""
        res = requests.get(
            f"{self.base_url}/api/collections/users/auth-record",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if res.status_code == 200:
            return res.json()
        return None

class PocketBaseCollection:
    def __init__(self, base_url, collection, headers):
        self.collection = collection
        self.base_url = base_url
        self.headers = headers

    def get_full_list(self):
        res = requests.get(
            f"{self.base_url}/api/collections/{self.collection}/records", headers=self.headers)
        res.raise_for_status()
        return res.json().get("items", [])

    def get_list(self, query_params=None):
        from urllib.parse import urlencode
        query = f"?{urlencode(query_params)}" if query_params else ""
        res = requests.get(
            f"{self.base_url}/api/collections/{self.collection}/records{query}", headers=self.headers)
        res.raise_for_status()
        return res.json()

    def get_one(self, record_id):
        res = requests.get(
            f"{self.base_url}/api/collections/{self.collection}/records/{record_id}", headers=self.headers)
        res.raise_for_status()
        return res.json()

    def create(self, data):
        res = requests.post(
            f"{self.base_url}/api/collections/{self.collection}/records", json=data, headers=self.headers)
        res.raise_for_status()
        return res.json()

    def update(self, record_id, data):
        res = requests.patch(
            f"{self.base_url}/api/collections/{self.collection}/records/{record_id}", json=data, headers=self.headers)
        res.raise_for_status()
        return res.json()

    def delete(self, record_id):
        res = requests.delete(
            f"{self.base_url}/api/collections/{self.collection}/records/{record_id}", headers=self.headers)
        res.raise_for_status()
        return {"status": "ok"}


# Export client as `pb`
pb = PocketBaseClient()
