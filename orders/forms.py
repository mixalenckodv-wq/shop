from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):
    """Форма оформления заказа. Обязательные поля минимальны."""

    class Meta:
        model = Order
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "comment",
            "telegram_chat_id",
        )
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "comment": forms.Textarea(attrs={"rows": 2}),
            "telegram_chat_id": forms.TextInput(
                attrs={"placeholder": "Необязательно — для статусов в Telegram"}
            ),
        }
        labels = {
            "telegram_chat_id": "Telegram chat_id (необязательно)",
        }
        help_texts = {
            "telegram_chat_id": "Узнать свой chat_id можно, отправив боту команду /start.",
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = [c for c in phone if c.isdigit()]
        if len(digits) < 6:
            raise forms.ValidationError("Введите корректный номер телефона.")
        return phone
