import re
from difflib import SequenceMatcher
from .models import InsuranceQA
from functools import lru_cache
from pathlib import Path
import numpy as np

MODEL_PATH = Path(__file__).resolve().parent / "paraphrase-multilingual-MiniLM-L12-v2"
MODEL_PATH = str(MODEL_PATH)

@lru_cache(maxsize=1)
def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_PATH)

def compute_embedding(text: str) -> list[float]:
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()

def semantic_score(user_text: str, qa: InsuranceQA) -> float:
    qa_vec = qa.get_embedding()
    if not qa_vec:
        return 0.0
    user_vec = compute_embedding(user_text)
    return float(np.dot(user_vec, qa_vec))

STOPWORDS = {
    # English
    "the", "a", "an", "is", "are", "do", "does", "i", "you", "my", "your",
    "what", "how", "can", "to", "of", "for", "in", "on", "and", "or", "it",
    "me", "we", "with", "about", "tell", "please", "hi", "hello",
    # French
    "le", "la", "les", "un", "une", "des", "et", "ou", "de", "du",
    "à", "en", "pour", "que", "qui", "ce", "cette", "mon", "ton", "son",
    "comment", "quel", "quelle", "est", "sont", "bonjour", "salut",
    # Arabic
    "في", "من", "على", "عن", "إلى", "أن", "الذي", "التي", "هذا", "هذه",
    "كيف", "ما", "هل", "أنا", "انت", "مرحبا", "السلام", "هو", "هي", "لا"
}

def normalize(text: str) -> str:
    text = text.lower()
    # 1. Remove Arabic diacritics (Harakat) and Tatweel
    text = re.sub(r'[\u064b-\u0652\u0640]', '', text)
    # 2. Normalize Arabic Alef variants to standard 'ا'
    text = re.sub(r'[أإآ]', 'ا', text)
    # 3. Normalize Teh Marbuta to Heh if common, or keep. Let's clean punctuation:
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()

def tokenize(text: str) -> list[str]:
    return [t for t in normalize(text).split() if t not in STOPWORDS and len(t) > 1]

def fuzzy_token_match(word: str, token_list: list[str], cutoff: float = 0.8) -> bool:
    if word in token_list:
        return True
    for token in token_list:
        if len(word) >= 4 and len(token) >= 4:
            if SequenceMatcher(None, word, token).ratio() >= cutoff:
                return True
    return False

def score_qa(user_tokens: list[str], user_text: str, qa: InsuranceQA) -> float:
    all_questions = [qa.question] + [v.variant_question for v in qa.question_variants.all()]
    best_qa_score = 0.0

    for q_text in all_questions:
        score = 0.0
        q_norm = normalize(q_text)
        
        for kw in qa.keyword_list:
            kw_norm = normalize(kw)
            if " " in kw_norm: 
                if kw_norm in user_text or SequenceMatcher(None, kw_norm, user_text).ratio() > 0.75:
                    score += 3.0
            else:
                if fuzzy_token_match(kw_norm, user_tokens, cutoff=0.78):
                    score += 2.0

        q_tokens = tokenize(q_text)
        fuzzy_overlap_count = sum(1 for q_t in q_tokens if fuzzy_token_match(q_t, user_tokens, cutoff=0.8))
        score += fuzzy_overlap_count * 1.0

        ratio = SequenceMatcher(None, user_text, q_norm).ratio()
        if ratio > 0.4:
            score += ratio * 2.5  

        if score > best_qa_score:
            best_qa_score = score

    best_qa_score += qa.priority * 0.1
    return best_qa_score

def find_best_answer(user_message: str, previous_text: str = None, locale: str = None, threshold: float = 0.30):
    query_to_process = user_message
    
    if previous_text and len(user_message.split()) <= 4:
        query_to_process = f"{previous_text} {user_message}"

    user_text = normalize(query_to_process)
    user_tokens = tokenize(query_to_process)
    
    if not user_tokens and len(user_text) < 2:
        return None, 0.0, {}

    # FIXED: Do not strictly block on needs_embedding=False so auto-translated items are searchable immediately
    candidates_qs = InsuranceQA.objects.filter(is_active=True)
    if locale:
        candidates_qs = candidates_qs.filter(locale__language_code=locale)
    
    candidates = list(candidates_qs.prefetch_related("question_variants", "links").select_related("topic", "locale"))
    if not candidates:
        return None, 0.0, {}

    scored = []
    for qa in candidates:
        kw = score_qa(user_tokens, user_text, qa)
        sem = semantic_score(user_text, qa)

        kw_norm = min(kw / 6.0, 1.0)
        # Give keyword/fuzzy matching more weight if embedding is empty or still generating
        sem_weight = 0.75 if qa.get_embedding() else 0.0
        kw_weight = 1.0 if not qa.get_embedding() else 0.25
        
        combined = (sem_weight * sem) + (kw_weight * kw_norm)
        scored.append((qa, combined, sem, kw_norm))

    if not scored:
        return None, 0.0, {}

    scored.sort(key=lambda x: x[1], reverse=True)
    best_qa, best_score, sem, kw = scored[0]

    debug = {
        "semantic": round(sem, 3), 
        "keyword": round(kw, 3),
        "runner_up": scored[1][1] if len(scored) > 1 else 0
    }

    if best_score < threshold:
        return None, best_score, debug

    return best_qa, best_score, debug

def get_suggestions(limit: int = 6, starters_only: bool = True, locale: str = None):
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