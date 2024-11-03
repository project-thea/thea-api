from django.contrib import admin
from .models import Subject, Test, Disease, Result

class SubjectAdmin(admin.ModelAdmin):
    # control which columns appear in the list view
    list_display = ('email', 'name', 'name')
    
    # Fields for when adding a user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name', 
                'email', 
                'password', 
            )}
        ),
    )
    
    # Fields for editing existing users, grouped in fieldsets
    # fieldsets = (
    #     (None, {'fields': ('email', 'password')}),
    #     ('Personal info', {'fields': ('name',)}),
    #     ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    #     ('Important dates', {'fields': ('last_login', 'date_joined')}),
    # )
    
    # Fields you can search by
    search_fields = ('email', 'name')
    
    # Fields you can use to order the user list
    ordering = ('email', 'name')

    readonly_fields = ('date_archived', 'date_deleted', 'created_at', 'modified_at')

class TestAdmin(admin.ModelAdmin):
    # control which columns appear in the list view
    list_display = ('disease_id', 'subject')
    
    # Fields for when adding a user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'subject', 
                'disease_id', 
            )}
        ),
    )
    
    # Fields for editing existing users, grouped in fieldsets
    # fieldsets = (
    #     (None, {'fields': ('email', 'password')}),
    #     ('Personal info', {'fields': ('name',)}),
    #     ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    #     ('Important dates', {'fields': ('last_login', 'date_joined')}),
    # )

    readonly_fields = ('created_at', 'modified_at')


class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name', 
            )}
        ),
    )
    
    readonly_fields = ('created_at', 'modified_at')

class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_id', 'result_status', 'subject', 'test_center')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'test_id', 
                'result_status',
                'subject',
                'test_center'
            )}
        ),
    )
    
    readonly_fields = ('created_at', 'modified_at')
    

admin.site.register(Subject, SubjectAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Disease, DiseaseAdmin)
admin.site.register(Result, ResultAdmin)