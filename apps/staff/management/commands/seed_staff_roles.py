"""
Place this file at: apps/staff/management/commands/seed_staff_roles.py
(create the management/commands folders with empty __init__.py files if they
don't already exist)

Run once with:  python manage.py seed_staff_roles
Safe to re-run -- uses get_or_create, so it won't duplicate roles.
"""
from django.core.management.base import BaseCommand
from apps.staff.models import StaffRole

ROLES = [
    'Project Manager', 'Site Engineer', 'Site Supervisor', 'Quantity Surveyor',
    'Foreman', 'Bricklayer / Mason', 'Carpenter', 'Electrician', 'Plumber',
    'Painter', 'Iron Bender / Steel Fixer', 'Tiler', 'Labourer', 'Security / Watchman', 'Driver',
]


class Command(BaseCommand):
    help = 'Seed the standard construction staff roles (idempotent).'

    def handle(self, *args, **options):
        created = 0
        for order, name in enumerate(ROLES):
            role, was_created = StaffRole.objects.get_or_create(
                name=name,
                defaults={'order': order, 'is_active': True},
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created} new staff role(s) ({len(ROLES)} total in list).'
        ))