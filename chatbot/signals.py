from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .matcher import invalidate_index
from .models import InsuranceQA, InsuranceQAQuestionVariant


@receiver([post_save, post_delete], sender=InsuranceQA)
@receiver([post_save, post_delete], sender=InsuranceQAQuestionVariant)
def qa_changed(sender, **kwargs):
    # run after the DB transaction commits, so the rebuilt index sees the final data
    transaction.on_commit(invalidate_index)