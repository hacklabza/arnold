# Notes

## NLTK

### Getting a list of sinonyms for word

```python
>>> go_sets = [s for s in wordnet.synsets('go') if 'go.v' in s.name()]
>>> go_sets
[Synset('go.v.02'), Synset('go.v.03'), Synset('go.v.05'), Synset('go.v.09'), Synset('go.v.10'), Synset('go.v.16'), Synset('go.v.19'), Synset('go.v.22'), Synset('go.v.23'), Synset('go.v.25'), Synset('go.v.28')]
>>> [s.lemma_names() for s in go_sets]
[['go', 'proceed', 'move'], ['go', 'go_away', 'depart'], ['go'], ['go'], ['go'], ['go'], ['go'], ['go'], ['go'], ['go', 'lead'], ['go']]
>>> [s.lemma_names() for s in go_sets]
```

### Filtering words

```python
>>> from nltk.corpus import stopwords
>>> from nltk.tokenize import word_tokenize
>>>
>>> command_sentence = "Arnold, go forward for 3 seconds"
>>> stop_words = set(stopwords.words('english'))
>>> word_tokens = word_tokenize(command_sentence)
>>>
>>> filtered_command_sentence = [w for w in word_tokens if not w.lower() in stop_words]
>>> filtered_command_sentence
['Arnold', ',', 'go', 'forward', '3', 'seconds']
```
