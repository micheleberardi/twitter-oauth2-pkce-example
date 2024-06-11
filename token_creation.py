import base64
import hashlib
import os
import requests
import urllib.parse

# Step 1: Generate a code verifier and code challenge
def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(40)).rstrip(b'=').decode('utf-8')

def generate_code_challenge(verifier):
    challenge = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(challenge).rstrip(b'=').decode('utf-8')

code_verifier = generate_code_verifier()
code_challenge = generate_code_challenge(code_verifier)
state = base64.urlsafe_b64encode(os.urandom(30)).rstrip(b'=').decode('utf-8')


client_id = 'client_id'  # Replace with your actual Client ID
redirect_uri = 'https://callback.domain.com'  # Replace with your actual Redirect URI

# Step 2: Direct user to authorization URL
auth_url = (
    "https://twitter.com/i/oauth2/authorize?"
    "response_type=code"
    f"&client_id={client_id}"
    f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
    f"&scope=tweet.read%20tweet.write%20users.read%20offline.access"
    f"&state={state}"
    f"&code_challenge={code_challenge}"
    "&code_challenge_method=S256"
)
print(f"Go to the following URL and authorize the app: {auth_url}")

# Step 3: After authorization, capture 'code' and 'state' from the callback URL
# In a real application, you would need to handle the callback URL and extract these parameters
code = input('Enter the authorization code you received: ')
received_state = input('Enter the state you received: ')

if received_state != state:
    raise ValueError("State does not match")

# Step 4: Exchange authorization code for access token
token_url = "https://api.twitter.com/2/oauth2/token"
token_data = {
    'client_id': client_id,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': redirect_uri,
    'code_verifier': code_verifier,
}

response = requests.post(token_url, data=token_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
token_response = response.json()

access_token = token_response['access_token']
refresh_token = token_response['refresh_token']

# Step 5: Post a tweet using the access token
tweet_text = "Hello World! This is a tweet from my app."

def post_tweet(text, access_token):
    tweet_url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text
    }
    response = requests.post(tweet_url, headers=headers, json=payload)
    if response.status_code == 201:
        print("Successfully posted the tweet")
        return response.json()
    else:
        print(f"Tweet creation failed: {response.text}")
        raise Exception(f"Tweet creation failed with status code {response.status_code}")

post_tweet(tweet_text, access_token)

# Refresh access token when needed
def refresh_access_token(refresh_token, client_id):
    token_url = "https://api.twitter.com/2/oauth2/token"
    token_data = {
        'client_id': client_id,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }

    response = requests.post(token_url, data=token_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    token_response = response.json()
    print(token_response)

    new_access_token = token_response['access_token']
    new_refresh_token = token_response.get('refresh_token', refresh_token)
    return new_access_token, new_refresh_token

new_access_token, new_refresh_token = refresh_access_token(refresh_token, client_id)
