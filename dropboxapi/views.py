# views.py
from django.shortcuts import render, redirect
from django.conf import settings
from .models import DropboxAccessTokens
from django.http import JsonResponse
import dropbox
import requests

# Redirect user to Dropbox authorization page
def dropbox_login(request):
    # Your Dropbox app credentials
    app_key = settings.DROPBOX_APP_KEY
    redirect_uri = settings.DROPBOX_REDIRECT_URI

    # Dropbox authorization URL
    authorization_url = f'https://www.dropbox.com/oauth2/authorize?client_id={app_key}&response_type=code&redirect_uri={redirect_uri}'
    return redirect(authorization_url)

# Handle the Dropbox callback and exchange code for access token
def dropbox_callback(request):
    # Dropbox token URL
    token_url = 'https://api.dropboxapi.com/oauth2/token'
    app_key = settings.DROPBOX_APP_KEY
    app_secret = settings.DROPBOX_APP_SECRET
    redirect_uri = settings.DROPBOX_REDIRECT_URI

    # Get the authorization code from the callback URL
    code = request.GET.get('code')

    if not code:
        return redirect('error_page')  # Redirect to error page if no code exists

    # Exchange the authorization code for an access token
    data = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': app_key,
        'client_secret': app_secret,
        'redirect_uri': redirect_uri
    }

    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        access_token = response.json()['access_token']
        refresh_token = response.json().get('refresh_token')
        expires_in = response.json().get('expires_in')
        print(access_token)
        print(refresh_token)
        print(expires_in)
        user = request.user
        token, created = DropboxAccessTokens.objects.get_or_create(user=user)
        token.token = access_token
        token.refresh_token = refresh_token
        token.expires_in = expires_in
        token.save()

        # Save the access token and refresh token (store securely)
        # For simplicity, we're just passing them to the template
        return redirect('dropboxapi:dropbox_files')  # Redirect to the files page
    else:
        return redirect('error_page')  # Redirect to error page if something goes wrong

def list_files(request):
    user = request.user
    try:
        access_token = DropboxAccessTokens.objects.get(user=user).token
    except DropboxAccessTokens.DoesNotExist:
        access_token = None

    if not access_token:
        return JsonResponse({'error': 'User is not authenticated with Dropbox.'})

    dbx = dropbox.Dropbox(access_token)
    try:
        result = dbx.files_list_folder('/spend_analizer')
        files = [{'name': file.name, 'path': file.path_display} for file in result.entries]
        return JsonResponse({'files': files})
    except dropbox.exceptions.ApiError as e:
        return JsonResponse({'error': str(e)})
