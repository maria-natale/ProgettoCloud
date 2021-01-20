class Book:
    def __init__(self, nome=None, autore=None, prezzo=None, disp=None, genere=None):
        self.nome = nome
        self.autore = autore
        self.prezzo = prezzo
        self.disp = disp
        self.genere = genere


    def setNome(self,name):
        self.nome = name

    def setAutore(self, aut):
        self.autore = aut

    def setPrezzo(self,p):
        self.prezzo = p

    def setDisp(self,d):
        self.disp = d

    def setGen (self,g):
        self.genere = g

    def getNome(self):
        return self.nome
    def getAutore(self):
        return self.autore
    def getPrezzo(self):
        return self.prezzo
    def getDisp(self):
        return self.disp
    def getGen(self):
        return self.genere