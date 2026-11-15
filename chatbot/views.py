# chatbot/views.py
import json
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .matcher import find_best_answer, get_suggestions, resolve_locale
from .models import ChatMessage, ChatSession

SUPPORTED_LOCALES = ("fr", "ar", "en")
DEFAULT_LOCALE = "fr"
FALLBACKS = {
    "fr": (
        "Je ne suis pas sûr de comprendre. Je peux vous aider sur les produits, "
        "garanties, sinistres et tarifs. Reformulez ou contactez notre équipe."
    ),
    "ar": (
        "لست متأكداً من فهمي لسؤالك. يمكنني مساعدتك بخصوص المنتجات والضمانات "
        "والتعويضات والأسعار. حاول إعادة الصياغة أو تواصل مع فريقنا."
    ),
    "en": (
        "I'm not sure about that. I can help with products, coverage, claims "
        "and pricing. Try rephrasing, or contact our team."
    ),
}

SMALLTALK = {
    "greeting": {
        "fr": "Bonjour ! Comment puis-je vous aider avec vos questions d'assurance ?",
        "ar": "مرحباً! كيف يمكنني مساعدتك في أسئلة التأمين؟",
        "en": "Hello! How can I help you with your insurance questions?",
    },
    "thanks": {
        "fr": "Avec plaisir ! N'hésitez pas si vous avez d'autres questions.",
        "ar": "على الرحب والسعة! لا تتردد في طرح أي سؤال آخر.",
        "en": "You're welcome! Let me know if you have any other question.",
    },
    "bye": {
        "fr": "Au revoir ! Bonne journée.",
        "ar": "مع السلامة! أتمنى لك يوماً سعيداً.",
        "en": "Goodbye! Have a great day.",
    },
}

RATE_LIMIT_MESSAGES = {
    "fr": "Trop de messages. Veuillez réessayer plus tard.",
    "ar": "رسائل كثيرة جداً. يرجى المحاولة لاحقاً.",
    "en": "Too many messages. Please try again later.",
}
INVALID_MESSAGES = {
    "fr": "Requête invalide.",
    "ar": "طلب غير صالح.",
    "en": "Invalid request.",
}

RATE_LIMIT = 60          # messages per hour per session
SESSION_TTL_HOURS = 24   # reuse session if seen within this window
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days


def _get_locale(request, lang=None):
    code = lang or getattr(request, "LANGUAGE_CODE", "") or DEFAULT_LOCALE
    code = str(code).lower().replace("_", "-").split("-")[0]
    return code if code in SUPPORTED_LOCALES else DEFAULT_LOCALE


def _get_or_create_session(request):
    sid = request.COOKIES.get("chat_session")
    session = None

    if sid:
        try:
            session = ChatSession.objects.get(id=sid)
            if session.last_seen_at < timezone.now() - timedelta(hours=SESSION_TTL_HOURS):
                session = None
            else:
                # last_seen_at is auto_now but only updates on save(): without this the
                # session expired 24h after creation even for active users.
                session.save(update_fields=["last_seen_at"])
        except (ChatSession.DoesNotExist, ValueError):
            session = None

    if session is None:
        session = ChatSession.objects.create(
            user=request.user if request.user.is_authenticated else None,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
            ip_address=request.META.get("REMOTE_ADDR") or None,
        )
    return session


def _rate_limit_exceeded(session):
    key = f"chat_rl_{session.id}"
    count = cache.get(key, 0)
    if count >= RATE_LIMIT:
        return True
    cache.set(key, count + 1, 3600)
    return False


def _set_session_cookie(response, session):
    response.set_cookie(
        "chat_session",
        str(session.id),
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="Lax",
    )
    return response


def _alternatives(debug, limit=3):
    """'Did you mean...' questions found by the matcher, in the suggestions format."""
    return [
        {"question": a["question"], "topic": a.get("topic")}
        for a in (debug.get("alternatives") or [])[:limit]
    ]


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------
@require_POST
@csrf_protect
def chat_api(request):
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError("body must be a JSON object")
        message = (data.get("message") or "").strip()[:500]
    except (json.JSONDecodeError, ValueError, AttributeError):
        locale = _get_locale(request)
        return JsonResponse(
            {"reply": INVALID_MESSAGES[locale], "error": True}, status=400
        )
    locale = _get_locale(request, data.get("lang"))
    if not message:
        return JsonResponse(
            {"reply": FALLBACKS[locale], "error": True, "locale": locale}, status=400
        )
    # Arabic message on a French/English page -> answer in Arabic
    locale = resolve_locale(message, locale)

    session = _get_or_create_session(request)
    if _rate_limit_exceeded(session):
        resp = JsonResponse(
            {"reply": RATE_LIMIT_MESSAGES[locale], "error": True, "locale": locale},
            status=429,
        )
        return _set_session_cookie(resp, session)

    prev = session.messages.filter(role="user").order_by("-created_at").first()
    previous_text = prev.text if prev else None

    ChatMessage.objects.create(session=session, role="user", text=message)

    qa, score, debug = find_best_answer(
        message,
        previous_text=previous_text,
        locale=locale,
    )
    status = (debug or {}).get("status")
    suggestions = []
    links = []

    if status == "smalltalk":
        intent = debug["intent"]
        reply_text = SMALLTALK[intent][locale]
        if intent == "greeting":
            suggestions = get_suggestions(locale=locale)
    elif qa is None:
        reply_text = FALLBACKS[locale]
        # near-miss questions first, starter questions as a last resort
        suggestions = _alternatives(debug) or get_suggestions(locale=locale)
    else:
        reply_text = qa.answer
        links = [
            {"label": l.label, "url": l.url, "new_tab": l.open_new_tab}
            for l in qa.links.all()
        ]
        if status == "ambiguous":
            suggestions = _alternatives(debug)

    ChatMessage.objects.create(
        session=session,
        role="bot",
        text=reply_text,
        matched_qa=qa,
        confidence=score if qa else None,
    )

    debug = dict(debug or {})
    debug["locale"] = locale

    resp = JsonResponse(
        {
            "reply": reply_text,
            "links": links,
            "topic": qa.topic.name if qa and qa.topic else None,
            "matched_question": qa.question if qa else None,
            "confidence": round(score, 2),
            "matched": qa is not None or status == "smalltalk",
            "ambiguous": status == "ambiguous",
            "locale": locale,
            "suggestions": suggestions,
            "session_id": str(session.id),
            "debug": debug if settings.DEBUG else None,
        }
    )
    return _set_session_cookie(resp, session)


@require_GET
@ensure_csrf_cookie
def history_api(request):
    sid = request.COOKIES.get("chat_session")
    if not sid:
        return JsonResponse({"messages": []})
    try:
        session = ChatSession.objects.get(id=sid)
    except (ChatSession.DoesNotExist, ValueError):
        return JsonResponse({"messages": []})
    msgs = [
        {"role": m.role, "text": m.text, "at": m.created_at.isoformat()}
        for m in session.messages.all()[:100]
    ]
    return JsonResponse({"messages": msgs, "session_id": str(session.id)})


@require_GET
def suggestions_api(request):
    locale = _get_locale(request, request.GET.get("lang"))
    return JsonResponse(
        {"suggestions": get_suggestions(locale=locale), "locale": locale}
    )