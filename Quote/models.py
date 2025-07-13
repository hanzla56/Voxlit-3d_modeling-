from django.db import models
from accounts.models import MyUser

class QuoteOrder(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PENDING', 'PENDING'),
    ]
    user = models.ForeignKey("accounts.MyUser", on_delete=models.CASCADE,null=True,blank=True)
    model_file = models.FileField(upload_to='models/',null=True, blank=True)  # ✅ Saves file path
    customer_email = models.EmailField(null=True, blank=True)
    material = models.CharField(max_length=50)
    unit = models.CharField(max_length=10)
    num_pieces = models.PositiveIntegerField()
    print_quality = models.CharField(max_length=30,null=True, blank=True)  # ✅ new field
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=30,null=True, blank=True)  # ✅ new field
    density = models.CharField(max_length=30,null=True, blank=True)  # ✅ new field



    stripe_session_id = models.CharField(max_length=255,null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PAID')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status} - ${self.price}"

class QuoteRequest(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # Project Details
    project_title = models.CharField(max_length=255)
    project_description = models.TextField()

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.project_title}"
    

class ContactUs(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=100)
    Subject = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # Project Details
    Message = models.TextField()
    contact_file = models.FileField(upload_to='contact/',null=True, blank=True)  # ✅ Saves file path


    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} - {self.Subject}"
    

class NewsletterList(models.Model):
      email = models.EmailField(unique=True)
      
      def clean(self):
        if NewsletterList.objects.exclude(pk=self.pk).filter(email__iexact=self.email).exists():
            raise ValidationError({'email': "This email is already subscribed."})

      def __str__(self):
        return self.email
    
    
class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question