import pickle
from modules.clasificador import Clasificador
from modules.preprocesamiento import TextVectorizer

#cls =  Clasificador()


with open('./src/modules/clasificadorsk/data/clasificador_svm.pkl', 'rb') as archivo:
  cls  = pickle.load(archivo)

text= ["no funciona el campus virtual "]
print(cls.clasificar(text))
