from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from .models import SoftwareName, License, ActivationLog
from .serializers import (
    SoftwareNameSerializer,
    LicenseSerializer,
    ActivateLicenseSerializer,
    ValidateLicenseSerializer,
    RenewLicenseSerializer,
    ActivationLogSerializer,
)
from .permissions import HasStaticAPIKey


def get_client_ip(request):
    """ดึง IP Address จาก request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class SoftwareNameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet สำหรับดึงข้อมูลซอฟต์แวร์
    GET /api/software/ - ดึงรายการซอฟต์แวร์ทั้งหมด
    GET /api/software/{id}/ - ดึงข้อมูลซอฟต์แวร์เฉพาะ
    """

    queryset = SoftwareName.objects.filter(is_active=True)
    serializer_class = SoftwareNameSerializer
    permission_classes = [HasStaticAPIKey]


class LicenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet สำหรับจัดการ License
    """

    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    permission_classes = [HasStaticAPIKey]

    def get_queryset(self):
        """กรอง License ตาม query parameters"""
        queryset = super().get_queryset()

        # กรองตาม software_id
        software_id = self.request.query_params.get("software_id")
        if software_id:
            queryset = queryset.filter(software_id=software_id)

        # กรองตาม email
        email = self.request.query_params.get("email")
        if email:
            queryset = queryset.filter(customer_email=email)

        # กรองเฉพาะที่ยังใช้งานได้
        active_only = self.request.query_params.get("active_only")
        if active_only == "true":
            queryset = queryset.filter(is_active=True, expires_at__gt=timezone.now())

        return queryset

    @action(detail=False, methods=["post"], permission_classes=[HasStaticAPIKey])
    def activate(self, request):
        """
        API สำหรับ Activate License
        POST /api/licenses/activate/
        Body: {
            "software_id": 1,
            "customer_email": "user@example.com",
            "machine_id": "MACHINE-123-456",
            "mac_address": "00:1B:63:84:45:E6",
            "duration_days": 360
        }
        """
        serializer = ActivateLicenseSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "ข้อมูลไม่ถูกต้อง",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                # ตรวจสอบว่ามี License สำหรับเครื่องนี้อยู่แล้วหรือไม่
                existing_license = License.objects.filter(
                    machine_id=serializer.validated_data["machine_id"],
                    mac_address=serializer.validated_data["mac_address"],
                    software_id=serializer.validated_data["software_id"],
                ).first()

                if existing_license:
                    # ถ้ามี License อยู่แล้ว ให้อัพเดทข้อมูล
                    existing_license.customer_email = serializer.validated_data[
                        "customer_email"
                    ]
                    existing_license.duration_days = serializer.validated_data[
                        "duration_days"
                    ]
                    existing_license.activated_at = timezone.now()
                    existing_license.expires_at = timezone.now() + timezone.timedelta(
                        days=serializer.validated_data["duration_days"]
                    )
                    existing_license.is_active = True
                    existing_license.save()
                    license = existing_license
                    action_type = "renew"
                else:
                    # สร้าง License ใหม่
                    license = serializer.save()
                    action_type = "activate"

                # บันทึก Log
                ActivationLog.objects.create(
                    license=license,
                    action=action_type,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    success=True,
                )

                return Response(
                    {
                        "success": True,
                        "message": "Activate สำเร็จ",
                        "data": {
                            "license_key": license.license_key,
                            "software_name": license.software.name,
                            "customer_email": license.customer_email,
                            "activated_at": license.activated_at,
                            "expires_at": license.expires_at,
                            "duration_days": license.duration_days,
                            "days_remaining": license.days_remaining(),
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            # บันทึก Log แบบ error
            if "license" in locals():
                ActivationLog.objects.create(
                    license=license,
                    action="activate",
                    ip_address=get_client_ip(request),
                    success=False,
                    error_message=str(e),
                )

            return Response(
                {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], permission_classes=[HasStaticAPIKey])
    def validate(self, request):
        """
        API สำหรับ Validate License
        POST /api/licenses/validate/
        Body: {
            "machine_id": "MACHINE-123-456",
            "mac_address": "00:1B:63:84:45:E6",
            "software_name": "Software A"
        }
        """
        serializer = ValidateLicenseSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "valid": False,
                    "message": "ข้อมูลไม่ถูกต้อง",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        machine_id = serializer.validated_data["machine_id"]
        mac_address = serializer.validated_data["mac_address"]
        software_name = serializer.validated_data["software_name"]

        try:
            # ค้นหา License
            license = License.objects.select_related("software").get(
                machine_id=machine_id,
                mac_address=mac_address,
                software__name=software_name,
                is_active=True,
            )

            # ตรวจสอบว่าหมดอายุหรือไม่
            is_valid = not license.is_expired()

            # บันทึก Log
            ActivationLog.objects.create(
                license=license,
                action="validate",
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                success=is_valid,
            )

            if is_valid:
                return Response(
                    {
                        "success": True,
                        "valid": True,
                        "message": "License ใช้งานได้",
                        "data": {
                            "software_name": license.software.name,
                            "customer_email": license.customer_email,
                            "expires_at": license.expires_at,
                            "days_remaining": license.days_remaining(),
                        },
                    }
                )
            else:
                return Response(
                    {
                        "success": True,
                        "valid": False,
                        "message": "License หมดอายุแล้ว",
                        "data": {"expires_at": license.expires_at},
                    }
                )

        except License.DoesNotExist:
            return Response(
                {
                    "success": True,
                    "valid": False,
                    "message": "ไม่พบ License หรือ License ไม่ถูกต้อง",
                }
            )
        except Exception as e:
            return Response(
                {"success": False, "valid": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], permission_classes=[HasStaticAPIKey])
    def renew(self, request):
        """
        API สำหรับต่ออายุ License
        POST /api/licenses/renew/
        Body: {
            "machine_id": "MACHINE-123-456",
            "mac_address": "00:1B:63:84:45:E6",
            "software_id": 1,
            "duration_days": 360
        }
        """
        serializer = RenewLicenseSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "ข้อมูลไม่ถูกต้อง",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                license = serializer.save()

                # บันทึก Log
                ActivationLog.objects.create(
                    license=license,
                    action="renew",
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    success=True,
                )

                return Response(
                    {
                        "success": True,
                        "message": "ต่ออายุ License สำเร็จ",
                        "data": {
                            "software_name": license.software.name,
                            "expires_at": license.expires_at,
                            "days_remaining": license.days_remaining(),
                        },
                    }
                )

        except Exception as e:
            return Response(
                {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ActivationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet สำหรับดู Log การ Activate
    GET /api/logs/ - ดูรายการ Log ทั้งหมด
    """

    queryset = ActivationLog.objects.all()
    serializer_class = ActivationLogSerializer
    permission_classes = [HasStaticAPIKey]

    def get_queryset(self):
        """กรอง Log ตาม query parameters"""
        queryset = super().get_queryset()

        # กรองตาม license_id
        license_id = self.request.query_params.get("license_id")
        if license_id:
            queryset = queryset.filter(license_id=license_id)

        # กรองตาม action
        action = self.request.query_params.get("action")
        if action:
            queryset = queryset.filter(action=action)

        return queryset


@csrf_protect
@never_cache
def login_view(request):
    """
    Custom login view with Thai messages
    """
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Set session expiry based on remember me checkbox
            if not remember:
                # Session expires when browser closes
                request.session.set_expiry(0)
            else:
                # Session lasts for 2 weeks
                request.session.set_expiry(1209600)

            messages.success(request, 'เข้าสู่ระบบสำเร็จ')

            # Redirect to next page or dashboard
            next_page = request.GET.get('next', 'dashboard')
            return redirect(next_page)
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')

    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    """
    Logout view
    """
    logout(request)
    messages.success(request, 'ออกจากระบบสำเร็จ')
    return redirect('login')


@login_required
def index_view(request):
    """
    Index/Home view - redirects to dashboard
    """
    return redirect('dashboard')
