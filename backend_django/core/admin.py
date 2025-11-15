from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.urls import reverse
from decimal import Decimal
from .models import User
from mlm.models import Tariff, StructureNode
from billing.models import Payment, Bonus


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-панель для пользователей."""
    list_display = ['username', 'email', 'status', 'referral_code', 'get_invited_by', 'get_balance_display', 'get_total_bonuses', 'get_invited_count', 'is_active_mlm', 'date_joined']
    list_filter = ['status', 'is_active_mlm', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'referral_code', 'telegram_id']
    actions = ['add_balance_action', 'add_balance_direct_action']
    readonly_fields = ['get_balance_info', 'get_balance_history', 'get_structure_info', 'get_referral_stats']
    date_hierarchy = 'date_joined'
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('MLM Information', {
            'fields': ('status', 'referral_code', 'invited_by', 'is_active_mlm', 'telegram_id', 'get_referral_stats')
        }),
        ('Структура', {
            'fields': ('get_structure_info',),
            'classes': ('collapse',)
        }),
        ('Баланс', {
            'fields': ('balance', 'get_balance_info', 'get_balance_history'),
            'classes': ('collapse',)
        }),
    )
    
    def get_invited_by(self, obj):
        """Отображение партнера с ссылкой на него."""
        if obj.invited_by:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:core_user_change', args=[obj.invited_by.id]),
                obj.invited_by.username
            )
        return "-"
    get_invited_by.short_description = "Партнер"
    get_invited_by.admin_order_field = 'invited_by'
    
    def get_invited_count(self, obj):
        """Количество приглашенных пользователей."""
        total = obj.invited_users.count()
        with_payment = obj.invited_users.filter(
            payments__status=Payment.PaymentStatus.COMPLETED
        ).distinct().count()
        
        if total > 0:
            return format_html(
                '<span style="color: #417690; font-weight: bold;">{}/{}</span>',
                with_payment,
                total
            )
        return "0/0"
    get_invited_count.short_description = "Приглашено"
    get_invited_count.admin_order_field = 'invited_users'
    
    def get_total_bonuses(self, obj):
        """Получить общую сумму бонусов пользователя."""
        total = Bonus.objects.filter(user=obj).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        green = Bonus.objects.filter(user=obj, bonus_type=Bonus.BonusType.GREEN).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        yellow = Bonus.objects.filter(user=obj, bonus_type=Bonus.BonusType.YELLOW).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        return format_html(
            '<div style="line-height: 1.4;">'
            '<span style="color: #28a745;">💚 ${:.2f}</span><br>'
            '<span style="color: #ffc107;">💛 ${:.2f}</span><br>'
            '<strong>💰 ${:.2f}</strong>'
            '</div>',
            green, yellow, total
        )
    get_total_bonuses.short_description = "Бонусы"
    
    def get_balance_display(self, obj):
        """Отображение баланса с цветом."""
        balance = obj.balance or Decimal('0.00')
        if balance > 0:
            color = '#28a745'
            icon = '💰'
        elif balance < 0:
            color = '#dc3545'
            icon = '⚠️'
        else:
            color = '#6c757d'
            icon = '💵'
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 1.1em;">{} ${:.2f}</span>',
            color,
            icon,
            balance
        )
    get_balance_display.short_description = "Баланс"
    get_balance_display.admin_order_field = 'balance'
    
    def get_structure_info(self, obj):
        """Информация о структуре пользователя."""
        if not obj.pk:
            return "Сначала сохраните пользователя"
        
        try:
            node = obj.structure_node
        except StructureNode.DoesNotExist:
            return format_html('<p style="color: #dc3545;">⚠️ Пользователь не размещен в структуре</p>')
        
        children = node.children.all()
        children_count = children.count()
        
        # Получаем информацию о родителе
        parent_info = ""
        if node.parent:
            parent_node = StructureNode.objects.filter(user=node.parent).first()
            if parent_node:
                parent_info = format_html(
                    '<p><strong>Родитель:</strong> <a href="{}">{}</a> (Уровень {}, Позиция {})</p>',
                    reverse('admin:core_user_change', args=[node.parent.id]),
                    node.parent.username,
                    parent_node.level,
                    parent_node.position
                )
        
        # Информация о детях
        children_html = ""
        if children_count > 0:
            children_html = '<div style="margin-top: 10px;"><strong>Дети ({})</strong><ul style="margin: 5px 0; padding-left: 20px;">'.format(children_count)
            for child in children:
                children_html += format_html(
                    '<li><a href="{}">{}</a> (Позиция {})</li>',
                    reverse('admin:core_user_change', args=[child.user.id]),
                    child.user.username,
                    child.position
                )
            children_html += '</ul></div>'
        else:
            children_html = '<p style="color: #6c757d; margin-top: 10px;">Нет детей в структуре</p>'
        
        return format_html(
            '<div style="padding: 15px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;">'
            '<h3 style="margin-top: 0; color: #417690;">🌳 Информация о структуре</h3>'
            '<p><strong>Уровень:</strong> {}</p>'
            '<p><strong>Позиция:</strong> {}</p>'
            '<p><strong>Тариф:</strong> {}</p>'
            '{}'
            '{}'
            '</div>',
            node.level,
            node.position,
            node.tariff.name if node.tariff else 'Не указан',
            parent_info,
            children_html
        )
    get_structure_info.short_description = "🌳 Структура"
    
    def get_referral_stats(self, obj):
        """Статистика по реферальной программе."""
        if not obj.pk:
            return "Сначала сохраните пользователя"
        
        total_invited = obj.invited_users.count()
        invited_with_payment = obj.invited_users.filter(
            payments__status=Payment.PaymentStatus.COMPLETED
        ).distinct().count()
        
        total_payments = Payment.objects.filter(
            user__in=obj.invited_users.all(),
            status=Payment.PaymentStatus.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        return format_html(
            '<div style="padding: 10px; background: #e7f3ff; border: 1px solid #b3d9ff; border-radius: 5px; margin: 10px 0;">'
            '<p><strong>📊 Статистика рефералов:</strong></p>'
            '<p>Всего приглашено: <strong>{}</strong></p>'
            '<p>С оплатой: <strong style="color: #28a745;">{}</strong></p>'
            '<p>Общая сумма платежей: <strong style="color: #417690;">${:.2f}</strong></p>'
            '<p style="margin-top: 10px; margin-bottom: 0;">Реферальная ссылка: <code style="background: white; padding: 2px 5px; border-radius: 3px;">https://t.me/Equilibrium_Club_bot?start={}</code></p>'
            '</div>',
            total_invited,
            invited_with_payment,
            total_payments,
            obj.referral_code
        )
    get_referral_stats.short_description = "📊 Реферальная статистика"
    
    def get_balance_info(self, obj):
        """Информация о балансе с кнопками быстрого пополнения."""
        if not obj.pk:
            return "Сначала сохраните пользователя"
        
        balance = obj.balance or Decimal('0.00')
        
        return format_html(
            '''
            <div style="padding: 15px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; margin: 10px 0;">
                <h3 style="margin-top: 0; color: #417690;">Текущий баланс: <span style="color: #28a745; font-weight: bold; font-size: 1.2em;">${:.2f}</span></h3>
                <div style="margin-top: 15px;">
                    <p style="margin-bottom: 10px; font-weight: bold; color: #333;">💰 Быстрое пополнение:</p>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px;">
                        <button type="button" onclick="addBalanceQuick(10)" style="padding: 8px 15px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer; font-weight: bold; transition: all 0.2s;">+$10</button>
                        <button type="button" onclick="addBalanceQuick(50)" style="padding: 8px 15px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer; font-weight: bold; transition: all 0.2s;">+$50</button>
                        <button type="button" onclick="addBalanceQuick(100)" style="padding: 8px 15px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer; font-weight: bold; transition: all 0.2s;">+$100</button>
                        <button type="button" onclick="addBalanceQuick(500)" style="padding: 8px 15px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer; font-weight: bold; transition: all 0.2s;">+$500</button>
                        <button type="button" onclick="addBalanceQuick(1000)" style="padding: 8px 15px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer; font-weight: bold; transition: all 0.2s;">+$1000</button>
                    </div>
                    <div style="margin-top: 15px; display: flex; align-items: center; gap: 10px;">
                        <input type="number" id="balance_amount" placeholder="Введите сумму" step="0.01" min="0" style="padding: 8px; width: 200px; border: 1px solid #ddd; border-radius: 3px;">
                        <button type="button" onclick="addBalanceCustom()" style="padding: 8px 15px; background: #417690; color: white; border: none; border-radius: 3px; cursor: pointer; font-weight: bold; transition: all 0.2s;">Пополнить</button>
                    </div>
                </div>
                <p style="margin-top: 15px; font-size: 12px; color: #666; border-top: 1px solid #dee2e6; padding-top: 10px;">
                    💡 <strong>Инструкция:</strong> Нажмите на кнопку быстрого пополнения или введите сумму вручную. 
                    Баланс автоматически обновится в поле выше. Затем нажмите кнопку "Сохранить" внизу формы.
                </p>
            </div>
            <script>
                function addBalanceQuick(amount) {{
                    var balanceField = document.querySelector('#id_balance');
                    if (balanceField) {{
                        var currentBalance = parseFloat(balanceField.value) || 0;
                        var newBalance = (currentBalance + amount).toFixed(2);
                        balanceField.value = newBalance;
                        
                        // Визуальная обратная связь
                        balanceField.style.background = '#d4edda';
                        balanceField.style.border = '2px solid #28a745';
                        balanceField.style.transition = 'all 0.3s ease';
                        
                        setTimeout(function() {{
                            balanceField.style.background = '';
                            balanceField.style.border = '';
                        }}, 1000);
                        
                        // Показываем уведомление
                        showNotification('Баланс увеличен на $' + amount + '. Новый баланс: $' + newBalance);
                    }}
                }}
                
                function addBalanceCustom() {{
                    var amountInput = document.querySelector('#balance_amount');
                    var balanceField = document.querySelector('#id_balance');
                    
                    if (!amountInput || !balanceField) {{
                        alert('Ошибка: поле баланса не найдено');
                        return;
                    }}
                    
                    if (!amountInput.value || parseFloat(amountInput.value) <= 0) {{
                        alert('Пожалуйста, введите корректную сумму');
                        amountInput.focus();
                        return;
                    }}
                    
                    var amount = parseFloat(amountInput.value);
                    var currentBalance = parseFloat(balanceField.value) || 0;
                    var newBalance = (currentBalance + amount).toFixed(2);
                    balanceField.value = newBalance;
                    
                    // Визуальная обратная связь
                    balanceField.style.background = '#d4edda';
                    balanceField.style.border = '2px solid #28a745';
                    balanceField.style.transition = 'all 0.3s ease';
                    
                    setTimeout(function() {{
                        balanceField.style.background = '';
                        balanceField.style.border = '';
                    }}, 1000);
                    
                    // Очищаем поле ввода
                    amountInput.value = '';
                    
                    // Показываем уведомление
                    showNotification('Баланс увеличен на $' + amount.toFixed(2) + '. Новый баланс: $' + newBalance);
                }}
                
                function showNotification(message) {{
                    // Создаем элемент уведомления
                    var notification = document.createElement('div');
                    notification.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #28a745; color: white; padding: 15px 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); z-index: 9999; font-weight: bold;';
                    notification.textContent = message;
                    document.body.appendChild(notification);
                    
                    // Удаляем уведомление через 3 секунды
                    setTimeout(function() {{
                        notification.style.transition = 'opacity 0.5s ease';
                        notification.style.opacity = '0';
                        setTimeout(function() {{
                            document.body.removeChild(notification);
                        }}, 500);
                    }}, 3000);
                }}
            </script>
            ''',
            balance
        )
    get_balance_info.short_description = "💰 Управление балансом"
    
    def get_balance_history(self, obj):
        """История операций с балансом."""
        if not obj.pk:
            return "Сначала сохраните пользователя"
        
        # Получаем последние платежи пользователя
        payments = Payment.objects.filter(user=obj).order_by('-created_at')[:10]
        
        if not payments.exists():
            return format_html('<p style="color: #666;">Нет операций с балансом</p>')
        
        history_html = '<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">'
        history_html += '<thead><tr style="background: #f0f0f0;"><th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Дата</th><th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Тариф</th><th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Сумма</th><th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Статус</th></tr></thead><tbody>'
        
        for payment in payments:
            status_colors = {
                'COMPLETED': '#28a745',
                'PENDING': '#ffc107',
                'FAILED': '#dc3545',
                'CANCELLED': '#6c757d'
            }
            status_color = status_colors.get(payment.status, '#000')
            
            history_html += format_html(
                '<tr><td style="padding: 8px; border: 1px solid #ddd;">{}</td><td style="padding: 8px; border: 1px solid #ddd;">{}</td><td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">${:.2f}</td><td style="padding: 8px; border: 1px solid #ddd; color: {}; font-weight: bold;">{}</td></tr>',
                payment.created_at.strftime('%d.%m.%Y %H:%M'),
                payment.tariff.name if payment.tariff else '-',
                payment.amount,
                status_color,
                payment.get_status_display()
            )
        
        history_html += '</tbody></table>'
        return format_html(history_html)
    get_balance_history.short_description = "История платежей"
    
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
    
    def add_balance_direct_action(self, request, queryset):
        """Action для прямого пополнения баланса выбранных пользователей."""
        from django.http import HttpResponse
        from django.middleware.csrf import get_token
        
        # Проверяем, была ли отправлена форма
        if request.method == 'POST' and 'amount' in request.POST:
            amount = request.POST.get('amount')
            
            if not amount:
                self.message_user(request, "❌ Не указана сумма", level='error')
                return
            
            try:
                amount_decimal = Decimal(amount)
                
                updated_count = 0
                for user in queryset:
                    user.balance += amount_decimal
                    user.save()
                    updated_count += 1
                
                self.message_user(
                    request,
                    f"✅ Пополнен баланс {updated_count} пользователям на сумму ${amount_decimal}",
                    level='success'
                )
                from django.http import HttpResponseRedirect
                return HttpResponseRedirect(request.path)
            except Exception as e:
                self.message_user(request, f"❌ Ошибка: {e}", level='error')
                return
        
        # Отображаем форму ввода суммы
        csrf_token = get_token(request)
        user_ids = ','.join(str(u.id) for u in queryset)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Пополнение баланса</title>
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
                input[type="number"] {{
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
            <h2>💰 Пополнение баланса</h2>
            <p><strong>Выбрано пользователей: {queryset.count()}</strong></p>
            <form method="post" action="">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}" />
                <input type="hidden" name="action" value="add_balance_direct_action" />
                <input type="hidden" name="_selected_action" value="{user_ids}" />
                <label for="amount">Сумма пополнения баланса ($):</label>
                <input type="number" name="amount" id="amount" step="0.01" min="0" required />
                <div>
                    <input type="submit" class="button submit" value="Пополнить баланс" />
                    <a href="/admin/core/user/" class="button cancel">Отмена</a>
                </div>
            </form>
        </body>
        </html>
        """
        return HttpResponse(html)
    add_balance_direct_action.short_description = "💰 Пополнить баланс (напрямую)"
