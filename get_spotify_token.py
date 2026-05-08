"""
Spotify Refresh Token Generator (No Local Server Required)
-----------------------------------------------------------
This version works even if localhost redirect URIs are blocked.
You just paste the redirect URL from your browser manually.

Setup:
  1. In your Spotify App settings, set Redirect URI to:
         http://localhost:8888/callback
     (type it, press ENTER to add as a tag, then click Save)

  2. Run this script:
         pip install requests
         python get_spotify_token.py

  3. Open the printed URL in your browser, log in, approve access.
     Your browser will show a "This site can't be reached" error — that's OK!
     Copy the FULL URL from your browser's address bar and paste it here.
"""

import base64
import urllib.parse
import requests

# ─────────────────────────────────────────
# PASTE YOUR VALUES HERE
# ─────────────────────────────────────────
CLIENT_ID     = input("Paste your Spotify CLIENT_ID: ").strip()
CLIENT_SECRET = input("Paste your Spotify CLIENT_SECRET: ").strip()
# ─────────────────────────────────────────

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE        = "user-read-currently-playing user-read-recently-played"
AUTH_URL     = "https://accounts.spotify.com/authorize"
TOKEN_URL    = "https://accounts.spotify.com/api/token"

# Step 1: Build and print the auth URL
params = {
    "client_id":     CLIENT_ID,
    "response_type": "code",
    "redirect_uri":  REDIRECT_URI,
    "scope":         SCOPE,
}
auth_link = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

print("\n" + "=" * 60)
print("STEP 1: Open this URL in your browser:")
print("=" * 60)
print(auth_link)
print("=" * 60)
print("\nSPTEP 2: Log in to Spotify and click 'Agree'.")
print("Your browser will show a 'This site can't be reached' error.")
print("That's EXPECTED. Just copy the full URL from the address bar.\n")

# Step 2: Ask user to paste the redirect URL
redirect_response = input("STEP 3: Paste the full URL from your browser here:\n> ").strip()

# Step 3: Extract the code from the pasted URL
parsed = urllib.parse.urlparse(redirect_response)
code = urllib.parse.parse_qs(parsed.query).get("code", [None])[0]

if not code:
    print("\n❌ Could not find a 'code' in the URL you pasted.")
    print("   Make sure you copied the full URL from the address bar.")
    exit(1)

print("\n✅ Authorization code extracted! Fetching your refresh token...")

# Step 4: Exchange code for tokens
auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
response = requests.post(
    TOKEN_URL,
    data={
        "grant_type":   "authorization_code",
        "code":         code,
        "redirect_uri": REDIRECT_URI,
    },
    headers={"Authorization": f"Basic {auth_header}"},
)

if response.status_code != 200:
    print(f"\n❌ Token exchange failed: {response.text}")
    exit(1)

tokens = response.json()
refresh_token = tokens.get("refresh_token")

print("\n" + "=" * 60)
print("✅ SUCCESS! Your Refresh Token:")
print("=" * 60)
print(refresh_token)
print("=" * 60)
print("\n📋 Add this to GitHub Secrets as:  SPOTIFY_REFRESH_TOKEN")
print("   Repo → Settings → Secrets → Actions → New repository secret\n")
