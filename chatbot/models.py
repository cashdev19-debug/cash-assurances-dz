# chatbot/models.py
from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel
import json
from modelcluster.models import ClusterableModel
from wagtail.models import Orderable, TranslatableMixin
from modelcluster.fields import ParentalKey
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import threading
import uuid
import logging
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
logger = logging.getLogger(__name__)



class InsuranceTopic(TranslatableMixin, models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
    ]

    class Meta(TranslatableMixin.Meta):
        unique_together = [("translation_key", "locale")]
        verbose_name = "Insurance Topic"
        verbose_name_plural = "Insurance Topics"

    def __str__(self):
        return f"{self.name} ({self.locale.language_code})"


class InsuranceQALink(Orderable):
    qa = ParentalKey(
        "chatbot.InsuranceQA",
        on_delete=models.CASCADE,
        related_name="links",
    )
    label = models.CharField(max_length=80, help_text="Button text, e.g. 'Get a quote'")
    url = models.CharField(
        max_length=500,
        help_text="Absolute path (/quote/) or full URL (https://...)",
    )
    open_new_tab = models.BooleanField(default=False)

    panels = [
        FieldPanel("label"),
        FieldPanel("url"),
        FieldPanel("open_new_tab"),
    ]

    def clean(self):
        super().clean()
        if not self.url:
            return
        parsed = urlparse(self.url)
        if parsed.scheme and parsed.scheme not in ("http", "https"):
            raise ValidationError({"url": "Only http(s) or relative URLs allowed."})


class InsuranceQAQuestionVariant(Orderable):
    """Allows adding multiple alternative ways of asking the same question."""
    qa = ParentalKey(
        "chatbot.InsuranceQA",
        on_delete=models.CASCADE,
        related_name="question_variants",
    )
    variant_question = models.CharField(
        max_length=300,
        help_text="Alternative phrasing, e.g. 'How much does full coverage cost?'",
    )

    panels = [
        FieldPanel("variant_question"),
    ]

    def __str__(self):
        return self.variant_question



class InsuranceQA(TranslatableMixin, ClusterableModel):
    """A translatable question/answer pair supporting multiple alternative phrasings."""
    topic = models.ForeignKey(
        InsuranceTopic,
        on_delete=models.CASCADE,
        related_name="qas",
        null=True,
        blank=True,
    )
    question = models.CharField(
        max_length=300,
        help_text="Canonical question, e.g. 'What does full coverage include?'",
    )
    answer = models.TextField(
        help_text="The chatbot's reply. Keep it concise (2–4 sentences)."
    )
    keywords = models.TextField(
        help_text="Comma-separated trigger words, e.g. 'full coverage, comprehensive, collision'"
    )
    priority = models.PositiveSmallIntegerField(
        default=0,
        help_text="Higher = shown first when scores tie.",
    )
    is_active = models.BooleanField(default=True)
    is_starter = models.BooleanField(
        default=False,
        help_text="Show this question in the first-use suggestion list.",
    )
    _embedding = models.TextField(
        blank=True,
        default="",
        help_text="Cached embedding (JSON). Auto-generated.",
    )
    needs_embedding = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Set automatically. True when embedding is stale.",
    )

    panels = [
        FieldPanel("topic"),
        FieldPanel("question"),
        InlinePanel("question_variants", label="Alternative Question Phrasings"),
        FieldPanel("answer"),
        FieldPanel("keywords"),
        FieldPanel("priority"),
        FieldPanel("is_active"),
        FieldPanel("is_starter"),
        InlinePanel("links", label="Action links"),
    ]

    class Meta(TranslatableMixin.Meta):
        unique_together = [("translation_key", "locale")]
        ordering = ["-priority", "question"]

    def __str__(self):
        return f"{self.question} [{self.locale.language_code.upper()}]"

    @property
    def keyword_list(self):
        return [k.strip().lower() for k in self.keywords.split(",") if k.strip()]

    def get_embedding(self):
        if not self._embedding:
            return None
        try:
            return json.loads(self._embedding)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Corrupt embedding for QA %s, ignoring.", self.pk)
            return None

    def save(self, *args, **kwargs):
        self.needs_embedding = True
        super().save(*args, **kwargs)
        if self.pk:
            _schedule_embedding(self.pk)


# -------------------------------------------------------------------
# Background embedding worker
# -------------------------------------------------------------------
def _schedule_embedding(qa_pk: int):
    t = threading.Thread(
        target=_compute_embedding_job,
        args=(qa_pk,),
        daemon=True,
        name=f"embed-qa-{qa_pk}",
    )
    t.start()


def _compute_embedding_job(qa_pk: int):
    from django.db import close_old_connections
    close_old_connections()
    try:
        from .matcher import compute_embedding
        qa = InsuranceQA.objects.get(pk=qa_pk)
        
        # Combine canonical question, all alternative variants, and keywords for a rich semantic vector
        variants_text = " ".join([v.variant_question for v in qa.question_variants.all()])
        text = f"{qa.question} {variants_text} {' '.join(qa.keyword_list)}"
        
        vec = compute_embedding(text)
        InsuranceQA.objects.filter(pk=qa_pk).update(
            _embedding=json.dumps(vec),
            needs_embedding=False,
        )
        logger.info("Embedding computed for QA %s", qa_pk)
    except Exception as e:
        logger.exception("Embedding job failed for QA %s: %s", qa_pk, e)
    finally:
        close_old_connections()



    from django.utils.html import format_html
from django.contrib import admin

class ChatSession(ClusterableModel):  # Changed from models.Model to ClusterableModel
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    user_agent = models.CharField(max_length=300, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    panels = [
        FieldPanel("user",read_only=True),
        FieldPanel("is_closed",read_only=True),
        FieldPanel("ip_address",read_only=True),
        FieldPanel("user_agent",read_only=True),
        # This renders the full message history directly inside the session edit view!
        InlinePanel("messages", label="Chat Transcript Messages"),
    ]

    class Meta:
        ordering = ["-last_seen_at"]

    def __str__(self):
        return f"Session {self.id}"

    @admin.display(description="Messages Count")
    def message_count(self):
        return self.messages.count()


class ChatMessage(Orderable):  # Inherit from Orderable so InlinePanel works cleanly
    ROLE_CHOICES = [("user", "User"), ("bot", "Bot")]

    session = ParentalKey( 
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=8, choices=ROLE_CHOICES)
    text = models.TextField()
    matched_qa = models.ForeignKey(
        InsuranceQA, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("role",read_only=True),
        FieldPanel("text",read_only=True),
        FieldPanel("confidence",read_only=True),
        FieldPanel("matched_qa",read_only=True),
    ]

    class Meta:
        ordering = ["created_at"]
        
