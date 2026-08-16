from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagethread',
            name='agents',
            field=models.ManyToManyField(
                blank=True,
                help_text='Staff members assigned to respond to client messages in this thread',
                related_name='assigned_threads',
                to='staff.staffmember',
            ),
        ),
    ]
