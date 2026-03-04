from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_alter_booking_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=100, unique=True)),
                ('transaction_type', models.CharField(choices=[('booking', 'Booking'), ('advertisement', 'Advertisement'), ('sponsorship', 'Sponsorship')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('upi', 'UPI'), ('paytm', 'PayTM'), ('phonepay', 'PhonePay'), ('googlepay', 'Google Pay'), ('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'), ('crypto', 'Cryptocurrency')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('admin_notes', models.TextField(blank=True)),
                ('admin_approved', models.BooleanField(default=False)),
                ('admin_approved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('advertisement', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='booking.advertisement')),
                ('admin_approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_payments', to=settings.AUTH_USER_MODEL)),
                ('booking', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='booking.booking')),
                ('tournament', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='booking.tournament')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user', 'status'], name='booking_paym_user_id_status_idx'),
                    models.Index(fields=['transaction_type', 'status'], name='booking_paym_transac_status_idx'),
                ],
            },
        ),
    ]
