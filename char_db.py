from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
Base = declarative_base()
class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    user = Column(String)
    personagem = relationship("personagem", back_populates="player")
class Personagem(Base):
    __tablename__ = "personagem"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    nivel = Column(Integer)
    origem = Column(String)
    especialização = Column(String)
    atributos= relationship("atributos", back_populates="personagem")
class Atributos(Base):
    __tablename__ = "atributos"
    #stats cap 25/40
    pontos_atributo = Column(Integer,default = 10)
    forca_nivel = Column(Integer,default=10) 
    forca_pontos_usados = Column(Integer,default=0) 
    essencia_nivel = Column(Integer,default=10) 
    essencia_pontos_usados = Column(Integer,default=0) 
    essencia_negativa_nivel = Column(Integer,default=10) 
    essencia_negativa_pontos_usados = Column(Integer,default=0) 
    destreza_nivel = Column(Integer,default=10) 
    destreza_pontos_usados = Column(Integer,default=0) 
    constituicao_nivel = Column(Integer,default=10) 
    constituicao_pontos_usados = Column(Integer,default=0) 
    inteligencia_nivel = Column(Integer,default=10) 
    inteligencia_pontos_usados = Column(Integer,default=0) 
    sabedoria_nivel = Column(Integer,default=10) 
    sabedoria_pontos_usados = Column(Integer,default=0) 
    fama_nivel = Column(Integer,default=10) 
    fama_pontos_usados = Column(Integer,default=0) 
    stamina_nivel = Column(Integer,default=10) 
    stamina_pontos_usados = Column(Integer,default=0) 
    movimento_nivel = Column(Integer,default=12)
    movimento_pontos_usados = Column(Integer)
    hp = Column(Integer,default=15)
    hp_nivel = Column(Integer,default=15)
    hp_pontos_usados = Column(Integer,default=0)
    integridade_nivel = Column(Integer,default=0)
    integridade_pontos_usados = Column(Integer)
    defesa_nivel = Column(Integer,default=0)
    defesa_pontos_usados = Column(Integer,default=0)
    #
    personagem_id = Column(Integer, ForeignKey("personagens.id"))
    personagem = relationship("personagem", back_populates="atributos")
class Itens(Base):
    __tablename__ = "itens"
    slots_disponiveis = Column(Integer, default = 10)
    slots_usados = Column(Integer, default = 0)
    personagem_id = Column(Integer, ForeignKey("personagens.id"))
    personagem = relationship("personagem", back_populates="itens")
class Equipamentos(Base):
    __tablename__ = "equipamentos"
    id = Column(Integer, primary_key=True)
    tipo = Column(Integer)
    nome = Column(String)
    personagem_id = Column(Integer, ForeignKey("personagens.id"))
    personagem = relationship("personagem", back_populates="equipamentos")