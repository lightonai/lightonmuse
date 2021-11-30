import lightonmuse


representer = lightonmuse.Represent("orion-fr")
sentence = "Je voudrais un café et deux croissants, s'il vous plait."
outputs, cost, rid = representer(sentence)
embedding = outputs[0]["embedding"]
print(f"Request {rid} cost {cost}")
print(f"The size of the embedding for a single sentence is {len(embedding)}")

sentence_list = [sentence, "Ma grande sœur a toujours eu un formidable esprit créatif."]
outputs, cost, rid = representer(sentence_list)
print(f"Request {rid} cost {cost}")
print(f"Sending a list of sentences of length {len(sentence_list)} to `Represent`"
      f"returns a list of embeddings of length {len(outputs)}")
first_embedding, second_embedding = outputs[0]["embedding"], outputs[1]["embedding"]
print(f"The size of the embeddings for each sentence is {len(second_embedding)}")
