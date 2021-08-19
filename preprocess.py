import re
from types import new_class
import emoji
import unidecode
from tqdm import tqdm

import spacy #spacy==3.1.1

from lemmatizer import get_lemma_dict

lemma_dict = get_lemma_dict(lg=True)


my_stopword_list = {'aquilo', 'aquela', 'aquele','aquelas', 'aqueles',   'a','pra','dms', 'ah', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo', 'as', 'ate', 'ateh', 'bastante', 'cidade', 'com', 'como', 'da', 'das', 'de', 'dela', 'delas', 'dele', 'deles', 'demais', 'depois', 'diz', 'do', 'dos', 'e', 'eh', 'ela', 'elas', 'ele', 'eles', 'em', 'entre', 'era', 'eram', 'eramos', 'essa', 'essas', 'esse', 'esses', 'esta', 'estah', 'estamos', 'estao', 'estas', 'estava', 'estavam', 'estavamos', 'este', 'esteja', 'estejam', 'estejamos', 'estes', 'esteve', 'estive', 'estivemos', 'estiver', 'estivera', 'estiveram', 'estiveramos', 'estiverem', 'estivermos', 'estivesse', 'estivessem', 'estivessemos', 'estou', 'eu', 'fala', 'falaram', 'falei', 'falou', 'faz', 'fazem', 'fez', 'fiz', 'fizeram', 'foi', 'fomos', 'for', 'foram', 'foramos', 'forem', 'formos', 'fosse', 'fossem', 'fossemos', 'fui', 'ha', 'haa', 'haja', 'hajam', 'hajamos', 'hao', 'havemos', 'havia', 'hei', 'houve', 'houvemos', 'houver', 'houvera', 'houveram', 'houveramos', 'houverao', 'houverei', 'houverem', 'houveremos', 'houveria', 'houveriam', 'houveriamos', 'houvermos', 'houvesse', 'houvessem', 'houvessemos', 'imensamente', 'isso', 'isto', 'ja', 'jah', 'lhe', 'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu', 'meus', 'minha', 'minhas', 'mt', 'muito', 'muitíssimo', 'na', 'nas', 'ne', 'neh', 'no', 'nos', 'nossa', 'nossas', 'nosso', 'nossos', 'num', 'numa', 'o', 'oi', 'ola', 'opa', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos', 'por', 'pouco', 'pouquinho', 'q', 'qq', 'qual', 'quando', 'quase', 'que', 'quem', 'rt', 'sao', 'se', 'seja', 'sejam', 'sejamos', 'sem', 'ser', 'sera', 'serao', 'serei', 'seremos', 'seria', 'seriam', 'seriamos', 'seu', 'seus', 'so', 'soh', 'somos', 'sou', 'sua', 'suas', 'tambem', 'tb', 'tbm', 'te', 'tem', 'temos', 'tenha', 'tenham', 'tenhamos', 'tenho', 'ter', 'terao', 'tere', 'terei', 'teremos', 'teria', 'teriam', 'teriamos', 'teu', 'teus', 'teve', 'tinha', 'tinham', 'tinhamos', 'tive', 'tivemos', 'tiver', 'tivera', 'tiveram', 'tiveramos', 'tiverem', 'tivermos', 'tivesse', 'tivessem', 'tivessemos', 'tu', 'tua', 'tuas', 'um', 'uma', 'vc', 'vcs', 'voce', 'voces', 'vos',  'vs', 'pro', 'po', 'nossa', 'qq', 'cpf', 'ta','nmrl', 'pprt', 'mn', 'fml', 'preco','compra','ai','karol','comprar','agora','nada','casas','bahia','quero','roubo','irao','tudo','dinheiro','posicao','valor','ainda','cara','carro','cb','porque','compra','piza','comprei','seara','gente','pode','la','to','loja','baiano','casa','onde','sadia','produto','saber','sim','propaganda','pedido','assim','ver','vegana','reais','deus','volta','todos','dias','frete','entao','shoping','alguem','patrocinadores','brasil','acho','hoje','site','empresa','vamos','sobre','vem','coisa','anos','parece','favor','carne','mil','pontofrio','quer','produtos','tao','queria','olha','entrega','fica''dia','vai','tudo','quero','aqui','comprar','paypal','shoping','natal','fazer','ai','prefeito','loja','todos','dar','valor','riomar','vou','bahia','agora','pode','hospital','sempre','brasil','rio','salvador','gente','hoje','casas','vamos','ano','clinicas','anos','onde','la','casa','promocao','grande','governador','hora','honda','sim','drogasil','kondzila','olha','to','mar','todo','saude','preco','queria','vem','familia','saber','ver','nada','carro','faco','mourao','preciso','seara','martins','paulo','white','assim','comprei','produtos','anethun','site','link','pq','compra','dias','vitoria','whatsap','raia','fica','lojas','derby','linha','sentiram','senti'}
my_emoji_stopword = {'🏻','🏼','🏽','🏾','🏿','♂','♀'}
class Preprocess():
    def __init__(self):
        self.REGEX_REMOVE_PUNCTUATION = re.compile('[%s]' % re.escape('!¡"$%&\'()*+,.ªº/:;<=>#¿?[\\]^_`{|}~'))
        self.URL_RE = re.compile(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*')
        self.WWW_RE = re.compile(r'www?[-_.?&~;+=/#0-9A-Za-z]{1,2076}')
        #self.HASHTAG_RE = re.compile(r'#[-_.?&~;+=/#0-9A-Za-z]{1,2076}')
        self.MENTION_RE = re.compile(r'@[-_.?&~;+=/#0-9A-Za-z]{1,2076}')
        self.MAIL_RE = re.compile(r'\S*@\S*\s?')
        #self.DIGIT_RE = re.compile(r"\b[0-9]+\b\s*")
        self.DIGIT_RE = re.compile(r"\S*\d\S*") #remove if contains digit
        self.REPEATED_LETTER =  re.compile(r"([a-q?=t-z])\1{1,}")
        self.REPEATED_LETTER_RS =  re.compile(r"([rs])\1{2,}")
        #self.REPEATED_LETTER_HIFEN = re.compile(r"([-?=t-z])\1{1,}") #remove repeated
        self.LETTER_HIFEN = re.compile(r"(?<!\w)\W+|\W+(?!\w)") #remove hifen if hifen is between and len(1) guarda-roupa (keep) meu--deus (remove)
        

            

    def extract_emojis(self, s):
        return [c for c in s if c in emoji.UNICODE_EMOJI]


    def remove_nprop(sentence):
        tags = tagger.tag(sentence.split())
        
        words = [t[0] for t in tags if t[1]!='NPROP']
        names = [t[0] for t in tags if t[1] =='NPROP']

        if(len(names)!=0):
            founded_names.append(names)

        return " ".join(words)
    def transform(self, texts):
        #texts: lista de posts
        #labels: lista com o sentimento de cada post
        new_texts = []
        for t in range(len(texts)):
            if "div>" not in texts[t] and "<img src=" not in texts[t] and "style=" not in texts[t] and "text-align:" not in texts[t]:
            
                sentence = texts[t].lower().replace("\n", "").replace("\t", " ").strip() 
                sentence = " ".join([s for s in sentence.split() if s not in ["rt", "RT"]]) 
                #sentence = self.remove_nprop(sentence)
                emojis = self.extract_emojis(sentence) #encontra os emojis
                emojis = [e for e in emojis if e not in my_emoji_stopword]
                sentence = unidecode.unidecode(sentence)
                sentence =  self.MAIL_RE.sub(" ", sentence)
                sentence =  self.URL_RE.sub(" ", sentence)
                sentence =  self.WWW_RE.sub(" ", sentence)
                #sentence =  self.HASHTAG_RE.sub(" ", sentence)
                sentence =  self.REPEATED_LETTER.sub(r"\1", sentence)
                sentence =  self.REPEATED_LETTER_RS.sub(r"\1\1", sentence)
                sentence =  self.MENTION_RE.sub(" ", sentence)
                sentence = self.LETTER_HIFEN.sub(" ", sentence)

                sentence =  self.REGEX_REMOVE_PUNCTUATION.sub(" ", sentence)
                sentence =  self.DIGIT_RE.sub("", sentence)


                sentence =  " ".join([token for token in sentence.split()  if token not in my_stopword_list])
                sentence = " ".join([sentence] + emojis) #adiciona os emojis novamente 

                    
                sentence = sentence.strip()
                new_texts.append(sentence)
        return new_texts
      
    def fit_transform(self, texts, labels):
        print("preprocessing") 

        #texts: lista de posts
        #labels: lista com o sentimento de cada post

        posts_dict = {}
        for t in tqdm(range(len(texts))):
            if "div>" not in texts[t] and "<img src=" not in texts[t] and "style=" not in texts[t] and "text-align:" not in texts[t]:
              
                sentence = texts[t].lower().replace("\n", "").replace("\t", " ").strip() 
                sentence = " ".join([s for s in sentence.split() if s not in ["rt", "RT"]])  
                #sentence = self.remove_nprop(sentence)
                emojis = self.extract_emojis(sentence) #find emojis 
                emojis = [e for e in emojis if e not in my_emoji_stopword]  #remove stopwords emojis
                sentence = unidecode.unidecode(sentence) #normalize
                sentence =  self.MAIL_RE.sub(" ", sentence) #remove email
                sentence =  self.URL_RE.sub(" ", sentence) #remove url
                sentence =  self.WWW_RE.sub(" ", sentence) #remove www
                #sentence =  self.HASHTAG_RE.sub(" ", sentence) #remove hashtags
                sentence =  self.REPEATED_LETTER.sub(r"\1", sentence)  
                sentence =  self.REPEATED_LETTER_RS.sub(r"\1\1", sentence)
                sentence =  self.MENTION_RE.sub(" ", sentence)
                sentence = self.LETTER_HIFEN.sub(" ", sentence)
                sentence =  self.REGEX_REMOVE_PUNCTUATION.sub(" ", sentence)
                sentence =  self.DIGIT_RE.sub("", sentence)


                sentence =  " ".join([token for token in sentence.split()  if token not in my_stopword_list])
                sentence = " ".join([sentence] + emojis) #adiciona os emojis novamente 

                    
                sentence = sentence.strip()

            if(sentence != ""):
                posts_dict[sentence]=labels[t]
                #new_texts.append(sentence)
                #new_labels.append(labels[t])

        return [d[0] for d in list(posts_dict.items())], [d[1] for d in list(posts_dict.items())]


    def fit_transform_lemma(self, texts, labels):
        print("preprocessing using lemmatization")
        #texts: lista de posts
        #labels: lista com o sentimento de cada post
        posts_dict = {}

    
        for t in tqdm(range(len(texts))):
            if "div>" not in texts[t] and "<img src=" not in texts[t] and "style=" not in texts[t] and "text-align:" not in texts[t]:
              
                sentence = texts[t].lower().replace("\n", "").replace("\t", " ").strip() 
                sentence = " ".join([s for s in sentence.split() if s not in ["rt", "RT"]])  
                #sentence = self.remove_nprop(sentence)
                emojis = self.extract_emojis(sentence) #find emojis 
                emojis = [e for e in emojis if e not in my_emoji_stopword]  #remove stopwords emojis
                sentence = unidecode.unidecode(sentence) #normalize
                sentence =  self.MAIL_RE.sub(" ", sentence) #remove email
                sentence =  self.URL_RE.sub(" ", sentence) #remove url
                sentence =  self.WWW_RE.sub(" ", sentence) #remove www
                #sentence =  self.HASHTAG_RE.sub(" ", sentence) #remove hashtags
                sentence =  self.REPEATED_LETTER.sub(r"\1", sentence)  
                sentence =  self.REPEATED_LETTER_RS.sub(r"\1\1", sentence)
                sentence =  self.MENTION_RE.sub(" ", sentence)
                sentence = self.LETTER_HIFEN.sub(" ", sentence)
                sentence =  self.REGEX_REMOVE_PUNCTUATION.sub(" ", sentence)
                sentence =  self.DIGIT_RE.sub("", sentence)


                sentence = " ".join([lemma_dict.get(x, x) for x in sentence.split() if x not in my_stopword_list])
                sentence = " ".join([sentence] + emojis) #adiciona os emojis novamente 

                    
                sentence = sentence.strip()

            if(sentence != ""):
                posts_dict[sentence]=labels[t]
                #new_texts.append(sentence)
                #new_labels.append(labels[t])
        return [d[0] for d in list(posts_dict.items())], [d[1] for d in list(posts_dict.items())]
       

    def transform_lemma(self, texts):
        #texts: lista de posts
        #labels: lista com o sentimento de cada post
    
        new_texts  = []
    
        for t in range(len(texts)):
            if "div>" not in texts[t] and "<img src=" not in texts[t] and "style=" not in texts[t] and "text-align:" not in texts[t]:
              
                sentence = texts[t].lower().replace("\n", "").replace("\t", " ").strip() 
                sentence = " ".join([s for s in sentence.split() if s not in ["rt", "RT"]])  
                #sentence = self.remove_nprop(sentence)
                emojis = self.extract_emojis(sentence) #find emojis 
                emojis = [e for e in emojis if e not in my_emoji_stopword]  #remove stopwords emojis
                sentence = unidecode.unidecode(sentence) #normalize
                sentence =  self.MAIL_RE.sub(" ", sentence) #remove email
                sentence =  self.URL_RE.sub(" ", sentence) #remove url
                sentence =  self.WWW_RE.sub(" ", sentence) #remove www
                #sentence =  self.HASHTAG_RE.sub(" ", sentence) #remove hashtags
                sentence =  self.REPEATED_LETTER.sub(r"\1", sentence)  
                sentence =  self.REPEATED_LETTER_RS.sub(r"\1\1", sentence)
                sentence =  self.MENTION_RE.sub(" ", sentence)
                sentence = self.LETTER_HIFEN.sub(" ", sentence)
                sentence =  self.REGEX_REMOVE_PUNCTUATION.sub(" ", sentence)
                sentence =  self.DIGIT_RE.sub("", sentence)

                sentence = " ".join([lemma_dict.get(x, x) for x in sentence.split() if x not in my_stopword_list])
                #sentence = " ".join(filter(lambda x:x.strip() not in my_stopword_list, sentence.split()))
                sentence = " ".join([sentence] + emojis) #adiciona os emojis novamente 

                    
                new_texts.append(sentence.strip())
            else:
                new_texts.append("")

        return new_texts  

if __name__ == '__main__':
    import pickle, lzma, random
    p = Preprocess()
    import time
    start = time.time()
    a0= p.transform(['😋😋😋😋😋 meu amigaaao 👎🏾  🤦🏽‍♀️ 🤦🏿 🤷🏾‍♂️ aaaeee http://google.com google.com www.google.com']*10000)
    print(time.time() - start)


    start = time.time()
    a1= p.transform_lemma(['😋😋😋😋😋 meu amigaaao 👎🏾  🤦🏽‍♀️ 🤦🏿 🤷🏾‍♂️ aaaeee http://google.com google.com www.google.com']*10000)
    print(time.time() - start)

    # from spellchecker import SpellChecker

    # spell = SpellChecker(language='pt')

    # # find those words that may be misspelled
    # misspelled = spell.unknown(['something', 'is', 'hapenning', 'here'])
    # start = time.time()
    # c= [spell.correction("bomzao") for i in range(10000)]
    # print(time.time() - start)
    # for word in misspelled:
    #     # Get the one `most likely` answer
    #     print(spell.correction(word))

    #     # Get a list of `likely` options
    #     print(spell.candidates(word))


    import IPython; IPython.embed()