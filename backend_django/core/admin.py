from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from decimal import Decimal
from .models import User
from mlm.models import Tariff
from billing.models import Payment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-панель для пользователей."""
    list_display = ['username', 'email', 'status', 'referral_code', 'get_invited_by', 'get_total_bonuses', 'is_active_mlm', 'date_joined']
    list_filter = ['status', 'is_active_mlm', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'referral_code', 'telegram_id']
    actions = ['add_balance_action']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('MLM Information', {
            'fields': ('status', 'referral_code', 'invited_by', 'is_active_mlm', 'telegram_id')
        }),
    )
    
    def get_invited_by(self, obj):
        """Отображение партнера с ссылкой на него."""
        if obj.invited_by:
            return format_html(
                '<a href="/admin/core/user/{}/change/">{}</a>',
                obj.invited_by.id,
                obj.invited_by.username
            )
        return "-"
    get_invited_by.short_description = "Партнер"
    get_invited_by.admin_order_field = 'invited_by'
    
    def get_total_bonuses(self, obj):
        """Получить общую сумму бонусов пользователя."""
        from billing.models import Bonus
        from django.db.models import Sum
        total = Bonus.objects.filter(user=obj).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        return f"${total:.2f}"
    get_total_bonuses.short_description = "Бонусы"
    
    def add_balance_action(self, request, queryset):
        """Action для пополнения счета выбранных пользователей."""
        from django.http import HttpResponse
        from django.middleware.csrf import get_token
        
        # Проверяем, была ли отправлена форма
        if request.method == 'POST' and 'tariff_id' in request.POST and 'amount' in request.POST:
            tariff_id = request.POST.get('tariff_id')
            amount = request.POST.get('amount')
            
            if not tariff_id or not amount:
                self.message_user(request, "❌ Не указаны тариф или сумма", level='error')
                return
            
            try:
                tariff = Tariff.objects.get(id=tariff_id)
                amount_decimal = Decimal(amount)
                
                created_count = 0
                for user in queryset:
                    payment = Payment.objects.create(
                        user=user,
                        tariff=tariff,
                        amount=amount_decimal,
                        status=Payment.PaymentStatus.COMPLETED,
                        completed_at=timezone.now(),
                        metadata={'admin_action': True, 'admin_user': request.user.username}
                    )
                    created_count += 1
                
                self.message_user(
                    request,
                    f"✅ Создано {created_count} платежей на сумму ${amount_decimal} каждый для тарифа '{tariff.name}'",
                    level='success'
                )
                # Перенаправляем обратно к списку пользователей
                from django.http import HttpResponseRedirect
                return HttpResponseRedirect(request.path)
            except Exception as e:
                self.message_user(request, f"❌ Ошибка: {e}", level='error')
                return
        
        # Отображаем форму выбора тарифа и суммы
        tariffs = Tariff.objects.filter(is_active=True).order_by('entry_amount')
        csrf_token = get_token(request)
        
        tariff_options = '\n'.join([
            f'                        <option value="{t.id}">{t.name} - ${t.entry_amount}</option>'
            for t in tariffs
        ])
        
        # Сохраняем выбранные пользователей в сессии для повторного использования
        user_ids = ','.join(str(u.id) for u in queryset)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Пополнение счета</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                }}
                h2 {{
                    color: #417690;
                }}
                form {{
                    margin-top: 20px;
                }}
                label {{
                    display: block;
                    margin-top: 15px;
                    font-weight: bold;
                }}
                select, input[type="number"] {{
                    width: 100%;
                    padding: 8px;
                    margin-top: 5px;
                    box-sizing: border-box;
                }}
                .button {{
                    padding: 10px 20px;
                    margin-top: 20px;
                    border: none;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                }}
                .submit {{
                    background: #417690;
                    color: white;
                }}
                .cancel {{
                    background: #ba2121;
                    color: white;
                    margin-left: 10px;
                }}
            </style>
        </head>
        <body>
            <h2>💳 Пополнение счета</h2>
            <p><strong>Выбрано пользователей: {queryset.count()}</strong></p>
            <form method="post" action="">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}" />
                <input type="hidden" name="action" value="add_balance_action" />
                <input type="hidden" name="_selected_action" value="{user_ids}" />
                <label for="tariff_id">Тариф:</label>
                <select name="tariff_id" id="tariff_id" required>
                    <option value="">-- Выберите тариф --</option>
{tariff_options}
                </select>
                <label for="amount">Сумма пополнения ($):</label>
                <input type="number" name="amount" id="amount" step="0.01" min="0" required />
                <div>
                    <input type="submit" class="button submit" value="Пополнить счет" />
                    <a href="/admin/core/user/" class="button cancel">Отмена</a>
                </div>
            </form>
        </body>
        </html>
        """
        return HttpResponse(html)
    add_balance_action.short_description = "💳 Пополнить счет (создать платеж)"
