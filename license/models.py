from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid
import secrets


class SoftwareName(models.Model):
    """Model สำหรับเก็บชื่อซอฟต์แวร์ที่มีในระบบ"""

    name = models.CharField(max_length=255, unique=True, verbose_name="ชื่อซอฟต์แวร์")
    description = models.TextField(blank=True, null=True, verbose_name="คำอธิบาย")
    is_active = models.BooleanField(default=True, verbose_name="ใช้งานอยู่")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สร้าง")

    class Meta:
        verbose_name = "Software Name"
        verbose_name_plural = "All Software"
        ordering = ["name"]

    def __str__(self):
        return self.name


class License(models.Model):
    """Model สำหรับเก็บข้อมูล License"""

    # ข้อมูลพื้นฐาน
    license_key = models.CharField(
        max_length=64, unique=True, default=uuid.uuid4, verbose_name="License Key"
    )
    software = models.ForeignKey(
        SoftwareName,
        on_delete=models.CASCADE,
        related_name="licenses",
        verbose_name="ซอฟต์แวร์",
    )

    # ข้อมูลลูกค้า
    customer_email = models.EmailField(verbose_name="อีเมล์ลูกค้า")

    # ข้อมูล Hardware
    machine_id = models.CharField(max_length=255, verbose_name="Machine ID")
    mac_address = models.CharField(max_length=17, verbose_name="MAC Address")

    # ข้อมูลระยะเวลา
    duration_days = models.IntegerField(verbose_name="ระยะเวลา (วัน)")
    activated_at = models.DateTimeField(
        default=timezone.now, verbose_name="วันที่ Activate"
    )
    expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name="วันหมดอายุ"
    )

    # สถานะ
    is_active = models.BooleanField(default=True, verbose_name="ใช้งานได้")

    # ข้อมูลเพิ่มเติม
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สร้าง")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="วันที่อัพเดท")
    notes = models.TextField(blank=True, null=True, verbose_name="หมายเหตุ")

    class Meta:
        verbose_name = "License"
        verbose_name_plural = "Licenses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["license_key"]),
            models.Index(fields=["machine_id", "mac_address"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        if self.expires_at:
            return f"{self.software.name} - {self.customer_email} (expires: {self.expires_at.date()})"
        return f"{self.software.name} - {self.customer_email}"

    def is_expired(self):
        """ตรวจสอบว่า License หมดอายุหรือไม่"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def days_remaining(self):
        """คำนวณจำนวนวันที่เหลือ"""
        if not self.expires_at:
            return 0
        if self.is_expired():
            return 0
        delta = self.expires_at - timezone.now()
        return delta.days

    def save(self, *args, **kwargs):
        """Override save เพื่อคำนวณวันหมดอายุอัตโนมัติ"""
        if not self.expires_at:
            self.expires_at = self.activated_at + timedelta(days=self.duration_days)
        super().save(*args, **kwargs)


class ActivationLog(models.Model):
    """Model สำหรับบันทึก Log การ Activate และ Validate"""

    ACTION_CHOICES = [
        ("activate", "Activate"),
        ("validate", "Validate"),
        ("renew", "Renew"),
        ("revoke", "Revoke"),
    ]

    license = models.ForeignKey(
        License, on_delete=models.CASCADE, related_name="logs", verbose_name="License"
    )
    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, verbose_name="การกระทำ"
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP Address"
    )
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    success = models.BooleanField(default=True, verbose_name="สำเร็จ")
    error_message = models.TextField(blank=True, null=True, verbose_name="ข้อความ Error")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่บันทึก")

    class Meta:
        verbose_name = "Activation Log"
        verbose_name_plural = "Activation Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} - {self.license.software.name} - {self.created_at}"
