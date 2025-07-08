from django.urls import path

from .views import *

urlpatterns = [
    path('',payment,name='payment'),
    path('test/',GetQuoteView.as_view(),name='test'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
]
