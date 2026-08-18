from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0001_initial'),
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectDocument',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Display name of the document', max_length=200)),
                ('document_type', models.CharField(choices=[('contract', 'Contract'), ('legal', 'Legal'), ('drawing', 'Drawing'), ('permit', 'Permit'), ('signoff', 'Sign-Off'), ('report', 'Report'), ('policy', 'Policy'), ('other', 'Other')], default='other', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('file', models.FileField(upload_to='project-documents/')),
                ('blob_name', models.CharField(blank=True, max_length=500)),
                ('blob_url', models.URLField(blank=True)),
                ('file_size', models.PositiveBigIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='projects.project')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Project Document',
                'verbose_name_plural': 'Project Documents',
                'db_table': 'project_documents',
                'ordering': ['document_type', '-created_at'],
            },
        ),
    ]
