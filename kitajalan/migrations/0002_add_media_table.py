from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('kitajalan', '0001_initial'),  # Sesuaikan dengan nomor migrasi terakhir
    ]

    operations = [
        migrations.CreateModel(
            name='MediaPembelajaran',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('judul', models.CharField(max_length=200)),
                ('tipe', models.CharField(choices=[('video', 'Video'), ('gambar', 'Gambar'), ('file', 'File Dokumen')], max_length=10)),
                ('file', models.FileField(upload_to='uploads/%Y/%m/%d/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'ordering': ['-uploaded_at'],
                'db_table': 'kitajalan_mediapembelajaran',
            },
        ),
    ]