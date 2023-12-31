import unittest
from unittest.mock import patch, Mock
import requests
from pact import Consumer, Provider

class CatalogoContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pact = Consumer('Pedido').has_pact_with(Provider('Catalogo'), pact_dir='./test/integration/contracts')
        cls.pact.start_service()
    
    @classmethod
    def tearDownClass(cls):
        cls.pact.stop_service() 

    def testCriarProdutoComSucesso(self):
        request_data = {
            "sku": "SKU123",
            "nome": "Produto Teste",
            "descr": "Descrição Teste",
            "urlImagem": "http://imagem",
            "estoque": {
                "emEstoque": 10,
                "reservado": 0
            },
            "preco": {
                "precoLista": 20.0,
                "precoDesconto": 15.0
            }
        }
        request_headers = {'Content-Type': 'application/json'}

        (self.pact
         .given('Um produto válido')
         .upon_receiving('Uma requisição para criar um produto')
         .with_request('POST', '/produto', body=request_data, headers=request_headers)
         .will_respond_with(200, body={"message": "Produto criado com sucesso"}))

        with self.pact:
            result = requests.post(self.pact.uri + '/produto', json=request_data, headers=request_headers)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {"message": "Produto criado com sucesso"})

    def testCriarProdutoFalhaProdutoJaExiste(self):
        request_data = {
            "sku": "SKU123",
            "nome": "Produto Teste",
            "descr": "Descrição Teste",
            "urlImagem": "http://imagem",
            "estoque": {
                "emEstoque": 10,
                "reservado": 0
            },
            "preco": {
                "precoLista": 20.0,
                "precoDesconto": 15.0
            }
        }
        request_headers = {'Content-Type': 'application/json'}

        (self.pact
         .given('Um produto já existente')
         .upon_receiving('Uma requisição para criar um produto que já existe')
         .with_request('POST', '/produto', body=request_data, headers=request_headers)
         .will_respond_with(409, body={"detail": "Erro ao criar produto: Produto já existente"}))

        with self.pact:
            result = requests.post(self.pact.uri + '/produto', json=request_data, headers=request_headers)
        self.assertEqual(result.status_code, 409)
        self.assertEqual(result.json(), {"detail": "Erro ao criar produto: Produto já existente"})

    def testCriarProdutoPrecoInvalido(self):
        request_data = {
            "sku": "SKU123",
            "nome": "Produto Teste",
            "descr": "Descrição Teste",
            "urlImagem": "http://imagem",
            "estoque": {
                "emEstoque": 10,
                "reservado": 0
            },
            "preco": {
                "precoLista": 10.0,
                "precoDesconto": 15.0
            }
        }
        request_headers = {'Content-Type': 'application/json'}

        (self.pact
            .given('Um produto com preço de desconto maior que o preço de lista')
            .upon_receiving('Uma requisição para criar um produto com preço inválido')
            .with_request('POST', '/produto', body=request_data, headers=request_headers)
            .will_respond_with(400))
        
        with self.pact:
            result = requests.post(self.pact.uri + '/produto', json=request_data, headers=request_headers)
        self.assertEqual(result.status_code, 400)
