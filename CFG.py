import nltk
from nltk import CFG
import random

grammar = CFG.fromstring("""
    S -> HELO MAILFROM RCPTTO DATA
    HELO -> "HELO " host
    host -> "hostname"
    MAILFROM -> "MAIL FROM:" from_add
    from_add -> "<a@a.com>"
    RCPTTO ->  "RCPT TO:" to_add
    to_add -> "<b@b.com>"
    DATA -> "DATA" body
    body -> "1" body | "2" body | "3" body | "4" body | "5" body | "!" body | "@" body | "#" body | "$" body | "%" body | "^" body | "&" body | TERM
    TERM -> "."
""")

def generate_sentence(grammar, symbol):
    if symbol in grammar._lhs_index:
        production = random.choice(grammar.productions(lhs=symbol))
        return ''.join(generate_sentence(grammar, sym) for sym in production.rhs())
    else:
        return symbol

sentence = generate_sentence(grammar, grammar.start())
print(sentence)
