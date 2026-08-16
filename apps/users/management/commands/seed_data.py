"""
Management command: python manage.py seed_data
Seeds the database with all initial data required to run the portal.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding Kaflox Portal database...'))
        self._seed_users()
        self._seed_staff_roles()
        self._seed_stage_templates()
        self._seed_material_categories()
        self._seed_suppliers()
        self._seed_materials()
        self._seed_demo_project()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully.'))

    def _seed_users(self):
        self.stdout.write('  Creating users...')

        # Super Admin
        if not User.objects.filter(email='admin@kafloxengineering.com').exists():
            User.objects.create_superuser(
                email='admin@kafloxengineering.com',
                password='KafloxAdmin2025!',
                first_name='Kaflox',
                last_name='Admin',
                role=User.SUPER_ADMIN,
            )
            self.stdout.write('    Created super admin: admin@kafloxengineering.com / KafloxAdmin2025!')

        # Demo Client
        if not User.objects.filter(email='client@demo.com').exists():
            User.objects.create_user(
                email='client@demo.com',
                password='DemoClient2025!',
                first_name='Olumide',
                last_name='Adewale',
                role=User.CLIENT,
                country='United Kingdom',
                preferred_currency='GBP',
                phone='+44 7700 900000',
            )
            self.stdout.write('    Created demo client: client@demo.com / DemoClient2025!')

        # Demo Team Member
        if not User.objects.filter(email='supervisor@kafloxengineering.com').exists():
            User.objects.create_user(
                email='supervisor@kafloxengineering.com',
                password='Supervisor2025!',
                first_name='Adebayo',
                last_name='Osei',
                role=User.TEAM_MEMBER,
                phone='+234 801 000 0001',
            )
            self.stdout.write('    Created team member: supervisor@kafloxengineering.com / Supervisor2025!')

    def _seed_staff_roles(self):
        self.stdout.write('  Creating staff roles...')
        from apps.staff.models import StaffRole
        roles = [
            ('Project Manager', 0),
            ('Site Engineer', 1),
            ('Site Supervisor', 2),
            ('Quantity Surveyor', 3),
            ('Foreman', 4),
            ('Bricklayer / Mason', 5),
            ('Carpenter', 6),
            ('Electrician', 7),
            ('Plumber', 8),
            ('Painter', 9),
            ('Iron Bender / Steel Fixer', 10),
            ('Tiler', 11),
            ('Labourer', 12),
            ('Security / Watchman', 13),
            ('Driver', 14),
        ]
        for name, order in roles:
            StaffRole.objects.get_or_create(name=name, defaults={'order': order})
        self.stdout.write(f'    Created {len(roles)} staff roles.')

    def _seed_stage_templates(self):
        self.stdout.write('  Creating stage templates...')
        from apps.stages.models import StageTemplate
        templates = [
            # Residential stages
            ('Site Clearing and Setting Out', 'Clearing vegetation, pegging out boundaries and setting out the building footprint.', 'residential', 1),
            ('Foundation (Excavation, Concrete, Backfill)', 'Excavation to required depth, pouring concrete strip or pad foundations, and compacted backfill.', 'residential', 2),
            ('German Floor / Substructure', 'Construction of the ground floor slab including blinding, DPM, reinforcement and concrete pour.', 'residential', 3),
            ('Block Work to Lintel Level', 'Laying block walls from ground level up to lintel height.', 'residential', 4),
            ('Lintel and Ring Beam', 'Formwork, reinforcement and concrete pour for lintels and ring beam.', 'residential', 5),
            ('Block Work to Roof Level', 'Continuation of block walls from ring beam to roof plate level.', 'residential', 6),
            ('Roofing', 'Installation of roof trusses, purlins, roofing sheets and fascia boards.', 'residential', 7),
            ('Electrical and Plumbing First Fix', 'Concealed electrical conduit, wiring, and plumbing pipe runs before plastering.', 'residential', 8),
            ('Plastering', 'Internal and external wall plastering and rendering.', 'residential', 9),
            ('Electrical and Plumbing Second Fix', 'Installation of sockets, switches, fittings, sanitaryware and plumbing fixtures.', 'residential', 10),
            ('Screeding and Tiling', 'Floor screeding followed by tiling of all wet areas and floors.', 'residential', 11),
            ('Doors and Windows Installation', 'Supply and installation of all door frames, doors, window frames and glazing.', 'residential', 12),
            ('Painting and Finishing', 'Internal and external painting, touch-ups and all finishing works.', 'residential', 13),
            ('Handover', 'Final inspection, snag resolution, documentation and client handover.', 'residential', 14),
            # Commercial-only stages
            ('Structural Steel Works', 'Fabrication and erection of structural steel frame elements.', 'commercial', 15),
            ('False Ceiling Installation', 'Installation of suspended ceiling systems and grid work.', 'commercial', 16),
            ('Facade and Cladding', 'External facade treatment, cladding and glazed curtain wall systems.', 'commercial', 17),
            ('Landscaping and External Works', 'Paving, drainage, planting and all external site works.', 'commercial', 18),
        ]
        for name, desc, ptype, order in templates:
            StageTemplate.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'project_type': ptype, 'default_order': order}
            )
        self.stdout.write(f'    Created {len(templates)} stage templates.')

    def _seed_material_categories(self):
        self.stdout.write('  Creating material categories...')
        from apps.materials.models import MaterialCategory
        categories = [
            'Cement and Concrete', 'Steel and Iron', 'Roofing Materials',
            'Wood and Timber', 'Sand and Aggregates', 'Blocks and Bricks',
            'Electrical Materials', 'Plumbing Materials', 'Tiles and Flooring',
            'Paints and Finishes', 'Doors and Windows', 'General Hardware',
        ]
        for cat in categories:
            MaterialCategory.objects.get_or_create(name=cat)
        self.stdout.write(f'    Created {len(categories)} material categories.')

    def _seed_suppliers(self):
        self.stdout.write('  Creating suppliers...')
        from apps.materials.models import Supplier
        suppliers = [
            {
                'name': 'Lagos Cement Depot',
                'contact_person': 'Mr Adeyemi',
                'phone_primary': '+234 801 234 5678',
                'address': '14 Cement Road, Apapa',
                'city': 'Lagos',
                'state': 'Lagos',
            },
            {
                'name': 'Steelman Nigeria Ltd',
                'contact_person': 'Mrs Ojo',
                'phone_primary': '+234 802 345 6789',
                'address': '7 Iron Close, Oshodi',
                'city': 'Lagos',
                'state': 'Lagos',
            },
            {
                'name': 'Rooftech Supplies',
                'contact_person': 'Mr Bello',
                'phone_primary': '+234 803 456 7890',
                'address': '23 Roofing Avenue, Surulere',
                'city': 'Lagos',
                'state': 'Lagos',
            },
            {
                'name': 'Eko Timber Merchants',
                'contact_person': 'Chief Nwosu',
                'phone_primary': '+234 804 567 8901',
                'address': '5 Timber Lane, Ijora',
                'city': 'Lagos',
                'state': 'Lagos',
            },
            {
                'name': 'Lekki Sand Suppliers',
                'contact_person': 'Mr Okafor',
                'phone_primary': '+234 805 678 9012',
                'address': 'Lekki-Epe Expressway, Km 12',
                'city': 'Lagos',
                'state': 'Lagos',
            },
            {
                'name': 'Block World Nigeria',
                'contact_person': 'Mrs Ibrahim',
                'phone_primary': '+234 807 890 1234',
                'address': '18 Block Factory Road, Ikorodu',
                'city': 'Lagos',
                'state': 'Lagos',
            },
        ]
        for s in suppliers:
            Supplier.objects.get_or_create(name=s['name'], defaults=s)
        self.stdout.write(f'    Created {len(suppliers)} suppliers.')

    def _seed_materials(self):
        self.stdout.write('  Creating materials and prices...')
        from apps.materials.models import Material, MaterialCategory, MaterialPrice, Supplier
        from django.contrib.auth import get_user_model
        import datetime
        User = get_user_model()
        admin = User.objects.filter(role='super_admin').first()
        today = datetime.date.today()

        cat_cement = MaterialCategory.objects.get(name='Cement and Concrete')
        cat_steel = MaterialCategory.objects.get(name='Steel and Iron')
        cat_roof = MaterialCategory.objects.get(name='Roofing Materials')
        cat_timber = MaterialCategory.objects.get(name='Wood and Timber')
        cat_sand = MaterialCategory.objects.get(name='Sand and Aggregates')
        cat_blocks = MaterialCategory.objects.get(name='Blocks and Bricks')

        sup_cement = Supplier.objects.get(name='Lagos Cement Depot')
        sup_steel = Supplier.objects.get(name='Steelman Nigeria Ltd')
        sup_roof = Supplier.objects.get(name='Rooftech Supplies')
        sup_timber = Supplier.objects.get(name='Eko Timber Merchants')
        sup_sand = Supplier.objects.get(name='Lekki Sand Suppliers')
        sup_block = Supplier.objects.get(name='Block World Nigeria')

        materials_data = [
            ('Dangote Cement 42.5', cat_cement, '50kg bag', sup_cement, Decimal('9500')),
            ('Iron Rod 12mm (Y12)', cat_steel, 'Per length', sup_steel, Decimal('8200')),
            ('Iron Rod 16mm (Y16)', cat_steel, 'Per length', sup_steel, Decimal('14500')),
            ('Roofing Sheet Long Span', cat_roof, 'Per metre', sup_roof, Decimal('4800')),
            ('Timber 2x3 inch', cat_timber, 'Per length', sup_timber, Decimal('2100')),
            ('Sand (Sharp)', cat_sand, 'Per tipper', sup_sand, Decimal('65000')),
            ('Granite 3/4 inch', cat_sand, 'Per tipper', sup_sand, Decimal('95000')),
            ('Hollow Blocks 9 inch', cat_blocks, 'Per unit', sup_block, Decimal('650')),
            ('Hollow Blocks 6 inch', cat_blocks, 'Per unit', sup_block, Decimal('450')),
        ]

        for name, category, unit, supplier, price in materials_data:
            mat, _ = Material.objects.get_or_create(name=name, defaults={'category': category, 'unit': unit})
            MaterialPrice.objects.get_or_create(
                material=mat, supplier=supplier, effective_date=today,
                defaults={'price': price, 'currency': 'NGN', 'is_active': True, 'updated_by': admin}
            )
        self.stdout.write(f'    Created {len(materials_data)} materials with prices.')

    def _seed_demo_project(self):
        self.stdout.write('  Creating demo project...')
        from apps.projects.models import Project
        from apps.stages.models import Stage, StageTemplate
        import datetime
        User = get_user_model()
        client = User.objects.filter(email='client@demo.com').first()
        if not client:
            return

        project, created = Project.objects.get_or_create(
            name='4-Bedroom Duplex – Lekki, Lagos',
            client=client,
            defaults={
                'description': 'Luxury 4-bedroom duplex with BQ on a 650sqm plot in Lekki Phase 1.',
                'project_type': Project.RESIDENTIAL,
                'status': Project.ACTIVE,
                'address': 'Plot 14, Admiralty Way',
                'city': 'Lekki',
                'state': 'Lagos',
                'contract_value': Decimal('85000000'),
                'currency': 'NGN',
                'start_date': datetime.date(2025, 1, 5),
                'estimated_end_date': datetime.date(2026, 8, 31),
            }
        )

        if created:
            templates = StageTemplate.objects.filter(
                project_type__in=['residential', 'both']
            ).order_by('default_order')
            stage_data = [
                (Stage.COMPLETED, datetime.date(2025, 1, 5), datetime.date(2025, 1, 15), Decimal('1200000'), Decimal('700000')),
                (Stage.COMPLETED, datetime.date(2025, 1, 20), datetime.date(2025, 2, 2), Decimal('4500000'), Decimal('1800000')),
                (Stage.COMPLETED, datetime.date(2025, 2, 5), datetime.date(2025, 2, 18), Decimal('2000000'), Decimal('900000')),
                (Stage.COMPLETED, datetime.date(2025, 2, 20), datetime.date(2025, 3, 10), Decimal('3200000'), Decimal('1500000')),
                (Stage.COMPLETED, datetime.date(2025, 3, 12), datetime.date(2025, 3, 25), Decimal('2800000'), Decimal('1000000')),
                (Stage.COMPLETED, datetime.date(2025, 4, 1), datetime.date(2025, 7, 15), Decimal('4000000'), Decimal('1500000')),
                (Stage.IN_PROGRESS, datetime.date(2025, 7, 18), None, Decimal('2800000'), Decimal('800000')),
                (Stage.AWAITING_PAYMENT, None, None, Decimal('2200000'), Decimal('1200000')),
                (Stage.PENDING, None, None, Decimal('3500000'), Decimal('1200000')),
                (Stage.PENDING, None, None, Decimal('1800000'), Decimal('800000')),
                (Stage.PENDING, None, None, Decimal('4800000'), Decimal('1800000')),
                (Stage.PENDING, None, None, Decimal('5500000'), Decimal('2000000')),
                (Stage.PENDING, None, None, Decimal('4000000'), Decimal('1500000')),
                (Stage.PENDING, None, None, Decimal('0'), Decimal('0')),
            ]
            for i, (tmpl, data) in enumerate(zip(templates, stage_data)):
                status, actual_start, actual_end, mat_cost, lab_cost = data
                Stage.objects.create(
                    project=project,
                    template=tmpl,
                    name=tmpl.name,
                    description=tmpl.description,
                    order=i + 1,
                    status=status,
                    actual_start=actual_start,
                    actual_end=actual_end,
                    material_cost=mat_cost,
                    labour_cost=lab_cost,
                )
            self.stdout.write('    Created demo project with 14 stages.')
        else:
            self.stdout.write('    Demo project already exists, skipped.')
