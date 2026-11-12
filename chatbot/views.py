# chatbot/views.py
import json
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .matcher import find_best_answer, get_suggestions
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
    session = _get_or_create_session(request)
    if _rate_limit_exceeded(session):
        resp = JsonResponse(
            {"reply": RATE_LIMIT_MESSAGES[locale], "error": True, "locale": locale},
            status=429,
        )
        return _set_session_cookie(resp, session)
    prev = (
        session.messages.filter(role="user").order_by("-created_at").first()
    )
    previous_text = prev.text if prev else None

    ChatMessage.objects.create(session=session, role="user", text=message)

    # 5. Find the best answer in the user's language
    qa, score, debug = find_best_answer(
        message,
        previous_text=previous_text,
        locale=locale,
    )

    if qa is None:
        reply_text = FALLBACKS[locale]
        links = []
    else:
        reply_text = qa.answer
        links = [
            {"label": l.label, "url": l.url, "new_tab": l.open_new_tab}
            for l in qa.links.all()
        ]

    # 6. Log the bot response
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
            "matched": qa is not None,
            "locale": locale,
            "suggestions": get_suggestions(locale=locale) if qa is None else [],
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