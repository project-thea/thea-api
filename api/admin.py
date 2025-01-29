from django.contrib import admin
from .models import (
    Subject, 
    Test, 
    Disease, 
    Result, Location)

class TestAdmin(admin.ModelAdmin):
    list_display = ('disease_id', 'subject')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'subject', 
                'disease_id', 
            )}
        ),
    )

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

class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'latitude', 'longitude', 'subject')
    
    add_fieldsets = (
        (None, {
            # 'classes': ('wide',),
            'fields': (
                'subject', 
                'latitude',
                'longitude'
            )}
        ),
    )

    readonly_fields = ('created_at', 'modified_at')

admin.site.register(Test, TestAdmin)
admin.site.register(Disease, DiseaseAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Location, LocationAdmin)