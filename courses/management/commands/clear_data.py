from __future__ import annotations

from typing import Set, Type

from django.apps import apps
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = (
        'Delete rows from all models except preserved authentication/user models. '
        'Use --dry-run to preview; use --yes to execute.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without performing deletes')
        parser.add_argument('--yes', action='store_true', help='Confirm destructive action')
        parser.add_argument('--preserve', type=str, default='', help='Comma-separated model dotted names to preserve (e.g. app.Model)')

    def handle(self, *args, **options):
        dry = options['dry_run']
        confirm = options['yes']
        extra = options.get('preserve') or ''

        User = get_user_model()

        # Build set of model classes to preserve
        preserve: Set[Type] = {User}

        # Preserve common auth models
        try:
            from django.contrib.auth.models import Group, Permission

            preserve.update({Group, Permission})
        except Exception:
            pass

        # Preserve simplejwt token blacklist models if present
        try:
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

            preserve.update({OutstandingToken, BlacklistedToken})
        except Exception:
            pass

        # Allow additional preserve models via --preserve
        for spec in [s.strip() for s in extra.split(',') if s.strip()]:
            try:
                app_label, model_name = spec.split('.', 1)
                m = apps.get_model(app_label, model_name)
                preserve.add(m)
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'Could not resolve preserve model {spec}: {e}'))

        # Collect all models
        all_models = list(apps.get_models())

        # Prepare summary
        to_delete = []
        for m in all_models:
            if m in preserve:
                continue
            # Skip migration and auth-related internal tables? we already preserved auth models
            to_delete.append(m)

        self.stdout.write(self.style.WARNING('This command will delete rows from the following models:'))
        for m in to_delete:
            self.stdout.write(f' - {m._meta.app_label}.{m._meta.model_name} ({m.objects.count()} rows)')

        if dry:
            self.stdout.write(self.style.SUCCESS('Dry run complete. No data was deleted.'))
            return

        if not confirm:
            self.stdout.write(self.style.ERROR('Destructive action not confirmed. Re-run with --yes to proceed.'))
            return

        # Perform deletion
        for m in to_delete:
            name = f'{m._meta.app_label}.{m._meta.model_name}'
            try:
                cnt = m.objects.count()
                if cnt:
                    m.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS(f'Deleted {cnt} rows from {name}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'No rows in {name}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Failed to clear {name}: {e}'))

        self.stdout.write(self.style.SUCCESS('Clear operation finished.'))
