from flask_restful import Resource, reqparse
from models.produto_model import ProdutoModel
from models.fornecedor_model import FornecedorModel
from models.categoria_model import CategoriaModel
from flask_jwt_extended import jwt_required


class Produtos(Resource):

    def get(self):
        order = [produto.json()
                 for produto in ProdutoModel.query.all()]
        return {'fornecedores': order}


class Produto(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('cod_produto', type=str,
                            required=True, help="Campo obrigatório.")
    argumentos.add_argument('nome_produto',  type=str,
                            required=True, help="Campo obrigatório.")
    argumentos.add_argument('valor_produto', type=float,
                            required=True, help="Campo obrigatório.")
    argumentos.add_argument('cod_categoria', type=int,
                            required=True, help="Campo obrigatório.")
    argumentos.add_argument('cod_fornecedor', type=int,
                            required=True, help="Campo obrigatório.")
    argumentos.add_argument('ativo', type=str, required=True)

    def get(self, id_produto):
        produto = ProdutoModel.find_produto(id_produto)
        if produto:
            return produto.json()
        return {'mensagem': 'Produto não encontrado.'}, 404

    @jwt_required
    def put(self, id_produto):
        dados = Produto.argumentos.parse_args()

        produto_encontrado = ProdutoModel.find_produto(id_produto)
        if produto_encontrado:
            produto_encontrado.update_produto(**dados)
            produto_encontrado.save_produto()
            return produto_encontrado.json(), 200

        if ProdutoModel.find_produto_by_cod(dados['cod_produto']):
            return {'mensagem': 'Produto com código "{}" já existe.'
                    .format(dados['cod_produto'])}, 400

        produto = ProdutoModel(id_produto, **dados)
        try:
            produto.save_produto()
        except ValueError:
            return {'mensagem': 'Erro ao salvar o produto.'}, 500
        return produto.json(), 201

    @jwt_required
    def delete(self, id_produto):
        produto = ProdutoModel.find_produto(id_produto)
        if produto:
            try:
                produto.delete_produto()
            except ValueError:
                return {'mensagem': 'Erro ao excluir o produto.'}, 500
            return {'mensagem': 'Produto excluído.'}
        return {'mensagem': 'Produto não encontrado.'}, 404


class ProdutoCadastro(Resource):

    @jwt_required
    def post(self):
        dados = Produto.argumentos.parse_args()

        if ProdutoModel.find_produto_by_cod(dados['cod_produto']):
            return {'mensagem': 'Produto com código "{}" já existe.'
                    .format(dados['cod_produto'])}, 400

        if not CategoriaModel.find_categoria(dados['cod_categoria']):
            return {'mensagem': 'Categoria com código "{}" não existe.'
                    .format(dados['cod_categoria'])}, 400

        if not FornecedorModel.find_fornecedor(dados['cod_fornecedor']):
            return {'mensagem': 'Fornecedor com código "{}" não existe.'
                    .format(dados['cod_fornecedor'])}, 400

        produto = ProdutoModel(**dados)

        try:
            produto.save_produto()
        except ValueError:
            return {'mensagem': 'Erro ao salvar o produto.'}, 500
        return produto.json(), 200
