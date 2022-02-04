from bs4 import BeautifulSoup
import requests
import sqlite3
from sqlite3 import OperationalError
from datetime import datetime
import csv
from abc import ABC, abstractmethod
import time


class Extract(ABC):
    header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0'}
    lista_fiis = []

    @abstractmethod
    def get_lista_fiis(self):
        pass

    @abstractmethod
    def get_cotacao(self):
        pass


class Extract_1(Extract):
    def __init__(self, nome_arquivo='fundosListados.csv'):
        self.nome_arquivo = nome_arquivo

    def _extract_to_list(self):
        with open(self.nome_arquivo, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.lista_fiis.append(row['Codigo'])

    def get_lista_fiis(self):
        if len(self.lista_fiis) == 0:
            self._extract_to_list()
        return self.lista_fiis

    def get_cotacao(self, fii):
        fii = fii.replace('/fiis/', '')
        url = 'https://finance.yahoo.com/quote/' + fii + '.SA'
        response = requests.get(url, headers=self.header)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            cotacao = soup.find_all('span', {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"})
            try:
                cotacao = cotacao[0].text
                return cotacao
            except IndexError:
                cotacao = '0.0'
                return cotacao

    def __str__(self):
        return "Classe Extract que faz uso de planilha e site yahoo finance "

    def __repr__(self):
        return "Classe Extract => Planilha e YahooFinance (API)"


class Extract_2(Extract):
    def _extract_to_list(self):
        url = 'https://mfinance.com.br/api/v1/fiis'
        res = requests.get(url).json()['fiis']
        for fii in res:
            self.lista_fiis.append(fii['symbol'])

    def get_lista_fiis(self):
        if len(self.lista_fiis) == 0:
            self._extract_to_list()
        return self.lista_fiis

    def get_cotacao(self, fii):
        url = 'https://mfinance.com.br/api/v1/fiis/' + fii
        res = requests.get(url).json()
        cotacao = str(res['lastPrice'])
        return cotacao

    def __str__(self):
        return "Classe Extract que faz uso da API mfinance "

    def __repr__(self):
        return "Classe Extract => API MFinance"


class Loader(ABC):
    @abstractmethod
    def armazenar_lista(self):
        pass


class Loader_1(Loader):
    def __init__(self, nome_banco='fii.db'):
        self.nome_banco = nome_banco
        self._criar_banco_fii(self.nome_banco)

    def _criar_banco_fii(self, nome_banco):
        self.conn = sqlite3.connect(self.nome_banco)
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("""
                    CREATE TABLE fii (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        codigo_fii TEXT NOT NULL,
                        preco FLOAT NOT NULL,
                        datetime DATE NOT NULL );
                        """)
        except OperationalError:
            print('Tabela já criada')
        self.conn.close()

    def armazenar_lista(self, lista_cotacao):
        self.conn = sqlite3.connect(self.nome_banco)
        self.cursor = self.conn.cursor()
        self.cursor.executemany("""
        INSERT INTO fii (codigo_fii, preco, datetime)
        VALUES (?,?,?)
        """, lista_cotacao)
        self.conn.commit()
        self.conn.close()

    def __str__(self):
        return "Classe Loader: Armazenar no banco de dados SQLite"

    def __repr__(self):
        return "Classe Loader: SQLite"


class Loader_2(Loader):
    def __init__(self, nome_arquivo='fii.csv'):
        self.nome_arquivo = nome_arquivo

    def armazenar_lista(self, lista_cotacao):
        header = ['codigo_fii', 'preco', 'datetime']
        with open(self.nome_arquivo, 'w') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(header)
            csv_out.writerows(lista_cotacao)

    def __str__(self):
        return "Classe Loader: Armazenar em planilhas CSV"

    def __repr__(self):
        return "Classe Loader: Planilhas CSV"


class MeuETL:
    lista_fiis = []

    def __init__(self, extract, loader):
        if not isinstance(extract, Extract):
            raise TypeError('Extrador incorreto')
        self.extract = extract
        if not isinstance(loader, Loader):
            raise TypeError('Carregador incorreto')
        self.load = loader
        self.lista_fiis = self.extract.get_lista_fiis()

    def execute(self):
        lista_cotacao = []
        for fii in self.lista_fiis:
            cotacao = self.extract.get_cotacao(fii)
            lista_cotacao.append((fii, cotacao, datetime.now()))
        self.load.armazenar_lista(lista_cotacao)

    def __str__(self):
        return "Classe Meu ETL"

    def __repr__(self):
        return "Classe Meu ETL"


if __name__ == "__main__":
    extrator1 = Extract_1()
    extrator2 = Extract_2()
    loader1 = Loader_1()
    loader2 = Loader_1('fii2.db')
    loader3 = Loader_2()

    t1 = time.time()
    meu_etl = MeuETL(extrator2, loader1)
    meu_etl.execute()
    t2 = time.time()
    print("--- %s seconds ---" % (t2 - t1))

    t1 = time.time()
    meu_etl = MeuETL(extrator1, loader2)
    meu_etl.execute()
    t2 = time.time()
    print("--- %s seconds ---" % (t2 - t1))

    t1 = time.time()
    meu_etl = MeuETL(extrator2, loader3)
    meu_etl.execute()
    t2 = time.time()
    print("--- %s seconds ---" % (t2 - t1))
