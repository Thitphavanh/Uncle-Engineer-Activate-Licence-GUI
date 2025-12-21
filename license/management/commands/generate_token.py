from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from license.utils import generate_api_token


class Command(BaseCommand):
    help = 'Generate API token for current hour'

    def handle(self, *args, **options):
        if not settings.API_TOKEN:
            self.stdout.write(
                self.style.ERROR('ERROR: API_TOKEN is not set in .env file!')
            )
            self.stdout.write(
                self.style.WARNING('Please set API_TOKEN in your .env file first.')
            )
            return

        now = timezone.now()
        token = generate_api_token(settings.API_TOKEN, now)

        # แสดงข้อมูล
        self.stdout.write(self.style.SUCCESS('\n=== API TOKEN GENERATED ==='))
        self.stdout.write(f'Current Time: {now.strftime("%Y-%m-%d %H:%M:%S %Z")}')
        self.stdout.write(f'Time Format: {now.strftime("%Y%m%d%H")}')
        self.stdout.write(self.style.SUCCESS(f'\nToken: {token}'))

        # แสดงตัวอย่างการใช้งาน
        self.stdout.write(self.style.WARNING('\n=== USAGE EXAMPLES ==='))
        self.stdout.write(f'\n1. Query Parameter:')
        self.stdout.write(f'   http://localhost:8000/api/software/?token={token}')
        self.stdout.write(f'\n2. Header:')
        self.stdout.write(f'   curl -H "X-API-TOKEN: {token}" http://localhost:8000/api/software/')

        self.stdout.write(self.style.WARNING(f'\n\nNote: This token is valid for current hour and will expire in the next hour.'))
