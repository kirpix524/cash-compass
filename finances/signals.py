# finances/signals.py

from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from .models import Transaction, Wallet

@receiver(post_save, sender=Transaction)
def adjust_balance_on_save(sender, instance: Transaction, created, **kwargs):
    """
    Когда транзакция создаётся или обновляется,
    корректируем баланс кошелька на дельту.
    """
    # вычисляем дельту: если это обновление, то old_amount уже сохранён в _old_amount
    delta = instance.amount
    if not created and hasattr(instance, '_old_amount'):
        delta = instance.amount - instance._old_amount

    with transaction.atomic():
        Wallet.objects.filter(pk=instance.wallet_id).update(
            current_balance=F('current_balance') + delta
        )

@receiver(pre_save, sender=Transaction)
def store_old_amount(sender, instance: Transaction, **kwargs):
    """
    Перед сохранением сохраняем старое значение amount,
    чтобы на post_save понять, насколько изменился amount.
    """
    if instance.pk:
        old = Transaction.objects.get(pk=instance.pk)
        instance._old_amount = old.amount

@receiver(pre_delete, sender=Transaction)
def adjust_balance_on_delete(sender, instance: Transaction, **kwargs):
    """
    При удалении транзакции отнимаем её сумму от баланса.
    """
    with transaction.atomic():
        Wallet.objects.filter(pk=instance.wallet_id).update(
            current_balance=F('current_balance') - instance.amount
        )
