
from __future__ import annotations

import logging
import re
import threading
import time
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
from django.core.cache import cache

from .models import InsuranceQA

logger = logging.getLogger(__name__)

try:  # much faster than difflib; pip install rapidfuzz
    from rapidfuzz import fuzz

    def _ratio(a: str, b: str) -> float:
        return fuzz.ratio(a, b) / 100.0

    def _partial(a: str, b: str) -> float:
        return fuzz.partial_ratio(a, b) / 100.0

except ImportError:  # graceful fallback
    from difflib import SequenceMatcher

    def _ratio(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    def _partial(a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        short, long_ = (a, b) if len(a) <= len(b) else (b, a)
        if short in long_:
            return 1.0
        n = len(short)
        return max(
            SequenceMatcher(None, short, long_[i:i + n]).ratio()
            for i in range(0, max(1, len(long_) - n + 1))
        )


# --------------------------------------------------------------------------- #
# Configuration - calibrate with evaluate() on real questions!
# --------------------------------------------------------------------------- #
MODEL_PATH = str(Path(__file__).resolve().parent / "paraphrase-multilingual-MiniLM-L12-v2")

TOP_K = 8                  # candidates kept after semantic search
SEM_WEIGHT = 0.70
KW_WEIGHT = 0.30
THRESHOLD = 0.40           # minimum combined score to answer
MIN_SEMANTIC = 0.35        # weak semantic match is rejected...
KEYWORD_RESCUE = 0.50      # ...unless keywords are at least this strong
AMBIGUITY_MARGIN = 0.04    # best - runner_up below this => "ambiguous"
SHORT_MESSAGE_WORDS = 4    # short messages may be follow-ups
CONFIDENT_SCORE = 0.60     # a standalone message this good is never merged with context
CONTEXT_GAIN = 0.05        # merged query must beat the raw one by this much
MIN_SUGGEST_SEM = 0.30     # near-miss questions below this are not suggested


# --------------------------------------------------------------------------- #
# Embedding model
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_PATH)


def compute_embedding(text: str) -> list[float]:
    """Public API used by models.py (must stay JSON-serializable)."""
    return get_model().encode(text, normalize_embeddings=True).tolist()


@lru_cache(maxsize=512)
def _embed_query(text: str) -> np.ndarray:
    return np.asarray(get_model().encode(text, normalize_embeddings=True), dtype=np.float32)


# --------------------------------------------------------------------------- #
# Text normalization
# --------------------------------------------------------------------------- #
# Negations ("not", "pas", "لا") are intentionally NOT stopwords.
STOPWORDS = {
    # English
    "the", "a", "an", "is", "are", "do", "does", "i", "you", "my", "your",
    "what", "how", "can", "to", "of", "for", "in", "on", "and", "or", "it",
    "me", "we", "with", "about", "tell", "please", "hi", "hello", "hey",
    # French
    "le", "la", "les", "un", "une", "des", "et", "ou", "de", "du", "au", "aux",
    "a", "en", "pour", "que", "qui", "ce", "cette", "mon", "ma", "mes", "ton", "son",
    "je", "tu", "il", "elle", "nous", "vous", "sur", "dans", "par",
    "comment", "quel", "quelle", "quels", "est", "sont", "bonjour", "salut", "bonsoir",
    # Arabic (already normalized: no hamza, ة->ه, ى->ي)
    "في", "من", "على", "عن", "الى", "ان", "الذي", "التي", "هذا", "هذه",
    "كيف", "ما", "هل", "انا", "انت", "مرحبا", "السلام", "عليكم", "هو", "هي",
}

_AR_ALEF = re.compile(r"[أإآٱ]")
_AR_PREFIX = re.compile(r"^(وال|بال|كال|فال|لل|ال)")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_SPACES = re.compile(r"\s+")
_AR_CHAR = re.compile(r"[\u0600-\u06FF]")


def normalize(text: str) -> str:
    """Lowercase, strip accents/diacritics, unify Arabic letter variants, drop punctuation."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))  # é->e, harakat removed
    text = text.replace("\u0640", "")                                 # tatweel
    text = _AR_ALEF.sub("ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه")
    text = _PUNCT.sub(" ", text)
    return _SPACES.sub(" ", text).strip()


def _strip_prefix(token: str) -> str:
    """Strip Arabic prefixes (ال, وال, بال...) keeping a root of 3+ letters."""
    stripped = _AR_PREFIX.sub("", token)
    return stripped if len(stripped) >= 3 else token


def tokenize(text: str) -> list[str]:
    return [
        _strip_prefix(t)
        for t in normalize(text).split()
        if len(t) > 1 and t not in STOPWORDS
    ]


def resolve_locale(message: str, locale: str) -> str:
    """If the user writes mostly Arabic script, answer in Arabic whatever the UI language."""
    letters = [c for c in message if c.isalpha()]
    if letters and sum(1 for c in letters if _AR_CHAR.match(c)) / len(letters) > 0.5:
        return "ar"
    return locale


# --------------------------------------------------------------------------- #
# Smalltalk
# --------------------------------------------------------------------------- #
_SMALLTALK = {
    "greeting": [
        "hi", "hello", "hey", "good morning", "good evening",
        "bonjour", "salut", "bonsoir", "coucou",
        "مرحبا", "اهلا", "اهلا وسهلا", "السلام عليكم", "سلام", "صباح الخير", "مساء الخير",
    ],
    "thanks": [
        "thanks", "thank you", "thx", "ok thanks", "merci", "merci beaucoup", "ok merci",
        "شكرا", "شكرا جزيلا", "بارك الله فيك", "جزاك الله خيرا",
    ],
    "bye": ["bye", "goodbye", "see you", "au revoir", "a bientot", "مع السلامه", "الى اللقاء"],
}
_SMALLTALK_NORM = {i: {normalize(p) for p in ps} for i, ps in _SMALLTALK.items()}


def detect_smalltalk(text: str) -> str | None:
    norm = normalize(text)
    for intent, phrases in _SMALLTALK_NORM.items():
        if norm in phrases:
            return intent
    return None


# --------------------------------------------------------------------------- #
# In-memory semantic index
# --------------------------------------------------------------------------- #
_VERSION_KEY = "chatbot_index_version"


@dataclass
class _Index:
    version: object
    qa_ids: list
    row_qa_idx: np.ndarray   # row -> position in qa_ids
    matrix: np.ndarray       # (rows, dim) normalized vectors
    langs: np.ndarray        # per QA language code


_index: _Index | None = None
_index_lock = threading.Lock()
_vec_cache: dict[str, np.ndarray] = {}   # text -> vector, so rebuilds only encode new texts


def invalidate_index() -> None:
    global _index
    try:
        cache.set(_VERSION_KEY, time.time(), None)
    except Exception:
        logger.exception("Could not bump chatbot index version")
    _index = None


def _encode_cached(texts: list[str]) -> list[np.ndarray]:
    missing = [t for t in dict.fromkeys(texts) if t not in _vec_cache]
    if missing:
        encoded = get_model().encode(missing, normalize_embeddings=True, batch_size=32)
        for t, v in zip(missing, encoded):
            _vec_cache[t] = np.asarray(v, dtype=np.float32)
    return [_vec_cache[t] for t in texts]


def _build_index(version) -> _Index:
    global _vec_cache
    qs = (
        InsuranceQA.objects.filter(is_active=True)
        .select_related("locale")
        .prefetch_related("question_variants")
    )
    qa_ids, langs, texts, row_qa = [], [], [], []
    for qa in qs:
        pos = len(qa_ids)
        qa_ids.append(qa.id)
        langs.append(qa.locale.language_code if qa.locale_id else None)
        for t in [qa.question] + [v.variant_question for v in qa.question_variants.all()]:
            t = (t or "").strip()
            if t:
                texts.append(t)
                row_qa.append(pos)

    if texts:
        matrix = np.vstack(_encode_cached(texts))
        _vec_cache = {t: _vec_cache[t] for t in set(texts)}  # drop stale texts
    else:
        dim = get_model().get_sentence_embedding_dimension()
        matrix = np.zeros((0, dim), dtype=np.float32)

    return _Index(
        version=version,
        qa_ids=qa_ids,
        row_qa_idx=np.asarray(row_qa, dtype=np.int64),
        matrix=matrix,
        langs=np.asarray(langs, dtype=object),
    )


def get_index() -> _Index:
    global _index
    try:
        version = cache.get(_VERSION_KEY)
    except Exception:
        version = None
    idx = _index
    if idx is not None and idx.version == version:
        return idx
    with _index_lock:
        if _index is None or _index.version != version:
            _index = _build_index(version)
        return _index


def warmup() -> None:
    """Load the model and build the index (call at startup, in a thread)."""
    try:
        _embed_query("warmup")
        get_index()
    except Exception:
        logger.exception("Chatbot warmup failed")


def semantic_search(query: str, locale: str | None, k: int = TOP_K) -> list[tuple[int, float]]:
    """[(qa_id, cosine)] best-first. Max over the question and all its variants."""
    idx = get_index()
    if idx.matrix.shape[0] == 0:
        return []

    sims = idx.matrix @ _embed_query(query)
    best = np.full(len(idx.qa_ids), -1.0, dtype=np.float32)
    np.maximum.at(best, idx.row_qa_idx, sims)

    if locale:
        mask = idx.langs == locale
        if mask.any():  # if nothing exists in this language, search everything
            best = np.where(mask, best, -1.0)

    order = np.argsort(-best)[:k]
    return [(idx.qa_ids[i], max(0.0, float(best[i]))) for i in order if best[i] > -0.999]


# --------------------------------------------------------------------------- #
# Keyword / fuzzy scoring (top-K candidates only)
# --------------------------------------------------------------------------- #
def fuzzy_token_match(word: str, token_list: list[str], cutoff: float = 0.8) -> bool:
    if word in token_list:
        return True
    if len(word) < 4:
        return False
    return any(len(t) >= 4 and _ratio(word, t) >= cutoff for t in token_list)


def keyword_score(user_tokens: list[str], user_text: str, qa: InsuranceQA) -> float:
    """0..1 = 60% declared keywords + 40% token overlap with the best question/variant."""
    points = 0.0
    for kw in qa.keyword_list:
        kw_norm = normalize(kw)
        if not kw_norm:
            continue
        if " " in kw_norm:
            if kw_norm in user_text:
                points += 1.0
            elif _partial(kw_norm, user_text) >= 0.85:
                points += 0.8
        elif fuzzy_token_match(_strip_prefix(kw_norm), user_tokens, 0.8):
            points += 1.0
    kw_part = min(points / 3.0, 1.0)  # 3 keyword hits = full score

    best_overlap = 0.0
    for q in [qa.question] + [v.variant_question for v in qa.question_variants.all()]:
        q_tokens = tokenize(q)
        if q_tokens:
            hits = sum(1 for t in q_tokens if fuzzy_token_match(t, user_tokens))
            best_overlap = max(best_overlap, hits / len(q_tokens))

    return 0.6 * kw_part + 0.4 * best_overlap


# --------------------------------------------------------------------------- #
# Ranking and decision
# --------------------------------------------------------------------------- #
@dataclass
class Match:
    qa: InsuranceQA
    score: float
    semantic: float
    keyword: float


def _rank(query: str, locale: str | None) -> list[Match]:
    user_text = normalize(query)
    user_tokens = tokenize(query)
    if not user_text or (not user_tokens and len(user_text) < 2):
        return []

    hits = semantic_search(query.strip(), locale)
    if not hits:
        return []

    sem_by_id = dict(hits)
    qas = {
        qa.id: qa
        for qa in InsuranceQA.objects.filter(id__in=sem_by_id)
        .select_related("topic", "locale")
        .prefetch_related("question_variants", "links")
    }

    matches = []
    for qa_id, sem in hits:
        qa = qas.get(qa_id)
        if qa is None:
            continue
        kw = keyword_score(user_tokens, user_text, qa)
        # priority is only a tie-breaker (max +0.02)
        score = SEM_WEIGHT * sem + KW_WEIGHT * kw + min(qa.priority, 10) * 0.002
        matches.append(Match(qa, score, sem, kw))

    matches.sort(key=lambda m: m.score, reverse=True)
    return matches


def _alt(m: Match) -> dict:
    return {
        "id": m.qa.id,
        "question": m.qa.question,
        "topic": m.qa.topic.name if m.qa.topic else None,
        "score": round(m.score, 3),
    }


def find_best_answer(
    user_message: str,
    previous_text: str | None = None,
    locale: str | None = None,
    threshold: float = THRESHOLD,
):
    """Returns (qa | None, score, debug). debug["status"] in ok/ambiguous/no_match/smalltalk."""
    intent = detect_smalltalk(user_message)
    if intent:
        return None, 0.0, {"status": "smalltalk", "intent": intent}

    ranked = _rank(user_message, locale)

    # Follow-up ("and the price?"): try with context, keep it only if clearly better.
    used_context = False
    raw_best = ranked[0].score if ranked else 0.0
    if (
        previous_text
        and len(user_message.split()) <= SHORT_MESSAGE_WORDS
        and raw_best < CONFIDENT_SCORE
    ):
        with_ctx = _rank(f"{previous_text} {user_message}", locale)
        if with_ctx and with_ctx[0].score > raw_best + CONTEXT_GAIN:
            ranked, used_context = with_ctx, True

    if not ranked:
        return None, 0.0, {"status": "no_match", "alternatives": []}

    best = ranked[0]
    runner = ranked[1] if len(ranked) > 1 else None
    margin = best.score - runner.score if runner else 1.0

    debug = {
        "status": "ok",
        "semantic": round(best.semantic, 3),
        "keyword": round(best.keyword, 3),
        "margin": round(margin, 3),
        "used_context": used_context,
        "alternatives": [],
    }

    weak = best.semantic < MIN_SEMANTIC and best.keyword < KEYWORD_RESCUE
    if best.score < threshold or weak:
        debug["status"] = "no_match"
        debug["alternatives"] = [_alt(m) for m in ranked[:3] if m.semantic >= MIN_SUGGEST_SEM]
        return None, best.score, debug

    if runner and margin < AMBIGUITY_MARGIN and runner.score >= threshold:
        debug["status"] = "ambiguous"
        debug["alternatives"] = [_alt(m) for m in ranked[1:4] if m.score >= threshold]
    return best.qa, best.score, debug


# --------------------------------------------------------------------------- #
# Suggestions
# --------------------------------------------------------------------------- #
def get_suggestions(limit: int = 6, starters_only: bool = True, locale: str | None = None):
    qs = InsuranceQA.objects.filter(is_active=True)
    if locale:
        qs = qs.filter(locale__language_code=locale)
    if starters_only:
        qs = qs.filter(is_starter=True)
    qs = qs.select_related("topic", "locale").order_by("-priority")[:limit]
    return [
        {"question": qa.question, "topic": qa.topic.name if qa.topic else None}
        for qa in qs
    ]


# --------------------------------------------------------------------------- #
# Calibration helper (run in `python manage.py shell`)
# --------------------------------------------------------------------------- #
def evaluate(cases: list[tuple[str, int | None]], locale: str | None = None) -> dict:
    """
    cases = [("comment résilier mon contrat", 12), ("recette de pizza", None), ...]
    expected id None means "must NOT answer". Prints failures, returns stats.
    """
    ok = 0
    for query, expected in cases:
        qa, score, dbg = find_best_answer(query, locale=locale)
        got = qa.id if qa else None
        if got == expected:
            ok += 1
        else:
            print(f"FAIL {query!r}: expected {expected}, got {got} "
                  f"(score={score:.2f}, {dbg.get('status')}, sem={dbg.get('semantic')}, "
                  f"kw={dbg.get('keyword')}, margin={dbg.get('margin')})")
    total = len(cases) or 1
    print(f"accuracy: {ok}/{len(cases)} = {ok / total:.0%}")
    return {"correct": ok, "total": len(cases)}