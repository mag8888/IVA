# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Баланс пользователя в долларах', max_digits=10, verbose_name='Баланс'),
        ),
    ]

