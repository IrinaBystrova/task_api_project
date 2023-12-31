from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserChangeForm, CustomUserCreationForm
from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = CustomUser

    list_display = (
        'username',
        'email',
        'is_active',
        'is_staff',
        'is_superuser',
        'last_login',
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (
            'Permissions',
            {
                'fields': (
                    'is_staff',
                    'is_active',
                    'is_superuser',
                    # 'groups',
                    'user_permissions',
                )
            },
        ),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'is_staff',
                    'is_active',
                ),
            },
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

    @staticmethod
    def _is_my_obj(request, obj):
        if obj is not None and obj.created_by != request.user:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        return self._is_my_obj(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self._is_my_obj(request, obj)
