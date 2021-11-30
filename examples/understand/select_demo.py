import lightonmuse


selecter = lightonmuse.Select("orion-fr")
reference = "Aujourd'hui il fait beau"
conjunction = "veut dire"
correct, wrong = "Il y a du soleil", "Il fait moche"
candidates = [correct, wrong]
# this will ask: `Aujourd'hui il fait beau` veut dire `Il y a du soleil`? and
# `Aujourd'hui il fait beau` veut dire `Il fait moche`?
# the answer with the highest logprob (closer to zero) will be the correct one
outputs, cost, rid = selecter(reference, candidates, conjunction=conjunction,
                              concat_best=False)
print(f"Request {rid} cost {cost}")
print("*"*10)
print(outputs)
print("*"*10)
print(f"According to the model, `{reference}` {conjunction} `{outputs[0]['best']}`.")
