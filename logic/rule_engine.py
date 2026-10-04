# 키워드 규칙으로 답변을 만든다. 규칙에 맞지 않으면 None을 돌려준다.
from data.menu_rules import RULES, EXCLUDE_WORDS, EXCLUDE_TAGS


def find_emotion(text):
    for emotion, rule in RULES.items():
        if any(k in text for k in rule["keywords"]):
            return emotion
    return None


def find_excluded_tags(text):
    """'매운 건 싫어' 같은 문장에서 제외할 태그를 찾는다."""
    if not any(w in text for w in EXCLUDE_WORDS):
        return set()
    return {tag for key, tag in EXCLUDE_TAGS.items() if key in text}


def recommend(emotion, excluded):
    rule = RULES[emotion]
    menus = [name for name, tags in rule["menus"] if not (set(tags) & excluded)]
    if not menus:
        return None  # 전부 걸러졌으면 API에게 맡긴다
    return f"{rule['empathy']} {', '.join(menus)} 어떠세요? {rule['reason']}"


def answer(text, state):
    """state: excluded(set), last_emotion(str|None)을 가진 딕셔너리 형태 객체."""
    new_excluded = find_excluded_tags(text)
    state.excluded |= new_excluded

    emotion = find_emotion(text)
    if emotion:
        state.last_emotion = emotion
    elif new_excluded and state.last_emotion:
        emotion = state.last_emotion  # 조건만 말했으면 이전 감정으로 다시 추천

    if not emotion:
        return None
    reply = recommend(emotion, state.excluded)
    if reply and new_excluded:
        reply = "알겠어요, 그건 빼고 다시 골라봤어요. " + reply
    return reply
