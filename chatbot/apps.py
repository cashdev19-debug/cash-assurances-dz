import os
import sys
import threading

from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chatbot"

    def ready(self):
        # --- register signals (keeps the matcher index in sync with Wagtail edits)
        from . import signals  # noqa: F401

        # --- your existing wagtail_localize patch (unchanged)
        from wagtail_localize.models import (
            Translation, StringSegment, StringTranslation,
        )
        def get_progress(self):
            segments = list(
                StringSegment.objects.filter(source_id=self.source_id)
                .values_list("string_id", "context_id")
            )
            done = set(
                StringTranslation.objects.filter(
                    locale_id=self.target_locale_id,
                    translation_of_id__in={s for s, _ in segments},
                ).values_list("translation_of_id", "context_id")
            )
            # a translation with context=None applies to any context
            done_any = {s for s, c in done if c is None}
            translated = sum(
                1 for s, c in segments if (s, c) in done or s in done_any
            )
            return len(segments), translated

        Translation.get_progress = get_progress

        # --- warm up the embedding model + index so the first user doesn't wait
        if self._should_warmup():
            threading.Thread(target=self._warmup, daemon=True, name="chatbot-warmup").start()

    @staticmethod
    def _should_warmup() -> bool:
        """Only when actually serving requests (not migrate, shell, tests, collectstatic...)."""
        argv = " ".join(sys.argv)
        if "runserver" in argv:
            # the autoreloader starts two processes; warm up only the serving one
            return os.environ.get("RUN_MAIN") == "true" or "--noreload" in argv
        return any(s in argv for s in ("gunicorn", "uwsgi", "daphne", "uvicorn"))

    @staticmethod
    def _warmup():
        from django.db import connection
        from .matcher import warmup
        try:
            warmup()  # logs its own errors
        finally:
            connection.close()