import os
from django.shortcuts import render, redirect
from django.urls import reverse
import google_auth_oauthlib.flow
import requests

from constants import AUTHORIZED_EMAIL
from .models import AuthorizedUser

# Create your views here.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email']

client_config = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "project_id": "scouting-excel-test",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": [
            "http://localhost:8000/auth/oauth2callback/",
            "http://127.0.0.1:8000/auth/oauth2callback/",
            "https://scouting.chrisccluk.live/"
        ],
        "javascript_origins": [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "https://scouting.chrisccluk.live"
        ]
    }
}


def authorize(request):
    # If user is already authenticated, redirect to home
    if request.session.get('email'):
        return redirect('/')
    
    # Check if this is a direct auth request (from login button)
    if request.GET.get('login') == 'true':
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=client_config, scopes=SCOPES)

        flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))
        print(f"Redirect URI: {flow.redirect_uri}")  # Debug line

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')

        return redirect(authorization_url)
    
    # Otherwise show login page
    return render(request, 'authenticate/login.html')


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

    email = r["email"]
    
    # Check database for authorization
    try:
        AuthorizedUser.objects.get(email=email)
        is_authorized = True
    except AuthorizedUser.DoesNotExist:
        # Fallback to constants file and team2073 check
        if email in AUTHORIZED_EMAIL or email.endswith('@team2073.com'):
            is_authorized = email in AUTHORIZED_EMAIL
        else:
            return render(request, 'authenticate/unauthorized.html', {'email': email})
    
    request.session["email"] = email
    request.session["is_authorized"] = is_authorized
    
    return redirect('/')


def logout(request):
    request.session.flush()
    return redirect('/auth/')


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}