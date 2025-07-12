from django.urls import path

from .views import *

app_name= "Quote"

urlpatterns = [
    path('',index,name='home'),
    path("save-quote/", save_quote, name="save_quote"),

    path('shoppingcart/',shoppingcart,name='shoppingcart'),
    path('service/',service,name='service'),
    path('payment/',payment,name='payment'),
    path('contact/',contact,name='contact'),
    path('test/',GetQuoteView.as_view(),name='test'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
]
