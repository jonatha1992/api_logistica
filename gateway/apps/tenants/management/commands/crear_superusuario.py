import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea el superusuario inicial si no existe ninguno. Lee DJANGO_SUPERUSER_EMAIL y DJANGO_SUPERUSER_PASSWORD.'

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Superusuario ya existe. No se crea uno nuevo.')
            return

        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not email or not password:
            self.stderr.write(
                'Variables DJANGO_SUPERUSER_EMAIL y DJANGO_SUPERUSER_PASSWORD no configuradas. '
                'El superusuario no fue creado.'
            )
            return

        username = email.split('@')[0]
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superusuario creado: {email}'))
