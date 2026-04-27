from django.core.management.base import BaseCommand
from organisation.models import TeamType


class Command(BaseCommand):
    help = 'Seeds TeamType colour labels for the organisation map legend'

    def handle(self, *args, **options):
        if TeamType.objects.exists():
            self.stdout.write(self.style.WARNING('TeamTypes already exist — skipping.'))
            return

        types = [
            ('Backend',  '#116B98'), # Dark Blue
            ('Frontend', '#1CB3FE'), # Light Blue
            ('Mobile',   '#0a8a3a'), # Green
            ('Data',     '#9b59b6'), # Purple
            ('DevOps',   '#e67e22'), # Orange
            ('QA/Ops',   '#27ae60'), # Dark Green
            ('Core',     '#d35400'), # Rust/Brown
            ('Security', '#f1c40f'), # Yellow
            ('Arch',     '#1abc9c'), # Teal
            ('Programme','#e74c3c'), # Red/Pink
        ]
        for name, color in types:
            TeamType.objects.create(name=name, color=color)

        self.stdout.write(self.style.SUCCESS(f'Created {len(types)} TeamTypes.'))
