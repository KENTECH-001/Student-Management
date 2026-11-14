import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_junior_subjects_senior_subjects'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),

        migrations.RemoveField(
            model_name='student',
            name='studentClass',
        ),

        migrations.AddField(
            model_name='student',
            name='assigned_class',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='students',
                to='myapp.schoolclass'
            ),
        ),

        migrations.RemoveField(
            model_name='teacher',
            name='assigned_class',
        ),

        migrations.AddField(
            model_name='teacher',
            name='assigned_class',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='class_teacher',
                to='myapp.schoolclass'
            ),
        ),
    ]