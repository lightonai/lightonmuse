import lightonmuse


creator = lightonmuse.Create("lyra-en")  # use "orion-fr" for French
sentence = "Ça fait un moment que je traîne chaque nuit sur le quai de notre gare. Je viens toujours"
n_tokens = 16
outputs, cost, rid = creator(sentence, n_tokens=n_tokens, seed=0, return_logprobs=True)
print(f"Request {rid} cost {cost}")
print("*"*10)
print(outputs)

