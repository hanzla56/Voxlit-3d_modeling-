from django.db import models

class QuoteOrder(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    ]

    customer_email = models.EmailField(null=True, blank=True)
    material = models.CharField(max_length=50)
    unit = models.CharField(max_length=10)
    num_pieces = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    stripe_session_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PAID')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status} - ${self.price}"
