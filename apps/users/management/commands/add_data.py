from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from apps.projects.models import Project, EOISubmission
from apps.staff.models import (
    StaffRole,
    StaffMember,
    AttendanceRecord,
    MaterialIssuance,
    DeliveryLog,
)
from apps.materials.models import (
    Supplier,
    MaterialCategory,
    Material,
    MaterialPrice,
    CostAnomalyFlag,
)
from apps.stages.models import (
    StageTemplate,
    Stage,
    StageComment,
    SnagItem,
)
from apps.payments.models import Payment, RefundRequest
from apps.media.models import ProjectMedia
from apps.messaging.models import MessageThread, Message, Notification


User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with realistic development data"

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write("Starting database seeding...\n")

        # ============================================================
        # USERS
        # ============================================================

        self.stdout.write("Creating users...")

        admin, _ = User.objects.get_or_create(
            email="admin@kaflox.com",
            defaults={
                "first_name": "Daniel",
                "last_name": "Admin",
                "phone": "+2348010000001",
                "role": User.SUPER_ADMIN,
                "country": "Nigeria",
                "preferred_currency": "NGN",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if not admin.has_usable_password():
            admin.set_password("Admin123!")
            admin.save()

        project_manager, _ = User.objects.get_or_create(
            email="manager@kaflox.com",
            defaults={
                "first_name": "Michael",
                "last_name": "Okafor",
                "phone": "+2348010000002",
                "role": User.TEAM_MEMBER,
                "country": "Nigeria",
                "preferred_currency": "NGN",
                "is_staff": True,
            },
        )

        project_manager.set_password("Manager123!")
        project_manager.save()

        site_engineer, _ = User.objects.get_or_create(
            email="engineer@kaflox.com",
            defaults={
                "first_name": "David",
                "last_name": "Ibrahim",
                "phone": "+2348010000003",
                "role": User.TEAM_MEMBER,
                "country": "Nigeria",
                "preferred_currency": "NGN",
            },
        )

        site_engineer.set_password("Engineer123!")
        site_engineer.save()

        client1, _ = User.objects.get_or_create(
            email="john.adebayo@example.com",
            defaults={
                "first_name": "John",
                "last_name": "Adebayo",
                "phone": "+2348010000010",
                "role": User.CLIENT,
                "country": "Nigeria",
                "preferred_currency": "NGN",
            },
        )

        client1.set_password("Client123!")
        client1.save()

        client2, _ = User.objects.get_or_create(
            email="sarah.williams@example.com",
            defaults={
                "first_name": "Sarah",
                "last_name": "Williams",
                "phone": "+2348010000011",
                "role": User.CLIENT,
                "country": "Nigeria",
                "preferred_currency": "NGN",
            },
        )

        client2.set_password("Client123!")
        client2.save()

        client3, _ = User.objects.get_or_create(
            email="emeka.okoro@example.com",
            defaults={
                "first_name": "Emeka",
                "last_name": "Okoro",
                "phone": "+2348010000012",
                "role": User.CLIENT,
                "country": "Nigeria",
                "preferred_currency": "NGN",
            },
        )

        client3.set_password("Client123!")
        client3.save()

        prospect, _ = User.objects.get_or_create(
            email="prospect@example.com",
            defaults={
                "first_name": "James",
                "last_name": "Brown",
                "phone": "+2348010000015",
                "role": User.EOI_PROSPECT,
                "country": "Nigeria",
                "preferred_currency": "NGN",
            },
        )

        prospect.set_password("Prospect123!")
        prospect.save()

        # ============================================================
        # STAFF ROLES
        # ============================================================

        self.stdout.write("Creating staff roles...")

        roles = {}

        role_data = [
            (
                "Project Manager",
                "Responsible for overall project coordination.",
                1,
            ),
            (
                "Site Engineer",
                "Supervises construction activities on site.",
                2,
            ),
            (
                "Site Supervisor",
                "Coordinates daily site activities.",
                3,
            ),
            (
                "Quantity Surveyor",
                "Handles project costing and material quantities.",
                4,
            ),
            (
                "Electrician",
                "Electrical installation and maintenance.",
                5,
            ),
            (
                "Plumber",
                "Plumbing installation and maintenance.",
                6,
            ),
        ]

        for name, description, order in role_data:
            role, _ = StaffRole.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "order": order,
                    "is_active": True,
                },
            )

            roles[name] = role

        # ============================================================
        # STAFF
        # ============================================================

        self.stdout.write("Creating staff members...")

        staff1, _ = StaffMember.objects.get_or_create(
            staff_id="KE-001",
            defaults={
                "first_name": "Michael",
                "last_name": "Okafor",
                "phone": "+2348020000001",
                "role": roles["Project Manager"],
                "staff_type": StaffMember.DIRECT,
                "status": StaffMember.ACTIVE,
            },
        )

        staff2, _ = StaffMember.objects.get_or_create(
            staff_id="KE-002",
            defaults={
                "first_name": "David",
                "last_name": "Ibrahim",
                "phone": "+2348020000002",
                "role": roles["Site Engineer"],
                "staff_type": StaffMember.DIRECT,
                "status": StaffMember.ACTIVE,
            },
        )

        staff3, _ = StaffMember.objects.get_or_create(
            staff_id="KE-003",
            defaults={
                "first_name": "Samuel",
                "last_name": "Adekunle",
                "phone": "+2348020000003",
                "role": roles["Site Supervisor"],
                "staff_type": StaffMember.DIRECT,
                "status": StaffMember.ACTIVE,
            },
        )

        staff4, _ = StaffMember.objects.get_or_create(
            staff_id="KE-004",
            defaults={
                "first_name": "Chinedu",
                "last_name": "Nwosu",
                "phone": "+2348020000004",
                "role": roles["Quantity Surveyor"],
                "staff_type": StaffMember.DIRECT,
                "status": StaffMember.ACTIVE,
            },
        )

        staff5, _ = StaffMember.objects.get_or_create(
            staff_id="KE-005",
            defaults={
                "first_name": "Victor",
                "last_name": "Eze",
                "phone": "+2348020000005",
                "role": roles["Electrician"],
                "staff_type": StaffMember.SUBCONTRACTOR,
                "status": StaffMember.ACTIVE,
                "company_name": "VoltPro Electricals",
                "company_registration": "RC-987654",
            },
        )

        staff6, _ = StaffMember.objects.get_or_create(
            staff_id="KE-006",
            defaults={
                "first_name": "Ibrahim",
                "last_name": "Musa",
                "phone": "+2348020000006",
                "role": roles["Plumber"],
                "staff_type": StaffMember.SUBCONTRACTOR,
                "status": StaffMember.ACTIVE,
                "company_name": "FlowTech Plumbing",
                "company_registration": "RC-456789",
            },
        )

        staff_members = [staff1, staff2, staff3, staff4, staff5, staff6]

        # ============================================================
        # MATERIAL CATEGORIES
        # ============================================================

        self.stdout.write("Creating material categories...")

        categories = {}

        category_data = [
            (
                "Cement",
                "Cement and concrete-related materials.",
            ),
            (
                "Steel",
                "Reinforcement and structural steel materials.",
            ),
            (
                "Blocks",
                "Concrete blocks and masonry materials.",
            ),
            (
                "Sand",
                "Construction sand and aggregates.",
            ),
            (
                "Electrical",
                "Electrical installation materials.",
            ),
            (
                "Plumbing",
                "Plumbing pipes and accessories.",
            ),
            (
                "Finishing",
                "Materials used for finishing and decoration.",
            ),
        ]

        for name, description in category_data:
            category, _ = MaterialCategory.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )

            categories[name] = category

        # ============================================================
        # SUPPLIERS
        # ============================================================

        self.stdout.write("Creating suppliers...")

        supplier1, _ = Supplier.objects.get_or_create(
            name="BuildMart Nigeria",
            defaults={
                "contact_person": "Peter Johnson",
                "phone_primary": "+2348030000001",
                "email": "sales@buildmart.example.com",
                "address": "12 Industrial Estate Road",
                "city": "Lagos",
                "state": "Lagos",
                "country": "Nigeria",
                "is_active": True,
                "notes": "Major construction material supplier.",
            },
        )

        supplier2, _ = Supplier.objects.get_or_create(
            name="Prime Construction Supplies",
            defaults={
                "contact_person": "Grace Okeke",
                "phone_primary": "+2348030000002",
                "phone_secondary": "+2348030000003",
                "email": "orders@primeconstruction.example.com",
                "address": "45 Airport Road",
                "city": "Abuja",
                "state": "FCT",
                "country": "Nigeria",
                "is_active": True,
            },
        )

        supplier3, _ = Supplier.objects.get_or_create(
            name="MegaBuild Materials",
            defaults={
                "contact_person": "Tunde Bello",
                "phone_primary": "+2348030000004",
                "email": "info@megabuild.example.com",
                "address": "8 Warehouse Avenue",
                "city": "Abuja",
                "state": "FCT",
                "country": "Nigeria",
                "is_active": True,
            },
        )

        suppliers = [supplier1, supplier2, supplier3]

        # ============================================================
        # MATERIALS
        # ============================================================

        self.stdout.write("Creating materials...")

        material_data = [
            (
                "Dangote Cement",
                "Cement",
                "50kg bag",
            ),
            (
                "12mm Reinforcement Bar",
                "Steel",
                "per length",
            ),
            (
                "16mm Reinforcement Bar",
                "Steel",
                "per length",
            ),
            (
                "9-inch Concrete Block",
                "Blocks",
                "per piece",
            ),
            (
                "Sharp Sand",
                "Sand",
                "per tipper",
            ),
            (
                "Plaster Sand",
                "Sand",
                "per tipper",
            ),
            (
                "Electrical Cable 2.5mm",
                "Electrical",
                "per meter",
            ),
            (
                "PVC Pipe 25mm",
                "Plumbing",
                "per length",
            ),
            (
                "Ceramic Floor Tiles",
                "Finishing",
                "per sqm",
            ),
        ]

        materials = {}

        for name, category_name, unit in material_data:
            material, _ = Material.objects.get_or_create(
                name=name,
                defaults={
                    "category": categories[category_name],
                    "unit": unit,
                    "is_active": True,
                },
            )

            materials[name] = material

        # ============================================================
        # MATERIAL PRICES
        # ============================================================

        self.stdout.write("Creating material prices...")

        price_data = [
            ("Dangote Cement", supplier1, Decimal("10500.00")),
            ("Dangote Cement", supplier2, Decimal("10800.00")),
            ("12mm Reinforcement Bar", supplier1, Decimal("8500.00")),
            ("12mm Reinforcement Bar", supplier2, Decimal("8700.00")),
            ("16mm Reinforcement Bar", supplier1, Decimal("14500.00")),
            ("16mm Reinforcement Bar", supplier3, Decimal("14800.00")),
            ("9-inch Concrete Block", supplier2, Decimal("850.00")),
            ("9-inch Concrete Block", supplier3, Decimal("900.00")),
            ("Sharp Sand", supplier1, Decimal("180000.00")),
            ("Sharp Sand", supplier2, Decimal("175000.00")),
            ("Plaster Sand", supplier1, Decimal("160000.00")),
            ("Plaster Sand", supplier3, Decimal("165000.00")),
            ("Electrical Cable 2.5mm", supplier2, Decimal("950.00")),
            ("PVC Pipe 25mm", supplier2, Decimal("2500.00")),
            ("Ceramic Floor Tiles", supplier3, Decimal("12500.00")),
        ]

        for material_name, supplier, price in price_data:
            MaterialPrice.objects.get_or_create(
                material=materials[material_name],
                supplier=supplier,
                effective_date=date.today(),
                defaults={
                    "price": price,
                    "currency": "NGN",
                    "is_active": True,
                    "updated_by": admin,
                },
            )

        # ============================================================
        # STAGE TEMPLATES
        # ============================================================

        self.stdout.write("Creating stage templates...")

        templates = {}

        template_data = [
            (
                "Foundation",
                "Site preparation, excavation and foundation works.",
                StageTemplate.BOTH,
                1,
            ),
            (
                "Structural Frame",
                "Columns, beams and structural reinforcement.",
                StageTemplate.BOTH,
                2,
            ),
            (
                "Blockwork",
                "Masonry and internal partition construction.",
                StageTemplate.BOTH,
                3,
            ),
            (
                "Roofing",
                "Roof structure and roofing installation.",
                StageTemplate.RESIDENTIAL,
                4,
            ),
            (
                "Electrical & Plumbing",
                "Electrical and plumbing first-fix installation.",
                StageTemplate.BOTH,
                5,
            ),
            (
                "Finishing",
                "Flooring, painting, fixtures and final finishing.",
                StageTemplate.BOTH,
                6,
            ),
        ]

        for name, description, project_type, order in template_data:
            template, _ = StageTemplate.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "project_type": project_type,
                    "default_order": order,
                    "is_active": True,
                },
            )

            templates[name] = template

        # ============================================================
        # PROJECTS
        # ============================================================

        self.stdout.write("Creating projects...")

        project1, _ = Project.objects.get_or_create(
            name="Adebayo Family Residence",
            defaults={
                "client": client1,
                "description": (
                    "Modern four-bedroom family residence with a detached "
                    "boys quarter and landscaped compound."
                ),
                "project_type": Project.RESIDENTIAL,
                "status": Project.ACTIVE,
                "address": "Plot 18, Gwarinpa Estate",
                "city": "Abuja",
                "state": "FCT",
                "country": "Nigeria",
                "contract_value": Decimal("85000000.00"),
                "currency": "NGN",
                "management_fee_percent": Decimal("15.00"),
                "start_date": date.today() - timedelta(days=90),
                "estimated_end_date": date.today() + timedelta(days=180),
                "camera_stream_url": "https://example.com/camera/project-001",
                "camera_online": True,
            },
        )

        project2, _ = Project.objects.get_or_create(
            name="Victoria Island Office Complex",
            defaults={
                "client": client2,
                "description": (
                    "Three-floor commercial office development "
                    "with modern interiors."
                ),
                "project_type": Project.COMMERCIAL,
                "status": Project.ACTIVE,
                "address": "14 Adeola Odeku Street",
                "city": "Lagos",
                "state": "Lagos",
                "country": "Nigeria",
                "contract_value": Decimal("210000000.00"),
                "currency": "NGN",
                "management_fee_percent": Decimal("15.00"),
                "start_date": date.today() - timedelta(days=45),
                "estimated_end_date": date.today() + timedelta(days=300),
                "camera_stream_url": "https://example.com/camera/project-002",
                "camera_online": True,
            },
        )

        project3, _ = Project.objects.get_or_create(
            name="Okoro Residence Renovation",
            defaults={
                "client": client3,
                "description": (
                    "Full renovation of an existing residential property."
                ),
                "project_type": Project.RENOVATION,
                "status": Project.COMPLETED,
                "address": "21 Independence Avenue",
                "city": "Enugu",
                "state": "Enugu",
                "country": "Nigeria",
                "contract_value": Decimal("45000000.00"),
                "currency": "NGN",
                "management_fee_percent": Decimal("15.00"),
                "start_date": date.today() - timedelta(days=240),
                "estimated_end_date": date.today() - timedelta(days=30),
                "actual_end_date": date.today() - timedelta(days=20),
                "camera_online": False,
            },
        )

        # Assign team members
        project1.team_members.set([project_manager, site_engineer])
        project2.team_members.set([project_manager, site_engineer])
        project3.team_members.set([project_manager, site_engineer])

        projects = [project1, project2, project3]

        # ============================================================
        # EOI SUBMISSIONS
        # ============================================================

        self.stdout.write("Creating EOI submissions...")

        EOISubmission.objects.get_or_create(
            email="anthony.martins@example.com",
            defaults={
                "first_name": "Anthony",
                "last_name": "Martins",
                "phone": "+2348050000001",
                "project_type": "residential",
                "project_location": "Maitama, Abuja",
                "budget_range": "₦80m - ₦120m",
                "timeline": "12 months",
                "description": "Looking to build a modern family residence.",
                "tc_accepted": True,
                "status": EOISubmission.PENDING,
            },
        )

        EOISubmission.objects.get_or_create(
            email="fatima.yusuf@example.com",
            defaults={
                "first_name": "Fatima",
                "last_name": "Yusuf",
                "phone": "+2348050000002",
                "project_type": "commercial",
                "project_location": "Wuse 2, Abuja",
                "budget_range": "₦150m - ₦250m",
                "timeline": "18 months",
                "description": "Commercial property development.",
                "tc_accepted": True,
                "status": EOISubmission.CONTACTED,
                "notes": "Initial consultation completed.",
            },
        )

        EOISubmission.objects.get_or_create(
            email="patrick.obi@example.com",
            defaults={
                "first_name": "Patrick",
                "last_name": "Obi",
                "phone": "+2348050000003",
                "project_type": "renovation",
                "project_location": "Enugu",
                "budget_range": "₦30m - ₦50m",
                "timeline": "8 months",
                "description": "Complete renovation of an existing house.",
                "tc_accepted": True,
                "status": EOISubmission.CONVERTED,
                "showcase_user": client3,
            },
        )

        # ============================================================
        # STAGES
        # ============================================================

        self.stdout.write("Creating project stages...")

        stages = []

        stage_definitions = [
            (
                "Foundation",
                templates["Foundation"],
                Stage.COMPLETED,
                Decimal("12000000"),
                Decimal("8000000"),
                Decimal("4000000"),
            ),
            (
                "Structural Frame",
                templates["Structural Frame"],
                Stage.IN_PROGRESS,
                Decimal("22000000"),
                Decimal("14000000"),
                Decimal("8000000"),
            ),
            (
                "Blockwork",
                templates["Blockwork"],
                Stage.PENDING,
                Decimal("15000000"),
                Decimal("9000000"),
                Decimal("6000000"),
            ),
            (
                "Roofing",
                templates["Roofing"],
                Stage.PENDING,
                Decimal("10000000"),
                Decimal("6000000"),
                Decimal("4000000"),
            ),
        ]

        for project in projects:

            for index, (
                name,
                template,
                status,
                estimated,
                material_cost,
                labour_cost,
            ) in enumerate(stage_definitions, start=1):

                # Renovation project also gets roofing for seed consistency
                stage, _ = Stage.objects.get_or_create(
                    project=project,
                    order=index,
                    defaults={
                        "template": template,
                        "name": name,
                        "description": template.description,
                        "status": (
                            Stage.COMPLETED
                            if project == project3
                            else status
                        ),
                        "estimated_cost": estimated,
                        "material_cost": material_cost,
                        "labour_cost": labour_cost,
                        "planned_start": date.today() - timedelta(
                            days=100 - (index * 20)
                        ),
                        "planned_end": date.today() + timedelta(
                            days=index * 30
                        ),
                        "actual_start": (
                            date.today() - timedelta(days=100 - (index * 20))
                            if status != Stage.PENDING
                            else None
                        ),
                        "actual_end": (
                            date.today() - timedelta(days=10)
                            if (
                                status == Stage.COMPLETED
                                or project == project3
                            )
                            else None
                        ),
                        "admin_notes": "Stage created from project template.",
                    },
                )

                stage.assigned_staff.set(
                    [
                        staff2,
                        staff3,
                    ]
                )

                stages.append(stage)

        # ============================================================
        # STAGE COMMENTS
        # ============================================================

        self.stdout.write("Creating stage comments...")

        first_stage = Stage.objects.filter(project=project1).order_by("order").first()
        second_stage = Stage.objects.filter(project=project1).order_by("order")[1]

        StageComment.objects.get_or_create(
            stage=first_stage,
            author=project_manager,
            content="Foundation inspection completed successfully.",
        )

        StageComment.objects.get_or_create(
            stage=first_stage,
            author=client1,
            content="Everything looks good from the inspection photos.",
        )

        StageComment.objects.get_or_create(
            stage=second_stage,
            author=site_engineer,
            content="Structural columns are currently being reinforced.",
        )

        # ============================================================
        # SNAG ITEMS
        # ============================================================

        self.stdout.write("Creating snag items...")

        SnagItem.objects.get_or_create(
            stage=first_stage,
            title="Minor foundation surface crack",
            defaults={
                "raised_by": client1,
                "description": (
                    "Small surface crack noticed around the eastern "
                    "foundation wall."
                ),
                "status": SnagItem.RESOLVED,
                "resolved_at": timezone.now() - timedelta(days=5),
            },
        )

        SnagItem.objects.get_or_create(
            stage=second_stage,
            title="Reinforcement spacing check",
            defaults={
                "raised_by": project_manager,
                "description": (
                    "Verify spacing of reinforcement bars before concrete pour."
                ),
                "status": SnagItem.OPEN,
            },
        )

        # ============================================================
        # ATTENDANCE
        # ============================================================

        self.stdout.write("Creating attendance records...")

        for project in [project1, project2]:

            for staff in staff_members[:4]:

                for days_ago in range(1, 4):

                    AttendanceRecord.objects.get_or_create(
                        staff_member=staff,
                        project=project,
                        date=date.today() - timedelta(days=days_ago),
                        defaults={
                            "status": AttendanceRecord.PRESENT,
                            "time_in": time(7, 45),
                            "task_assigned": (
                                "Daily site supervision and construction activities"
                            ),
                            "logged_by": admin,
                        },
                    )

        # ============================================================
        # MATERIAL ISSUANCES
        # ============================================================

        self.stdout.write("Creating material issuances...")

        MaterialIssuance.objects.get_or_create(
            project=project1,
            stage=first_stage,
            issued_to=staff3,
            material=materials["Dangote Cement"],
            defaults={
                "quantity": Decimal("50"),
                "purpose": "Foundation concrete works",
                "issued_by": admin,
                "date": date.today() - timedelta(days=7),
            },
        )

        MaterialIssuance.objects.get_or_create(
            project=project1,
            stage=second_stage,
            issued_to=staff3,
            material=materials["12mm Reinforcement Bar"],
            defaults={
                "quantity": Decimal("120"),
                "purpose": "Column reinforcement",
                "issued_by": admin,
                "date": date.today() - timedelta(days=3),
            },
        )

        MaterialIssuance.objects.get_or_create(
            project=project2,
            issued_to=staff2,
            material=materials["9-inch Concrete Block"],
            defaults={
                "quantity": Decimal("1200"),
                "purpose": "External wall construction",
                "issued_by": admin,
                "date": date.today() - timedelta(days=2),
            },
        )

        # ============================================================
        # DELIVERY LOGS
        # ============================================================

        self.stdout.write("Creating delivery logs...")

        delivery1 = DeliveryLog.objects.create(
            project=project1,
            stage=first_stage,
            supplier=supplier1,
            material=materials["Dangote Cement"],
            quantity=Decimal("100"),
            unit_price=Decimal("10500.00"),
            total_amount=Decimal("1050000.00"),
            delivery_date=date.today() - timedelta(days=10),
            delivery_time=time(10, 30),
            status=DeliveryLog.CONFIRMED,
            supervisor_confirmed=True,
            client_confirmed=True,
            camera_footage_ref="CAM-001-10:30:00",
            logged_by=admin,
        )

        delivery2 = DeliveryLog.objects.create(
            project=project1,
            stage=second_stage,
            supplier=supplier1,
            material=materials["12mm Reinforcement Bar"],
            quantity=Decimal("200"),
            unit_price=Decimal("8500.00"),
            total_amount=Decimal("1700000.00"),
            delivery_date=date.today() - timedelta(days=4),
            delivery_time=time(9, 15),
            status=DeliveryLog.PENDING,
            supervisor_confirmed=True,
            client_confirmed=False,
            camera_footage_ref="CAM-001-09:15:00",
            logged_by=admin,
        )

        DeliveryLog.objects.create(
            project=project2,
            supplier=supplier2,
            material=materials["9-inch Concrete Block"],
            quantity=Decimal("2000"),
            unit_price=Decimal("850.00"),
            total_amount=Decimal("1700000.00"),
            delivery_date=date.today() - timedelta(days=2),
            delivery_time=time(11, 0),
            status=DeliveryLog.CONFIRMED,
            supervisor_confirmed=True,
            client_confirmed=True,
            camera_footage_ref="CAM-002-11:00:00",
            logged_by=admin,
        )

        # ============================================================
        # COST ANOMALY FLAGS
        # ============================================================

        self.stdout.write("Creating cost anomaly flags...")

        CostAnomalyFlag.objects.create(
            stage=second_stage,
            material=materials["12mm Reinforcement Bar"],
            submitted_price=Decimal("9800.00"),
            database_price=Decimal("8500.00"),
            variance_percent=Decimal("15.29"),
            status=CostAnomalyFlag.OPEN,
            admin_notes="Price is above current supplier database price.",
        )

        CostAnomalyFlag.objects.create(
            stage=first_stage,
            material=materials["Dangote Cement"],
            submitted_price=Decimal("11000.00"),
            database_price=Decimal("10500.00"),
            variance_percent=Decimal("4.76"),
            status=CostAnomalyFlag.REVIEWED,
            reviewed_by=admin,
            admin_notes="Reviewed and accepted due to recent supplier adjustment.",
        )

        # ============================================================
        # PAYMENTS
        # ============================================================

        self.stdout.write("Creating payments...")

        payment1 = Payment.objects.create(
            project=project1,
            stage=first_stage,
            client=client1,
            amount=Decimal("15000000.00"),
            currency="NGN",
            material_cost=Decimal("8000000.00"),
            labour_cost=Decimal("4000000.00"),
            management_fee=Decimal("3000000.00"),
            management_fee_percent=Decimal("15.00"),
            status=Payment.CONFIRMED,
            payment_method=Payment.FLUTTERWAVE,
            flutterwave_ref="FLW-SEED-000001",
            flutterwave_tx_id="TX-SEED-000001",
            gateway_response={
                "status": "successful",
                "message": "Transaction successful",
            },
            confirmed_at=timezone.now() - timedelta(days=20),
        )

        Payment.objects.create(
            project=project1,
            stage=second_stage,
            client=client1,
            amount=Decimal("25000000.00"),
            currency="NGN",
            material_cost=Decimal("14000000.00"),
            labour_cost=Decimal("8000000.00"),
            management_fee=Decimal("3000000.00"),
            management_fee_percent=Decimal("15.00"),
            status=Payment.PROCESSING,
            payment_method=Payment.BANK_TRANSFER,
            flutterwave_ref="",
            gateway_response={
                "status": "pending",
                "message": "Awaiting bank confirmation",
            },
        )

        third_stage_project1 = Stage.objects.filter(
            project=project1
        ).order_by("order")[2]

        Payment.objects.create(
            project=project1,
            stage=third_stage_project1,
            client=client1,
            amount=Decimal("18000000.00"),
            currency="NGN",
            material_cost=Decimal("10000000.00"),
            labour_cost=Decimal("5500000.00"),
            management_fee=Decimal("2500000.00"),
            management_fee_percent=Decimal("15.00"),
            status=Payment.PENDING,
            payment_method="",
        )

        # Completed project payment
        for stage in Stage.objects.filter(project=project3):
            Payment.objects.create(
                project=project3,
                stage=stage,
                client=client3,
                amount=stage.total_amount_due,
                currency="NGN",
                material_cost=stage.material_cost,
                labour_cost=stage.labour_cost,
                management_fee=stage.management_fee,
                management_fee_percent=Decimal("15.00"),
                status=Payment.CONFIRMED,
                payment_method=Payment.FLUTTERWAVE,
                flutterwave_ref=f"FLW-COMPLETED-{stage.order:03d}",
                flutterwave_tx_id=f"TX-COMPLETED-{stage.order:03d}",
                gateway_response={
                    "status": "successful",
                    "message": "Transaction successful",
                },
                confirmed_at=timezone.now() - timedelta(days=60),
            )

        # ============================================================
        # REFUND REQUESTS
        # ============================================================

        self.stdout.write("Creating refund requests...")

        RefundRequest.objects.create(
            project=project3,
            client=client3,
            reason=(
                "Client requested refund of remaining project balance "
                "after project completion."
            ),
            amount_paid=Decimal("45000000.00"),
            deduction_effort=Decimal("1000000.00"),
            deduction_processing=Decimal("250000.00"),
            net_refund=Decimal("43750000.00"),
            status=RefundRequest.PROCESSED,
            admin_notes="Refund processed successfully.",
            processing_deadline=date.today() - timedelta(days=30),
            processed_at=timezone.now() - timedelta(days=25),
        )

        RefundRequest.objects.create(
            project=project1,
            client=client1,
            reason="Requesting refund for cancelled material order.",
            amount_paid=Decimal("5000000.00"),
            deduction_effort=Decimal("250000.00"),
            deduction_processing=Decimal("100000.00"),
            net_refund=Decimal("4650000.00"),
            status=RefundRequest.PENDING,
            processing_deadline=date.today() + timedelta(days=5),
        )

        # ============================================================
        # PROJECT MEDIA
        # ============================================================

        self.stdout.write("Creating project media...")

        ProjectMedia.objects.create(
            project=project1,
            stage=first_stage,
            uploaded_by=site_engineer,
            media_type=ProjectMedia.PHOTO,
            title="Foundation Progress",
            description="Foundation work after concrete pour.",
            file="project-media/foundation-progress.jpg",
            blob_name="project-001/foundation-progress.jpg",
            blob_url="https://example.blob.core.windows.net/project-001/foundation-progress.jpg",
            file_size=2450000,
            storage_tier=ProjectMedia.HOT,
        )

        ProjectMedia.objects.create(
            project=project1,
            stage=second_stage,
            uploaded_by=site_engineer,
            media_type=ProjectMedia.VIDEO,
            title="Structural Frame Progress",
            description="Video showing ongoing structural frame work.",
            file="project-media/structural-frame.mp4",
            blob_name="project-001/structural-frame.mp4",
            blob_url="https://example.blob.core.windows.net/project-001/structural-frame.mp4",
            file_size=85000000,
            duration_seconds=120,
            storage_tier=ProjectMedia.HOT,
        )

        ProjectMedia.objects.create(
            project=project2,
            uploaded_by=project_manager,
            media_type=ProjectMedia.PHOTO,
            title="Office Site Overview",
            description="Current overview of the commercial development.",
            file="project-media/office-overview.jpg",
            blob_name="project-002/office-overview.jpg",
            blob_url="https://example.blob.core.windows.net/project-002/office-overview.jpg",
            file_size=3200000,
            storage_tier=ProjectMedia.COOL,
        )

        ProjectMedia.objects.create(
            project=project1,
            stage=first_stage,
            uploaded_by=site_engineer,
            media_type=ProjectMedia.DELIVERY,
            title="Cement Delivery Footage",
            description="Footage showing delivery of cement to site.",
            file="project-media/cement-delivery.mp4",
            blob_name="project-001/cement-delivery.mp4",
            blob_url="https://example.blob.core.windows.net/project-001/cement-delivery.mp4",
            file_size=65000000,
            duration_seconds=90,
            storage_tier=ProjectMedia.HOT,
            delivery_log=delivery1,
        )

        # ============================================================
        # MESSAGE THREADS
        # ============================================================

        self.stdout.write("Creating message threads...")

        thread1 = MessageThread.objects.create(
            project=project1,
            subject="Foundation Progress Update",
        )

        thread1.participants.set(
            [
                client1,
                project_manager,
                site_engineer,
            ]
        )

        thread1.agents.set(
            [
                staff1,
                staff2,
            ]
        )

        Message.objects.create(
            thread=thread1,
            sender=project_manager,
            content=(
                "Hello John, the foundation stage has been completed "
                "successfully. We have uploaded the latest site photos."
            ),
            is_read=True,
            read_at=timezone.now() - timedelta(hours=5),
        )

        Message.objects.create(
            thread=thread1,
            sender=client1,
            content=(
                "Thanks. I have reviewed the photos. Everything looks good."
            ),
            is_read=False,
        )

        thread2 = MessageThread.objects.create(
            project=project2,
            subject="Material Delivery",
        )

        thread2.participants.set(
            [
                client2,
                project_manager,
            ]
        )

        thread2.agents.set([staff1])

        Message.objects.create(
            thread=thread2,
            sender=project_manager,
            content=(
                "The reinforcement materials have been delivered to site "
                "and are awaiting inspection."
            ),
            is_read=False,
        )

        # ============================================================
        # NOTIFICATIONS
        # ============================================================

        self.stdout.write("Creating notifications...")

        notifications = [
            {
                "recipient": client1,
                "project": project1,
                "notification_type": Notification.STAGE_COMPLETE,
                "title": "Foundation Stage Completed",
                "body": (
                    "The foundation stage of your project has been completed."
                ),
                "channel": Notification.IN_APP,
                "status": Notification.SENT,
            },
            {
                "recipient": client1,
                "project": project1,
                "notification_type": Notification.PAYMENT_DUE,
                "title": "Payment Due",
                "body": (
                    "Your next project stage payment is now due."
                ),
                "channel": Notification.EMAIL,
                "status": Notification.SENT,
            },
            {
                "recipient": client2,
                "project": project2,
                "notification_type": Notification.MEDIA_UPLOADED,
                "title": "New Project Media",
                "body": (
                    "New photos have been uploaded to your project."
                ),
                "channel": Notification.IN_APP,
                "status": Notification.PENDING,
            },
            {
                "recipient": project_manager,
                "project": project1,
                "notification_type": Notification.MESSAGE_RECEIVED,
                "title": "New Client Message",
                "body": (
                    "John Adebayo sent a new message about the project."
                ),
                "channel": Notification.IN_APP,
                "status": Notification.PENDING,
            },
            {
                "recipient": client3,
                "project": project3,
                "notification_type": Notification.PAYMENT_CONFIRMED,
                "title": "Payment Confirmed",
                "body": (
                    "Your project payment has been confirmed."
                ),
                "channel": Notification.EMAIL,
                "status": Notification.SENT,
            },
        ]

        for notification in notifications:
            Notification.objects.create(**notification)

        # ============================================================
        # SUMMARY
        # ============================================================

        self.stdout.write("\n")
        self.stdout.write(
            self.style.SUCCESS("Database seeding completed successfully!")
        )

        self.stdout.write("\nSeed summary:")
        self.stdout.write(f"Users: {User.objects.count()}")
        self.stdout.write(f"Projects: {Project.objects.count()}")
        self.stdout.write(f"EOI submissions: {EOISubmission.objects.count()}")
        self.stdout.write(f"Staff roles: {StaffRole.objects.count()}")
        self.stdout.write(f"Staff members: {StaffMember.objects.count()}")
        self.stdout.write(f"Suppliers: {Supplier.objects.count()}")
        self.stdout.write(f"Material categories: {MaterialCategory.objects.count()}")
        self.stdout.write(f"Materials: {Material.objects.count()}")
        self.stdout.write(f"Material prices: {MaterialPrice.objects.count()}")
        self.stdout.write(f"Stage templates: {StageTemplate.objects.count()}")
        self.stdout.write(f"Stages: {Stage.objects.count()}")
        self.stdout.write(f"Stage comments: {StageComment.objects.count()}")
        self.stdout.write(f"Snag items: {SnagItem.objects.count()}")
        self.stdout.write(f"Attendance records: {AttendanceRecord.objects.count()}")
        self.stdout.write(f"Material issuances: {MaterialIssuance.objects.count()}")
        self.stdout.write(f"Delivery logs: {DeliveryLog.objects.count()}")
        self.stdout.write(f"Cost anomaly flags: {CostAnomalyFlag.objects.count()}")
        self.stdout.write(f"Payments: {Payment.objects.count()}")
        self.stdout.write(f"Refund requests: {RefundRequest.objects.count()}")
        self.stdout.write(f"Project media: {ProjectMedia.objects.count()}")
        self.stdout.write(f"Message threads: {MessageThread.objects.count()}")
        self.stdout.write(f"Messages: {Message.objects.count()}")
        self.stdout.write(f"Notifications: {Notification.objects.count()}")

        self.stdout.write("\nDevelopment login accounts:")
        self.stdout.write("Admin: admin@kaflox.com / Admin123!")
        self.stdout.write("Manager: manager@kaflox.com / Manager123!")
        self.stdout.write("Engineer: engineer@kaflox.com / Engineer123!")
        self.stdout.write("Client: john.adebayo@example.com / Client123!")