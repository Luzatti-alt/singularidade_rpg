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
            "nome_personagem": "ainda a ser definido",
            "nivel": 1,
            "origem": "ainda a ser definida",
            "especializacao": "ainda a ser definida",
            "atributos": {
                #se for nçao for restirngido valor continua
                "pontos_atributo_disponivel": 10,
                "forca": {"nivel": 10, "pontos_usados": 0},
                "destreza": {"nivel": 10, "pontos_usados": 0},
                "constituicao": {"nivel": 10, "pontos_usados": 0},
                "inteligencia": {"nivel": 10, "pontos_usados": 0},
                "sabedoria": {"nivel": 10, "pontos_usados": 0},
                "fama": {"nivel": 10, "pontos_usados": 0},
                "stamina": {"nivel": 10, "pontos_usados": 0},
                "movimento": {"nivel": 12, "pontos_usados": 0},
                "hp": {"valor": 15, "pontos_usados": 0},
                "defesa": {"valor": 3, "pontos_usados": 0}
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
    
    def mudar_stats(quem,onde,infos):
        print(f"onde:{onde}")
        print(f"infos:{infos}")
        qual_dir = f"data/user/{quem}/char.json"
        if not os.path.exists(qual_dir):
                return "Personagem não encontrado."
        with open(qual_dir, "r", encoding="utf-8") as f:
            ficha = json.load(f)
        if onde == "!nome":
            ficha["nome_personagem"] = infos
        elif onde == "!origem":
            match infos.lower():
                case "herdeiro":
                    ficha["origem"] = infos
                    ficha["atributos"]["pontos_atributo_disponivel"] = 10
                    ficha["especializacao"] = "ainda a ser escolhido"
                case "restringido":
                    ficha["origem"] = infos
                    ficha["atributos"]["pontos_atributo_disponivel"] = 15
                    ficha["especializacao"] = infos
                case "hirbrido":
                    ficha["origem"] = infos
                    ficha["atributos"]["pontos_atributo_disponivel"] = 10
                    ficha["especializacao"] = "ainda a ser escolhido"
                case "sem técnica":
                    ficha["origem"] = infos
                    ficha["atributos"]["pontos_atributo_disponivel"] = 10
                    ficha["especializacao"] = "ainda a ser escolhido"
                case "corpo mutante":
                    ficha["origem"] = infos
                    ficha["atributos"]["pontos_atributo_disponivel"] = 10
                    ficha["especializacao"] = "ainda a ser escolhido"
                case _:
                    return "origem invalida"
        elif onde == "!especialização":
            print("especialização")
            match infos.lower():
                case "lutador":
                    ficha["especializacao"] = infos
                case "especialista em técnicas":
                    ficha["especializacao"] = infos
                case "controlador":
                    ficha["especializacao"] = infos
                case "suporte":
                    ficha["especializacao"] = infos
                case _:
                    return "especialização invalida"
        elif onde == "!atributo":
            atributos = infos.split(",")
            print(f"\natributos(lista?)\n{atributos}\n")
            for item in atributos:
                 item = item.strip()  # remove espaços
            if ":" not in item:
                return f"Formato inválido em: {item}"
            nome, valor = item.split(":", 1)
            nome = nome.strip().lower()
            valor = valor.strip()
            if not valor.isdigit():
                return f"Valor inválido para {nome}: {valor}"
            valor = int(valor)
            if nome not in ficha["atributos"]:
                return f"Atributo inválido: {nome}"
            ficha["atributos"]["pontos_usados"] = valor
        else:
            return "Comando inválido."
        with open(qual_dir, "w", encoding="utf-8") as f:
            json.dump(ficha, f, indent=4, ensure_ascii=False)
        return "Ficha atualizada com sucesso."   