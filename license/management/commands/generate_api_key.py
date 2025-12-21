from django.core.management.base import BaseCommand
import secrets


class Command(BaseCommand):
    help = 'Generate a strong random API key for production use'

    def add_arguments(self, parser):
        parser.add_argument(
            '--length',
            type=int,
            default=32,
            help='Length of the API key in bytes (default: 32)'
        )

    def handle(self, *args, **options):
        length = options['length']

        # Generate a cryptographically strong random key
        api_key = secrets.token_hex(length)

        self.stdout.write(self.style.SUCCESS('\n=== API KEY GENERATED ==='))
        self.stdout.write(f'\nKey Length: {length * 2} characters')
        self.stdout.write(self.style.SUCCESS(f'\nAPI Key: {api_key}'))

        self.stdout.write(self.style.WARNING('\n\n=== SETUP INSTRUCTIONS ==='))
        self.stdout.write('\n1. Add to your .env file:')
        self.stdout.write(f'   API_TOKEN={api_key}')

        self.stdout.write('\n\n2. Update views.py to use HasStaticAPIKey:')
        self.stdout.write('   from .permissions import HasStaticAPIKey')
        self.stdout.write('   permission_classes = [HasStaticAPIKey]')

        self.stdout.write('\n\n3. Restart your server:')
        self.stdout.write('   docker-compose restart backend')

        self.stdout.write(self.style.WARNING('\n\n=== CLIENT USAGE ==='))
        self.stdout.write('\nPython:')
        self.stdout.write(f'   headers = {{"X-API-TOKEN": "{api_key}"}}')
        self.stdout.write('   requests.get("https://api.yourdomain.com/api/software/", headers=headers)')

        self.stdout.write('\ncURL:')
        self.stdout.write(f'   curl -H "X-API-TOKEN: {api_key}" https://api.yourdomain.com/api/software/')

        self.stdout.write(self.style.ERROR('\n\n⚠️  SECURITY WARNING:'))
        self.stdout.write('   - Keep this key SECRET!')
        self.stdout.write('   - Never commit .env to version control')
        self.stdout.write('   - Use HTTPS in production')
        self.stdout.write('   - Rotate keys every 6-12 months\n')
