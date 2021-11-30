import lightonmuse


def get_most_suprising(token_scores):
    """Returns the most surprising token,
    i.e. the one with lowest logprob"""
    min_val = 0.
    for el in token_scores:
        key, value = el.popitem()
        if value < min_val:
            min_val = value
            most_surprising = key
    return most_surprising


analyser = lightonmuse.Analyse("orion-fr")

# this sentence is pretty much expected, probably "voudrais" or "cafe"
# will "surprise" the model the most because they can be switched for
# many other expressions in this context
sentence = "Je voudrais un café et deux croissants, s'il vous plait."
outputs, cost, rid = analyser(sentence)
print(f"Request {rid} cost {cost}")
print("*"*10)
print(outputs)
print("*"*10)
print(f"In the sentence: `{sentence}`")
print(f"The most surprising token is: {get_most_suprising(outputs[0]['token_scores'])}")

# expect "avions" to be the most unexpected word here
sentence = "Je voudrais un café et deux avions, s'il vous plait."
outputs, cost, rid = analyser(sentence)
print(f"Request {rid} cost {cost}")
print("*"*10)
print(outputs)
print("*"*10)
print(f"In the sentence: `{sentence}`")
print(f"The most surprising token is: {get_most_suprising(outputs[0]['token_scores'])}")
