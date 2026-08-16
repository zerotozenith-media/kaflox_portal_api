from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stage',
            name='assigned_staff',
            field=models.ManyToManyField(
                blank=True,
                help_text='Staff members assigned to work on this stage',
                related_name='assigned_stages',
                to='staff.staffmember',
            ),
        ),
    ]
