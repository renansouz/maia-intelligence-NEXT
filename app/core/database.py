import os
import oracledb
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

class Database:
    def __init__(self):
        # Configurações do Oracle vindas do .env
        self.user = os.getenv("ORACLE_USER")
        self.password = os.getenv("ORACLE_PASSWORD")
        self.dsn = f"{os.getenv('ORACLE_HOST')}:{os.getenv('ORACLE_PORT')}/{os.getenv('ORACLE_SERVICE')}"
        self.pool = None

    def get_pool(self):
        """Cria um Pool de Conexões se não existir (Singleton Pattern)"""
        if self.pool is None:
            try:
                # Iniciamos no modo 'thin' (não precisa de Instant Client no Mac/Linux)
                self.pool = oracledb.create_pool(
                    user=self.user,
                    password=self.password,
                    dsn=self.dsn,
                    min=1,    # Mínimo de conexões abertas
                    max=5,    # Máximo de conexões (seguro para o Oracle da FIAP)
                    increment=1
                )
            except Exception as e:
                raise e
        return self.pool

    def get_connection(self):
        """Retira uma conexão do Pool"""
        return self.get_pool().acquire()

    def release_connection(self, conn):
        """Devolve a conexão para o Pool"""
        self.get_pool().release(conn)

# Instância única para ser importada em todo o projeto
db = Database()