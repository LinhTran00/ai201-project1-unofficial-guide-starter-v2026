def judge(question, expects, answer, results) -> bool :
    '''
    Q1: 'give', expect: 'give'
    the expect is in the answer
    '''
    return expects.lower().strip() in answer.lower()

'''

LLM as judge -> recommend to use the code in generate.py to help reudce cache
rapidfuzz 

'''