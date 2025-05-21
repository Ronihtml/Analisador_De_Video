# YouTube Video Analyzer

## Sobre o Projeto

Este projeto permite aos usuários fornecer uma URL de vídeo do YouTube e obter:
- Download automático do áudio
- Transcrição do conteúdo usando o modelo Whisper da OpenAI
- Resumo automático do conteúdo

O aplicativo processa tudo em tempo real e mostra o progresso ao usuário através de uma interface amigável.

## Tecnologias Utilizadas

- **Backend**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Processamento de Áudio**: pytube, yt-dlp
- **Transcrição**: OpenAI Whisper
- **Resumo de Texto**: Algoritmo de extração baseado em frequência de palavras

## Pré-requisitos

- Python 3.8+
- FFmpeg (para processamento de áudio)
- Conta de desenvolvedor YouTube (opcional, para alto volume de solicitações)

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/youtube-analyzer.git
   cd youtube-analyzer
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   # No Windows
   venv\Scripts\activate
   # No Linux/MacOS
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Instale o FFmpeg (se ainda não tiver):
   - **Windows**: Baixe de [ffmpeg.org](https://ffmpeg.org/download.html) e adicione ao PATH
   - **MacOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

## Uso

1. Inicie o servidor Flask:
   ```bash
   python main.py
   ```

2. Abra seu navegador e acesse:
   ```
   http://localhost:5000
   ```

3. Cole a URL do vídeo do YouTube e clique em "Analisar Vídeo"

## Estrutura do Projeto

```
youtube-analyzer/
│   |
├   |__desktop/           # Arquivos (run_desktop, tkinter_app)
|   |
│   ├── static/           # Arquivos estáticos (CSS, JS)
│   ├── templates/        # Templates HTML
│   └── scripts/          # Scripts de processamento web
│
|__ database.py           #Banco De Dados
|
├── downloads/            # Diretório para arquivos baixados(é criado automaticamente)
├── requirements.txt      # Dependências do projeto
├── config.py             # Configurações
└── app.py                # Ponto de entrada da aplicação
```

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar um Pull Request.

1. Faça um Fork do projeto
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contato

Seu Nome - [ronald itaparica dos santos] - email: itaparicaronald@gmail.com

Link do Projeto: [https://github.com/seu-usuario/youtube-analyzer](https://github.com/seu-usuario/youtube-analyzer)
