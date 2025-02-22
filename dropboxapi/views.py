# views.py
from django.shortcuts import render, redirect
from django.conf import settings
from .models import DropboxAccessTokens, DropboxReceipt
from django.http import JsonResponse
from .utils import list_receipts, download_receipt
from .forms import DropboxReceiptForm
import requests
from PIL import Image
from io import BytesIO
import pytesseract
from expenses.utils import parse_receipt, format_to_iso
import json
import base64
from expenses.models import Expense, ExpenseItem
# Redirect user to Dropbox authorization page
def dropbox_login(request):
    user = request.user
    try:
        DropboxAccessTokens.objects.get(user=user)
        return redirect('dropboxapi:dropbox_files')
    except DropboxAccessTokens.DoesNotExist:
        pass
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
  files = list_receipts(request)
  if(request.method == 'POST'):
    form = DropboxReceiptForm(request.POST, files=files)

    if form.is_valid():
      receipt = form.save()

      file_name = form.cleaned_data['file_name']
      file_content = download_receipt(request, file_name)

      image = Image.open(BytesIO(file_content))

      buffer = BytesIO()
      image.save(buffer, format='JPEG')
      image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

      text = pytesseract.image_to_string(image)

      data = parse_receipt(text)
      total = data['total'] if data['total'] else 0
      date = data['date'] if data['date'] else ''
      merchant = data['merchant'] if data['merchant'] else ''

      return render(request, 'expenses/upload.html', {
        'records': data['items'],
        'expense': {
          'merchant': merchant,
          'post_date': format_to_iso(date),
          'category': 'Supermarkets'
        },
        'receipts': [{'name': file_name, 'path': '/receipts/' + file_name, 'id': receipt.id, 'image': image_base64}],
        'total': total,
        'is_dropbox': True
      })
  else:
    form = DropboxReceiptForm(files=files)
  return render(request, 'dropboxapi/dropbox_files.html', {'form': form})


def remove_receipt(request, receipt_id):
  receipt = DropboxReceipt.objects.get(id=receipt_id)
  receipt.delete()
  return JsonResponse({'message': 'Receipt removed successfully!'}, status=200)


def link_receipt(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    receipts = DropboxReceipt.objects.filter(id__in=data['receipt_ids'])
    merchant = data['merchant']
    formatted_date = data['post_date']
    expense, created = Expense.objects.update_or_create(
      amount=data['total'],
      transaction_date=data['post_date'],
      defaults={
          "category": data['category'],
          "amount": data['total'],
      }
    )

    if created:
      expense.merchant = merchant
      expense.transaction_date = formatted_date
      expense.post_date = formatted_date
      for receipt in receipts:
          expense.dropbox_receipts.add(receipt)
      expense.save()
    elif expense.dropbox_receipts.count() == 0:
      for receipt in receipts:
          expense.dropbox_receipts.add(receipt)
      expense.save()
    print(len(expense.dropbox_receipts.all()))


    ommit_items = ['total', 'amount', 'tax', 'subtotal', 'reg', 'SALES', 'CHANGE', 'are Di scover', 'Discover', 'scover', '5659', 'DISCOVER', 'BALANCE', '3 SUBTO1 AL']
    records = []
    for item in data['items']:
      omit = False
      for ommit_item in ommit_items:
          if ommit_item.lower() in item['description'].lower():
              omit = True
              break
      if omit:
          continue

      record = ExpenseItem.objects.create(
          description=item['description'],
          total=item['total'],
          price=item['price'],
          expense=expense
      )
      records.append(record)

    for receipt in receipts:
        receipt.expense = expense
        receipt.save()
    return JsonResponse({'message': 'Receipt linked successfully!'}, status=200)
