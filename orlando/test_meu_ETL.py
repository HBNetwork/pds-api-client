from meu_ETL import Extract, Extract_1, Loader
from meu_ETL import Extract_2
from meu_ETL import MeuETL
from meu_ETL import Loader_2
import pytest


class TestExtract_1:
    def test_metodo_get_lista_fiis(self):
        objeto = Extract_1()
        lista = objeto.get_lista_fiis()
        assert isinstance(lista, list)
        assert isinstance(lista[0], str)
        assert len(lista) == 383
        assert len(lista[0]) == 4

    def test_metodo_get_cotacao_1(self):
        objeto = Extract_1()
        cotacao = objeto.get_cotacao('hglg11')
        assert isinstance(cotacao, str)

    def test_metodo_get_cotacao_2(self):
        objeto = Extract_1()
        cotacao = objeto.get_cotacao('hglg')
        assert isinstance(cotacao, str)
        assert cotacao == '0.0'

    def test_str_repr(self):
        objeto = Extract_1()
        msg1 = 'Classe Extract que faz uso de planilha e site yahoo finance '
        msg2 = 'Classe Extract => Planilha e YahooFinance (API)'
        assert str(objeto) == msg1
        assert repr(objeto) == msg2


class TestExtract_2:
    def test_metodo_get_lista_fiis(self):
        objeto = Extract_2()
        lista = objeto.get_lista_fiis()
        assert isinstance(lista, list)
        assert isinstance(lista[0], str)
        assert len(lista) == 383
        assert len(lista[0]) == 4

    def test_metodo_get_cotacao_1(self):
        objeto = Extract_2()
        cotacao = objeto.get_cotacao('hglg11')
        assert isinstance(cotacao, str)

    def test_metodo_get_cotacao_2(self):
        objeto = Extract_2()
        cotacao = objeto.get_cotacao('hglg')
        assert isinstance(cotacao, str)
        assert cotacao == '0'

    def test_metodo__extract_to_list(self):
        objeto = Extract_2()
        objeto._extract_to_list()
        assert isinstance(objeto.lista_fiis, list)
        assert len(objeto.lista_fiis) > 200

    def test_str_repr(self):
        objeto = Extract_2()
        msg1 = 'Classe Extract que faz uso da API mfinance '
        msg2 = 'Classe Extract => API MFinance'
        assert str(objeto) == msg1
        assert repr(objeto) == msg2


class TestMeuETL:
    def test_instanciar_meu_etl_caminho_feliz(self):
        extrator = Extract_1()
        loader = Loader_2()
        etl = MeuETL(extrator, loader)
        assert isinstance(etl, MeuETL)
        assert isinstance(etl.extract, Extract)
        assert isinstance(etl.load, Loader)
        assert isinstance(etl.lista_fiis, list)

    def test_extrator_incorreto(self):
        extrator = str
        loader = Loader_2()
        with pytest.raises(TypeError) as error:
            MeuETL(extrator, loader)
        assert str(error.value) == 'Extrador incorreto'

    def test_carregador_incorreto(self):
        extrator = Extract_1()
        loader = str
        with pytest.raises(TypeError) as error:
            MeuETL(extrator, loader)
        assert str(error.value) == 'Carregador incorreto'

    def test_str_repr(self):
        extrator = Extract_1()
        loader = Loader_2()
        etl = MeuETL(extrator, loader)
        msg1 = 'Classe Meu ETL'
        assert str(etl) == msg1
        assert repr(etl) == msg1
