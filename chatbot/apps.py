from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chatbot"

    def ready(self):
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