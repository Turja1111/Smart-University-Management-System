from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from courses.models import Course, Department, Enrollment
from courses.schedule_utils import (
    department_code_from_course_code,
    department_display_name,
    section_to_slots,
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Import class routine sections from routine_extracted.json into Course rows.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default='routine_extracted.json',
            help='JSON path relative to project BASE_DIR (default: routine_extracted.json)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing Course rows whose code appears in the JSON before import.',
        )
        parser.add_argument(
            '--semester',
            type=str,
            default='fall',
            choices=['spring', 'summer', 'fall'],
            help='Course.semester value',
        )
        parser.add_argument(
            '--year',
            type=int,
            default=2026,
            help='Course.year',
        )
        parser.add_argument(
            '--enroll-email',
            type=str,
            default='',
            help='If set, enroll this student user in imported courses (see --enroll-limit).',
        )
        parser.add_argument(
            '--enroll-limit',
            type=int,
            default=0,
            help='Max courses to enroll (0 = enroll in all imported sections).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse and report counts without writing to the database.',
        )

    def handle(self, *args, **options):
        base = Path(settings.BASE_DIR)
        path = base / options['path']
        if not path.is_file():
            self.stderr.write(self.style.ERROR(f'File not found: {path}'))
            return

        raw = json.loads(path.read_text(encoding='utf-8'))
        sections = raw.get('sections')
        if not sections:
            self.stderr.write(self.style.ERROR('No "sections" key in JSON. Run parse_routine.py or use a full export.'))
            return

        semester = options['semester']
        year = options['year']
        dry = options['dry_run']

        dept_cache: dict[str, Department] = {}

        def get_dept(course_code: str) -> Department:
            key = department_code_from_course_code(course_code)
            if key in dept_cache:
                return dept_cache[key]
            name = department_display_name(key)
            if dry:
                d = Department(id=0, code=key, name=name)
                dept_cache[key] = d
                return d
            d, _ = Department.objects.get_or_create(
                code=key,
                defaults={'name': name, 'description': f'Auto-created from routine import ({key}).'},
            )
            dept_cache[key] = d
            return d

        codes_in_json = [s.get('course_full') for s in sections if s.get('course_full')]
        if options['clear'] and not dry:
            Course.objects.filter(code__in=codes_in_json).delete()
            self.stdout.write(self.style.WARNING('Clear: removed existing imported courses (matching codes from JSON).'))

        created = 0
        updated = 0
        for sec in sections:
            full = (sec.get('course_full') or '').strip()
            base_code = (sec.get('course_code') or '').strip()
            section_id = (sec.get('section') or '').strip()
            if not full or not base_code:
                continue

            dept = get_dept(base_code)
            slots = section_to_slots(sec)
            theory = sec.get('theory') or {}
            lab = sec.get('lab')
            schedule = {
                'slots': slots,
                'faculty_theory_initial': theory.get('initial'),
                'lab_faculty': lab.get('faculty') if isinstance(lab, dict) else None,
            }

            name = f'{base_code} — Section {section_id}'[:200]
            defaults = {
                'name': name,
                'description': '',
                'department': dept,
                'teacher': None,
                'credits': 3,
                'semester': semester,
                'year': year,
                'schedule': schedule,
                'max_students': 40,
                'is_active': True,
            }

            if dry:
                created += 1
                continue

            obj, was_created = Course.objects.update_or_create(
                code=full,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Routine import: {"(dry-run) " if dry else ""}{len(sections)} sections in file; '
                f'courses created={created}, updated={updated}.'
            )
        )

        enroll_email = (options['enroll_email'] or '').strip()
        limit = options['enroll_limit']
        if enroll_email and not dry:
            try:
                student = User.objects.get(email=enroll_email, role=User.Role.STUDENT)
            except User.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f'No student user with email {enroll_email!r}. Skipping enrollments.')
                )
                return

            imported_codes = [c for c in codes_in_json if c]
            courses_qs = Course.objects.filter(code__in=imported_codes).order_by('code')
            if limit and limit > 0:
                courses_qs = courses_qs[:limit]

            n = 0
            for course in courses_qs:
                Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={'status': Enrollment.Status.ENROLLED},
                )
                n += 1
            self.stdout.write(self.style.SUCCESS(f'Enrolled {student.email} in {n} course(s).'))
