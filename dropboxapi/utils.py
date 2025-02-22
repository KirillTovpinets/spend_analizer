
from .models import DropboxAccessTokens, DropboxReceipt
from django.http import JsonResponse
import dropbox
from django.shortcuts import render
from django.conf import settings


def list_receipts(request):
  user = request.user
  try:
      access_token = DropboxAccessTokens.objects.get(user=user).token
  except DropboxAccessTokens.DoesNotExist:
      access_token = None

  if not access_token:
      return JsonResponse({'error': 'User is not authenticated with Dropbox.'})

  dbx = dropbox.Dropbox(access_token)
  try:
      path = '/receipts/'
      result = dbx.files_list_folder(path)
      files = [{'name': file.name, 'path': file.path_display} for file in result.entries]
      return files
  except dropbox.exceptions.ApiError as e:
      return []


def download_receipt(request, file_path):
   user = request.user

   access_token = DropboxAccessTokens.objects.get(user=user).token
   dbx = dropbox.Dropbox(access_token)

   metadata, response = dbx.files_download('/receipts/' + file_path)

   return response.content
