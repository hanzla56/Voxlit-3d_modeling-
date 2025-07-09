import stripe
from django.conf import settings
from django.views import View
from django.shortcuts import redirect,render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.decorators import method_decorator


import requests
import json
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder


stripe.api_key = settings.STRIPE_SECRET_KEY

def index(request):
      return render(request,'Quote/full.html')
  
  
def payment(request):
      return render(request,'Quote/payment.html')

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = 'http://localhost:8000'
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': 1000,  # $10.00
                            'product_data': {
                                'name': 'T-shirt',
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',  # One-time payment
                success_url=YOUR_DOMAIN + '/payment/success/',
                cancel_url=YOUR_DOMAIN + '/payment/cancel/',
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})

        # Prevent duplicate saves
        if not QuoteOrder.objects.filter(stripe_session_id=session['id']).exists():
            QuoteOrder.objects.create(
                stripe_session_id=session['id'],
                customer_email=session.get('customer_email'),
                material=metadata.get('material'),
                unit=metadata.get('unit'),
                num_pieces=int(metadata.get('num_pieces')),
                price=float(metadata.get('price')),
                status='PAID'
            )

    return HttpResponse(status=200)


class PaymentSuccessView(View):
    def get(self, request):
        return JsonResponse({"message": "Payment was successful!"})

class PaymentCancelView(View):
    def get(self, request):
        return JsonResponse({"message": "Payment was cancelled!"})

@method_decorator(csrf_exempt, name='dispatch')  # Exempt CSRF for POST (testing only)
class GetQuoteView(View):
    def post(self, request):
        try:
            # Get uploaded file
            print(f'entering into view {request.POST}')
            file = request.FILES.get('file_upload')
            if not file:
                return JsonResponse({'error': 'No file uploaded'}, status=400)

            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file.name)
            mime_type = mime_type or 'application/octet-stream'
            print(f'the meme type ====================== {mime_type}')

            # Load other parameters
            json_payload = json.loads(request.POST.get('json_payload'))

            # Prepare request to pricing API
            m = MultipartEncoder(
                fields={
                    'json_payload': json.dumps(json_payload),
                    'file_upload': (file.name, file.read(), mime_type)
                }
            )
            
            print(f'the data is {m}')

            headers = {
                'Content-Type': m.content_type,
                'User-Agent': 'QuoteClient/1.0'
            }

            estimate_url = "http://31.97.55.253:7898/estimate"
            res = requests.post(estimate_url, data=m, headers=headers)

            if res.status_code != 200:
                print('api faild ------')
                return JsonResponse({'error': 'Estimate API failed', 'details': res.text}, status=400)

            estimate_data = res.json()
            print(f'the estimated data is {estimate_data}')
            price = float(estimate_data['printing_cost'])

            return JsonResponse({'price': price})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
      
    def get(self,request):
          return render(request,'Quote/test.html')
