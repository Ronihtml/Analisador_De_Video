"""
Configurações do aplicativo YouTube Analyzer.
"""

import os

# Diretórios do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, 'downloads')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'app', 'scripts')

# Configurações da aplicação Flask
class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')
    
    # Garantir que as pastas necessárias existem
    @staticmethod
    def init_app():
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        os.makedirs(SCRIPTS_DIR, exist_ok=True)

# Configurações específicas para desenvolvimento
class DevelopmentConfig(Config):
    DEBUG = True

# Configurações específicas para produção
class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Deve ser definido no ambiente

# Configurações específicas para testes
class TestingConfig(Config):
    TESTING = True

# Dicionário para selecionar o ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
