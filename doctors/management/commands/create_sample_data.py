from django.core.management.base import BaseCommand
from doctors.models import Department, Specialization, Doctor, DoctorAvailability
from users.models import User

class Command(BaseCommand):
    help = 'Create sample departments and specializations for the hospital system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create Departments
        departments_data = [
            {
                'name': 'Internal Medicine',
                'description': 'Medical specialty dealing with prevention, diagnosis, and treatment of adult diseases'
            },
            {
                'name': 'Surgery',
                'description': 'Medical specialty using operative manual and instrumental techniques'
            },
            {
                'name': 'Pediatrics',
                'description': 'Medical care of infants, children, and adolescents'
            },
            {
                'name': 'Obstetrics & Gynecology',
                'description': 'Medical and surgical specialty dealing with women\'s health'
            },
            {
                'name': 'Orthopedics',
                'description': 'Medical specialty focused on injuries and diseases of the musculoskeletal system'
            },
            {
                'name': 'Cardiology',
                'description': 'Medical specialty dealing with disorders of the heart and blood vessels'
            },
            {
                'name': 'Dermatology',
                'description': 'Medical specialty dealing with skin, hair, nails, and related disorders'
            },
            {
                'name': 'Neurology',
                'description': 'Medical specialty dealing with disorders of the nervous system'
            }
        ]

        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            departments[dept_data['name']] = dept
            if created:
                self.stdout.write(f'Created department: {dept.name}')
            else:
                self.stdout.write(f'Department already exists: {dept.name}')

        # Create Specializations
        specializations_data = [
            # Internal Medicine
            {'name': 'General Internal Medicine', 'department': 'Internal Medicine'},
            {'name': 'Endocrinology', 'department': 'Internal Medicine'},
            {'name': 'Gastroenterology', 'department': 'Internal Medicine'},
            {'name': 'Infectious Disease', 'department': 'Internal Medicine'},
            
            # Surgery
            {'name': 'General Surgery', 'department': 'Surgery'},
            {'name': 'Plastic Surgery', 'department': 'Surgery'},
            {'name': 'Vascular Surgery', 'department': 'Surgery'},
            {'name': 'Neurosurgery', 'department': 'Surgery'},
            
            # Pediatrics
            {'name': 'General Pediatrics', 'department': 'Pediatrics'},
            {'name': 'Pediatric Cardiology', 'department': 'Pediatrics'},
            {'name': 'Pediatric Surgery', 'department': 'Pediatrics'},
            
            # OB/GYN
            {'name': 'Obstetrics', 'department': 'Obstetrics & Gynecology'},
            {'name': 'Gynecology', 'department': 'Obstetrics & Gynecology'},
            {'name': 'Reproductive Endocrinology', 'department': 'Obstetrics & Gynecology'},
            
            # Orthopedics
            {'name': 'General Orthopedics', 'department': 'Orthopedics'},
            {'name': 'Sports Medicine', 'department': 'Orthopedics'},
            {'name': 'Spine Surgery', 'department': 'Orthopedics'},
            
            # Cardiology
            {'name': 'General Cardiology', 'department': 'Cardiology'},
            {'name': 'Interventional Cardiology', 'department': 'Cardiology'},
            {'name': 'Electrophysiology', 'department': 'Cardiology'},
            
            # Dermatology
            {'name': 'General Dermatology', 'department': 'Dermatology'},
            {'name': 'Dermatopathology', 'department': 'Dermatology'},
            {'name': 'Pediatric Dermatology', 'department': 'Dermatology'},
            
            # Neurology
            {'name': 'General Neurology', 'department': 'Neurology'},
            {'name': 'Epilepsy', 'department': 'Neurology'},
            {'name': 'Movement Disorders', 'department': 'Neurology'},
        ]

        for spec_data in specializations_data:
            dept = departments[spec_data['department']]
            spec, created = Specialization.objects.get_or_create(
                name=spec_data['name'],
                defaults={'department': dept}
            )
            if created:
                self.stdout.write(f'Created specialization: {spec.name}')
            else:
                self.stdout.write(f'Specialization already exists: {spec.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {Department.objects.count()} departments and {Specialization.objects.count()} specializations'
            )
        )
