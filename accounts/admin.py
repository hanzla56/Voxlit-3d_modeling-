from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser
from django.utils.translation import gettext_lazy as _


# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = MyUser

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("email", "username", "is_staff", "is_active")
    search_fields = ("email", "username")
    ordering = ("email",)
    
        # Use Django’s password hashing method
    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password') and not change:
            obj.set_password(form.cleaned_data['password'])  # Hash the password
            print('password change')
        super().save_model(request, obj, form, change)

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    
    
admin.site.register(MyUser,CustomUserAdmin)