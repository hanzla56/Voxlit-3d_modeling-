import stripe
from django.conf import settings
from django.views import View
from django.shortcuts import redirect,render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.decorators import method_decorator

from .models import *
import requests
import json
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def index(request):
      return render(request,'Quote/index.html')


def homeMain(request):
      return render(request,'Quote/home.html')


@login_required

def shoppingcart(request):
      print(request.user)
      items = QuoteOrder.objects.filter(user=request.user)
      context = {
          'items':items      }
      return render(request,'Quote/shoppingcart.html',context)
  

def service(request):
    if request.method == 'POST':
        try:
            print(request.POST)

            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            project_title = request.POST.get("project_title")
            email = request.POST.get("email")
            phone = request.POST.get("phone_number")
            message = request.POST.get("message_textcrea")

            # Validate required fields
            if not all([first_name, email, message]):
                print('❌ Validation failed: missing required fields')
                return HttpResponse("⚠️ Please fill all required fields.", status=400)

            # Save to DB
            QuoteRequest.objects.create(
                first_name=first_name,
                last_name=last_name,
                project_title=project_title,
                email=email,
                phone_number=phone,
                project_description=message,
            )

            return HttpResponse(status=200)

        except Exception as e:
            print(e)
            return HttpResponse("❌ An unexpected error occurred. Please try again later.", status=500)

    else:
        return render(request, 'Quote/service.html')
  
def payment(request):
      return render(request,'Quote/payment.html')
  
  
  
def contact(request):
    if request.method == 'POST':
        print(request.POST)
        first_name = request.POST.get("full_name")
        subject = request.POST.get("subject")
        email = request.POST.get("email")
        phone = request.POST.get("phone_number")
        message = request.POST.get("message_textcrea")
        file_name = request.FILES.get("attachment")

        # Validate required fields
        if not all([first_name, subject, email, message]):
            print('something is missing')
            return HttpResponse("⚠️ Please fill all required fields.", status=400)

        # Save to DB
        contact = ContactUs.objects.create(
            first_name=first_name,
            Subject=subject,
            email=email,
            phone_number=phone,
            Message=message,
            contact_file=file_name
        )

        return HttpResponse(status=200)

    else:
        return render(request,'Quote/contactus.html')



class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = 'http://localhost:8000'
        try:
            data = json.loads(request.body)
            price = float(data.get('price', 0))  # fallback to 0 if not present
            amount_in_cents = int(price * 100)
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': amount_in_cents,  # $10.00
                            'product_data': {
                                'name':  '3D Print Order',
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',  # One-time payment
                success_url=YOUR_DOMAIN + '/payment/success/',
                cancel_url=YOUR_DOMAIN + '/payment/cancel/',
            )
            print(checkout_session.id)
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})

@login_required
def save_quote(request):
    if request.method == "POST":
        print('enter into view')
        try:
            # data = json.loads(request.body)
            data = request.POST
            files = request.FILES
            
            print(f'the data is {data}=======')
            
            order = QuoteOrder.objects.create(
                model_file=files.get('model_file'),  # ✅ store file
                material=data["material"],
                unit=data["unit"],
                num_pieces=data.get("num_pieces"),
                price=data.get("price"),
                color=data.get("color"),
                customer_email=data.get("email"),  # optional
                status="PENDING"
            )

            return JsonResponse({"success": True, "order_id": order.id})

        except Exception as e:
            print(f'the error {e}')
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid method"}, status=405)


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
            print(f'the file is {file}')
            # file = 'test.stl'
            if not file:
                return JsonResponse({'error': 'No file uploaded'}, status=400)

            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file.name)
            mime_type = mime_type or 'application/octet-stream'
            print(f'the meme type ====================== {mime_type}')

            # Load other parameters
            json_payload = json.loads(request.POST.get('json_payload'))
            print(f'print the json {json_payload}')

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
            print(f'the error is {e}')
            return JsonResponse({'error': str(e)}, status=500)
      
    def get(self,request):
          return render(request,'Quote/test.html')
