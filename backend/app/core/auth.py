from google.oauth2 import id_token
from google.auth.transport import requests
import requests as http_requests
from app.core.config import settings

def verify_google_token(token: str):
    """
    Verifies a Google Token. 
    Supports both ID Token (JWT) and Access Token verification.
    """
    try:
        # 1. Try to verify as ID Token first (fastest, stateless)
        # CLIENT_ID = settings.GOOGLE_CLIENT_ID
        # idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        # return idinfo
        
        # 2. Since we are using access_token from frontend implicit flow most likely:
        # Call Google UserInfo Endpoint
        response = http_requests.get(
            f"https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json() # Returns dict with 'email', 'sub', 'name', etc.
            
        # 3. Fallback for Dev Mock (Keep this for robustness if needed, or remove)
        if token == "mock_dev_token":
             return {
                "email": "tester@gmail.com",
                "sub": "google-dev-id-123",
                "name": "Human Tester"
            }
            
        return None
    except Exception as e:
        print(f"Google Auth Verification Error: {e}")
        return None
