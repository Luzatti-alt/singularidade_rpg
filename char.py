import json
import os
class Char():
    data_dir = "data/user/"
    def __init__(self):
        pass
    #cria na pasta de user/username o json
    @staticmethod
    def criar_char_user(user):
        if not os.path.exists(Char.data_dir):
            os.makedirs(Char.data_dir)
        pasta_user = os.path.join(Char.data_dir, user)
        if not os.path.exists(pasta_user):
            os.makedirs(pasta_user)
        caminho_arquivo = os.path.join(pasta_user, "char.json")
        if os.path.exists(caminho_arquivo):
            return False
        #valores base
        ficha = {
            "user": user,
            "nivel": 1,
            "origem": "Desconhecida",
            "especializacao": "Nenhuma",

            "atributos": {
                "pontos_atributo": 10,
                "forca": {"nivel": 10, "pontos_usados": 0},
                "destreza": {"nivel": 10, "pontos_usados": 0},
                "constituicao": {"nivel": 10, "pontos_usados": 0},
                "inteligencia": {"nivel": 10, "pontos_usados": 0},
                "sabedoria": {"nivel": 10, "pontos_usados": 0},
                "fama": {"nivel": 10, "pontos_usados": 0},
                "stamina": {"nivel": 10, "pontos_usados": 0},
                "movimento": {"nivel": 12, "pontos_usados": 0},
                "hp": {"nivel": 15, "pontos_usados": 0},
                "defesa": {"nivel": 0, "pontos_usados": 0}
            },

            "itens": {
                "slots_disponiveis": 10,
                "slots_usados": 0,
                "lista": []
            },

            "equipamentos": []
        }

        # salvar arquivo
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(ficha, f, indent=4, ensure_ascii=False)

        return True