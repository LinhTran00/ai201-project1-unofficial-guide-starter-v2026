REFUSAL_PHRASES = (
    "there is no mention of how much",
    "there is no mention of allowing",
    "i don't have enough information",
    "i do not have enough information",
)


def judge(question, expects, answer, results) -> bool :
    '''
    Q1: 'give', expect: 'give'
    the expect is in the answer
    '''
    normalized_answer = answer.lower()
    if any(phrase in normalized_answer for phrase in REFUSAL_PHRASES):
        return False
    return expects.lower().strip() in normalized_answer

'''

LLM as judge -> recommend to use the code in generate.py to help reduce cache
rapidfuzz 

'''