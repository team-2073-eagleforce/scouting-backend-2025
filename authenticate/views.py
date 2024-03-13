import os
from django.shortcuts import render, redirect
from django.urls import reverse
import google_auth_oauthlib.flow
import requests

from constants import AUTHORIZED_EMAIL

# Create your views here.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email']

client_config = {
    "web": {
        "client_id": "351274848173-0eepc6g5hc4ri03l67rql056p7e6g8nv.apps.googleusercontent.com",
        "project_id": "scouting-excel-test",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": [
            "https://silver-chainsaw-4w5jqgp7xw4fjx96-8000.app.github.dev/auth/oauth2callback",
            "https://eagleforce-backend.onrender.com/auth/oauth2callback"
        ],
        "javascript_origins": [
            "https://silver-chainsaw-4w5jqgp7xw4fjx96-8000.app.github.dev",
            "https://eagleforce-backend.onrender.com"
        ]
    }
}


def authorize(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_config, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback')) #"https://silver-chainsaw-4w5jqgp7xw4fjx96-8000.app.github.dev/auth/oauth2callback" #

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    # session['state'] = state

    return redirect(authorization_url)


def oauth2callback(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_config, scopes=SCOPES) # , state=state
    flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback')) # "https://silver-chainsaw-4w5jqgp7xw4fjx96-8000.app.github.dev/auth/oauth2callback"

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    cred = credentials_to_dict(credentials)
    request.session['credentials'] = cred

    r = requests.get(f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={cred["token"]}').json()

    request.session["name"] = r["given_name"] + " " + r["family_name"]

    if r["email"] not in AUTHORIZED_EMAIL: #and r["email"] not in PIT_SCOUT_EMAIL:
        return "405 UNAUTHORIZED"

    request.session["email"] = r["email"]

    return redirect('/')


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}