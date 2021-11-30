import lightonmuse


comparer = lightonmuse.Compare("orion-fr")
reference = "Je suis content"
correct, wrong, out_of_context = "Je suis heureux", "Je suis triste", "Hello world, Rami"
candidates = [wrong, correct, out_of_context]
outputs, cost, rid = comparer(reference, candidates)
print(f"Request {rid} cost {cost}")
print("*"*10)
print(outputs)
print("*"*10)
similarities = outputs[0]["similarities"]
similarities.sort(key=lambda x: x["similarity"], reverse=True)
best = similarities[0]["candidate"]
print(f"The best candidate detected for `{reference}` is: `{best}`")
