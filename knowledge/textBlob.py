from textblob import TextBlob
import string
txt = """The Trump economic toll will be revealed over time. It is already enormous. The last report showed more than 17 million first-time applications for unemployment. The markets plunged again Wednesday after a government report showed the worst decline in retail sales ever. The Post reports: “That figure stands in stark contrast to February’s revised 0.4 percent decline. The drop blew past economist expectations of about 8 percent as the outbreak gutted consumer spending, yanked millions out of the workforce and forced people to stay home.” Given that 70 percent of our economy depends on consumer spending, we should get ready for some truly awful GDP numbers, which in turn will drive markets lower."""
exclude = set(string.punctuation)
res = ''.join(ch for ch in txt if ch not in exclude)
blob = TextBlob(res)
print(blob.noun_phrases)