import dropbox
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse

def authorize(request):
    dbx = dropbox.DropboxOAuth2FlowNoRedirect(settings.DROPBOX_APP_KEY, settings.DROPBOX_APP_SECRET)
    auth_url = dbx.start()
    return redirect(auth_url)

def callback(request):
    dbx = dropbox.DropboxOAuth2FlowNoRedirect(settings.DROPBOX_APP_KEY, settings.DROPBOX_APP_SECRET)
    auth_code = request.GET.get('code')
    access_token, user_id = dbx.finish(auth_code)
    # Store the access token (in the database or session)
    request.session['dropbox_access_token'] = access_token
    return JsonResponse({'message': 'Dropbox authorization successful.'})

def list_files(request):
    access_token = request.session.get('dropbox_access_token')
    if not access_token:
        return JsonResponse({'error': 'User is not authenticated with Dropbox.'})

    dbx = dropbox.Dropbox(access_token)
    try:
        result = dbx.files_list_folder('')
        files = [{'name': file.name, 'path': file.path_display} for file in result.entries]
        return JsonResponse({'files': files})
    except dropbox.exceptions.ApiError as e:
        return JsonResponse({'error': str(e)})
