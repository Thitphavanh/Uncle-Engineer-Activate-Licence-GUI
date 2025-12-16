from rest_framework import serializers
from .models import SoftwareName, License, ActivationLog
from django.utils import timezone
from datetime import timedelta


class SoftwareNameSerializer(serializers.ModelSerializer):
    """Serializer สำหรับ SoftwareName"""

    class Meta:
        model = SoftwareName
        fields = ["id", "name", "description", "is_active"]


class LicenseSerializer(serializers.ModelSerializer):
    """Serializer สำหรับ License"""

    software_name = serializers.CharField(source="software.name", read_only=True)
    is_expired = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = License
        fields = [
            "id",
            "license_key",
            "software",
            "software_name",
            "customer_email",
            "machine_id",
            "mac_address",
            "duration_days",
            "activated_at",
            "expires_at",
            "is_active",
            "is_expired",
            "days_remaining",
            "created_at",
            "notes",
        ]
        read_only_fields = ["license_key", "created_at"]

    def get_is_expired(self, obj):
        return obj.is_expired()

    def get_days_remaining(self, obj):
        return obj.days_remaining()


class ActivateLicenseSerializer(serializers.Serializer):
    """Serializer สำหรับการ Activate License"""

    software_id = serializers.IntegerField(required=True)
    customer_email = serializers.EmailField(required=True)
    machine_id = serializers.CharField(required=True, max_length=255)
    mac_address = serializers.CharField(required=True, max_length=17)
    duration_days = serializers.IntegerField(required=True, min_value=1)

    def validate_software_id(self, value):
        """ตรวจสอบว่า Software ID มีอยู่จริงและ Active"""
        try:
            software = SoftwareName.objects.get(id=value, is_active=True)
        except SoftwareName.DoesNotExist:
            raise serializers.ValidationError("ไม่พบซอฟต์แวร์ที่ระบุหรือซอฟต์แวร์ถูกปิดการใช้งาน")
        return value

    def validate_mac_address(self, value):
        """ตรวจสอบรูปแบบ MAC Address"""
        import re

        # รูปแบบ MAC Address: XX:XX:XX:XX:XX:XX หรือ XX-XX-XX-XX-XX-XX
        pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        if not re.match(pattern, value):
            raise serializers.ValidationError("รูปแบบ MAC Address ไม่ถูกต้อง")
        return value

    def create(self, validated_data):
        """สร้าง License ใหม่"""
        software = SoftwareName.objects.get(id=validated_data["software_id"])

        # สร้าง License
        license = License.objects.create(
            software=software,
            customer_email=validated_data["customer_email"],
            machine_id=validated_data["machine_id"],
            mac_address=validated_data["mac_address"],
            duration_days=validated_data["duration_days"],
            activated_at=timezone.now(),
            is_active=True,
        )

        return license


class ValidateLicenseSerializer(serializers.Serializer):
    """Serializer สำหรับการ Validate License"""

    machine_id = serializers.CharField(required=True, max_length=255)
    mac_address = serializers.CharField(required=True, max_length=17)
    software_name = serializers.CharField(required=True, max_length=255)


class RenewLicenseSerializer(serializers.Serializer):
    """Serializer สำหรับการต่ออายุ License"""

    machine_id = serializers.CharField(required=True, max_length=255)
    mac_address = serializers.CharField(required=True, max_length=17)
    software_id = serializers.IntegerField(required=True)
    duration_days = serializers.IntegerField(required=True, min_value=1)

    def validate(self, data):
        """ตรวจสอบว่ามี License อยู่จริง"""
        try:
            license = License.objects.get(
                machine_id=data["machine_id"],
                mac_address=data["mac_address"],
                software_id=data["software_id"],
            )
            data["license"] = license
        except License.DoesNotExist:
            raise serializers.ValidationError("ไม่พบ License ที่ระบุ")
        return data

    def save(self):
        """ต่ออายุ License"""
        license = self.validated_data["license"]
        duration_days = self.validated_data["duration_days"]

        # ถ้า License หมดอายุแล้ว ให้เริ่มนับใหม่จากวันนี้
        if license.is_expired():
            license.activated_at = timezone.now()
            license.expires_at = timezone.now() + timedelta(days=duration_days)
        else:
            # ถ้ายังไม่หมดอายุ ให้ขยายเวลาต่อจากวันหมดอายุเดิม
            license.expires_at = license.expires_at + timedelta(days=duration_days)

        license.duration_days = duration_days
        license.is_active = True
        license.save()

        return license


class ActivationLogSerializer(serializers.ModelSerializer):
    """Serializer สำหรับ ActivationLog"""

    license_info = serializers.SerializerMethodField()

    class Meta:
        model = ActivationLog
        fields = [
            "id",
            "license",
            "license_info",
            "action",
            "ip_address",
            "success",
            "error_message",
            "created_at",
        ]

    def get_license_info(self, obj):
        return f"{obj.license.software.name} - {obj.license.customer_email}"
