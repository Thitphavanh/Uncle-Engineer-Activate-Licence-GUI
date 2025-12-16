from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import SoftwareName, License, ActivationLog


@admin.register(SoftwareName)
class SoftwareNameAdmin(admin.ModelAdmin):
    """Admin interface สำหรับ SoftwareName"""

    list_display = ["name", "is_active", "license_count", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    ordering = ["name"]

    def license_count(self, obj):
        """แสดงจำนวน License ของแต่ละซอฟต์แวร์"""
        count = obj.licenses.count()
        active_count = obj.licenses.filter(
            is_active=True, expires_at__gt=timezone.now()
        ).count()
        return format_html(
            '<span style="color: green;">{}</span> / {}', active_count, count
        )

    license_count.short_description = "Active / Total Licenses"


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    """Admin interface สำหรับ License"""

    list_display = [
        "license_key_short",
        "software",
        "customer_email",
        "status_badge",
        "activated_at",
        "expires_at",
        "days_remaining_display",
    ]
    list_filter = ["software", "is_active", "activated_at", "expires_at"]
    search_fields = ["license_key", "customer_email", "machine_id", "mac_address"]
    readonly_fields = [
        "license_key",
        "created_at",
        "updated_at",
        "is_expired_display",
        "days_remaining_display",
    ]
    fieldsets = (
        ("ข้อมูล License", {"fields": ("license_key", "software", "is_active")}),
        ("ข้อมูลลูกค้า", {"fields": ("customer_email", "machine_id", "mac_address")}),
        (
            "ระยะเวลา",
            {
                "fields": (
                    "duration_days",
                    "activated_at",
                    "expires_at",
                    "is_expired_display",
                    "days_remaining_display",
                )
            },
        ),
        (
            "ข้อมูลเพิ่มเติม",
            {"fields": ("notes", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    ordering = ["-created_at"]

    def license_key_short(self, obj):
        """แสดง License Key แบบสั้น"""
        return f"{obj.license_key[:8]}...{obj.license_key[-4:]}"

    license_key_short.short_description = "License Key"

    def status_badge(self, obj):
        """แสดงสถานะแบบมีสี"""
        if obj.is_expired():
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 8px; border-radius: 3px;">หมดอายุ</span>'
            )
        elif obj.days_remaining() <= 7:
            return format_html(
                '<span style="background-color: #ffc107; color: black; '
                'padding: 3px 8px; border-radius: 3px;">ใกล้หมดอายุ</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 8px; border-radius: 3px;">ใช้งานได้</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; '
                'padding: 3px 8px; border-radius: 3px;">ปิดใช้งาน</span>'
            )

    status_badge.short_description = "สถานะ"

    def is_expired_display(self, obj):
        """แสดงสถานะหมดอายุ"""
        if obj.is_expired():
            return format_html('<span style="color: red;">✗ หมดอายุแล้ว</span>')
        return format_html('<span style="color: green;">✓ ใช้งานได้</span>')

    is_expired_display.short_description = "สถานะการหมดอายุ"

    def days_remaining_display(self, obj):
        """แสดงจำนวนวันที่เหลือ"""
        days = obj.days_remaining()
        if days <= 0:
            return format_html('<span style="color: red;">หมดอายุแล้ว</span>')
        elif days <= 7:
            return format_html(
                '<span style="color: orange; font-weight: bold;">{} วัน</span>', days
            )
        else:
            return format_html('<span style="color: green;">{} วัน</span>', days)

    days_remaining_display.short_description = "เหลืออีก"

    actions = ["activate_licenses", "deactivate_licenses"]

    def activate_licenses(self, request, queryset):
        """Action สำหรับเปิดใช้งาน License"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"เปิดใช้งาน {updated} License สำเร็จ")

    activate_licenses.short_description = "เปิดใช้งาน License ที่เลือก"

    def deactivate_licenses(self, request, queryset):
        """Action สำหรับปิดใช้งาน License"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"ปิดใช้งาน {updated} License สำเร็จ")

    deactivate_licenses.short_description = "ปิดใช้งาน License ที่เลือก"


@admin.register(ActivationLog)
class ActivationLogAdmin(admin.ModelAdmin):
    """Admin interface สำหรับ ActivationLog"""

    list_display = [
        "created_at",
        "action",
        "license_info",
        "success_badge",
        "ip_address",
    ]
    list_filter = ["action", "success", "created_at"]
    search_fields = ["license__license_key", "license__customer_email", "ip_address"]
    readonly_fields = [
        "license",
        "action",
        "ip_address",
        "user_agent",
        "success",
        "error_message",
        "created_at",
    ]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        """ไม่อนุญาตให้เพิ่ม Log ด้วยตนเอง"""
        return False

    def has_change_permission(self, request, obj=None):
        """ไม่อนุญาตให้แก้ไข Log"""
        return False

    def license_info(self, obj):
        """แสดงข้อมูล License"""
        return f"{obj.license.software.name} - {obj.license.customer_email}"

    license_info.short_description = "License"

    def success_badge(self, obj):
        """แสดงสถานะความสำเร็จ"""
        if obj.success:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 8px; border-radius: 3px;">✓ สำเร็จ</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; '
            'padding: 3px 8px; border-radius: 3px;">✗ ล้มเหลว</span>'
        )

    success_badge.short_description = "ผลลัพธ์"


# Customize Admin Site
admin.site.site_header = "License Management System"
admin.site.site_title = "License Admin"
admin.site.index_title = "จัดการระบบ License"
