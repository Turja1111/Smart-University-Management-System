from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='admission_session',
            field=models.CharField(blank=True, help_text='e.g. SPRING 2022', max_length=40),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='birth_certificate_no',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='emergency_contact_name',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='passport_no',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='emergency_contact',
            field=models.CharField(blank=True, help_text='Phone or alternate contact', max_length=40),
        ),
    ]
