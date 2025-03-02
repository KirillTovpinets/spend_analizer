
from .models import DropboxAccessTokens, DropboxReceipt
from django.http import JsonResponse
import dropbox
from django.shortcuts import render
from django.conf import settings
import urllib.parse
from django.db.models import Q


def list_receipts(request):
  user = request.user
  try:
      access_token = DropboxAccessTokens.objects.get(user=user).token
  except DropboxAccessTokens.DoesNotExist:
      access_token = None

  if not access_token:
      return JsonResponse({'error': 'User is not authenticated with Dropbox.'})


  try:
      dbx = dropbox.Dropbox(access_token)
      return fetch_files(dbx=dbx)
  except dropbox.exceptions.ApiError as e:
      return []

def fetch_files(dbx, path='/receipts/'):
    result = dbx.files_list_folder(path)
    files = []
    for entry in result.entries:
      existed = DropboxReceipt.objects.filter(Q(file_name=entry.name)|Q(file_name=entry.path_display)).exists()
      if existed:
         continue

      if(isinstance(entry, dropbox.files.FileMetadata)):
        files.append({'name': entry.name, 'path': entry.path_display})
      elif(isinstance(entry, dropbox.files.FolderMetadata)):
        files += fetch_files(dbx, entry.path_display)
    return files

def download_receipt(request, file_path):
  user = request.user

  access_token = DropboxAccessTokens.objects.get(user=user).token
  dbx = dropbox.Dropbox(access_token)

  metadata, response = dbx.files_download(file_path)

  return response.content
