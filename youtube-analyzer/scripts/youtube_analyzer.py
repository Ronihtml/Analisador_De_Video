import sys
import os
from pytube import YouTube
import whisper
import yt_dlp
import re
from collections import Counter
import string

def baixar_audio(url, output_path='./downloads'):
    """Baixa o áudio de um vídeo do YouTube usando yt-dlp."""
    try:
        # Garantir que o diretório de saída existe
        os.makedirs(output_path, exist_ok=True)
        
        print(f"Baixando áudio do vídeo: {url}")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, "%(title)s.%(ext)s"),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            arquivo_baixado = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            print(f"Áudio baixado com sucesso: {arquivo_baixado}")
            return arquivo_baixado
    except Exception as e:
        print(f"Erro ao baixar o áudio: {e}")
        sys.exit(1)

def transcrever_audio(arquivo_audio):
    """Transcreve o áudio para texto usando o modelo Whisper."""
    try:
        print("Iniciando transcrição do áudio com Whisper...")
        # Carrega o modelo pequeno do Whisper (menor e mais rápido)
        model = whisper.load_model("base")
        # Transcreve
        result = model.transcribe(arquivo_audio)
        transcricao = result["text"]
        print("Transcrição concluída!")
        return transcricao
    except Exception as e:
        print(f"Erro na transcrição: {e}")
        sys.exit(1)

def gerar_resumo_simples(texto, max_sentencas=10):
    """Gera um resumo simples do texto usando frequência de palavras."""
    print("Gerando resumo do conteúdo...")
    
    # Se o texto for muito curto, retorná-lo como resumo
    if len(texto) < 200:
        return texto
    
    # Remover pontuação e converter para minúsculas
    texto_limpo = texto.lower()
    for p in string.punctuation:
        texto_limpo = texto_limpo.replace(p, '')
    
    # Dividir em palavras e remover palavras comuns (stop words)
    palavras = texto_limpo.split()
    stop_words = ['e', 'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'das', 'dos', 
                 'em', 'na', 'no', 'nas', 'nos', 'para', 'por', 'pelo', 'pela', 'que', 
                 'com', 'como', 'mas', 'ou', 'se', 'porque', 'quando', 'onde', 'quem',
                 'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas', 'meu', 'minha',
                 'seu', 'sua', 'este', 'esta', 'isso', 'aquilo', 'é', 'são', 'foi', 'foram']
    
    palavras_filtradas = [p for p in palavras if p not in stop_words and len(p) > 2]
    
    # Contar frequência das palavras
    frequencia = Counter(palavras_filtradas)
    palavras_importantes = [palavra for palavra, _ in frequencia.most_common(20)]
    
    # Dividir o texto em sentenças
    sentencas = re.split(r'[.!?]+', texto)
    sentencas = [s.strip() for s in sentencas if len(s.strip()) > 10]
    
    # Pontuar sentenças com base nas palavras importantes
    pontuacao_sentencas = []
    for sentenca in sentencas:
        pontuacao = 0
        for palavra in palavras_importantes:
            if palavra.lower() in sentenca.lower():
                pontuacao += 1
        pontuacao_sentencas.append((sentenca, pontuacao))
    
    # Ordenar sentenças por pontuação
    sentencas_ordenadas = sorted(pontuacao_sentencas, key=lambda x: x[1], reverse=True)
    
    # Selecionar as melhores sentenças (limitado pelo max_sentencas)
    melhores_sentencas = [s[0] for s in sentencas_ordenadas[:max_sentencas]]
    
    # Reordenar as sentenças na ordem original do texto
    ordem_original = []
    for sentenca in melhores_sentencas:
        try:
            indice = texto.index(sentenca)
            ordem_original.append((indice, sentenca))
        except ValueError:
            # Se não encontrar a sentença exata, tente uma correspondência aproximada
            for s in sentencas:
                if sentenca in s:
                    try:
                        indice = texto.index(s)
                        ordem_original.append((indice, sentenca))
                        break
                    except ValueError:
                        pass
    
    ordem_original.sort()
    resumo = '. '.join([s[1] for s in ordem_original])
    
    # Garantir que o resumo termina com ponto final
    if resumo and not resumo.endswith('.'):
        resumo += '.'
    
    return resumo

def analisar_video(url_video):
    """Função principal que coordena a análise do vídeo."""
    print(f"Iniciando análise do vídeo: {url_video}")
    
    # Etapa 1: Baixar o áudio
    arquivo_audio = baixar_audio(url_video)
    
    # Etapa 2: Transcrever o áudio
    transcricao = transcrever_audio(arquivo_audio)
    
    # Etapa 3: Gerar resumo
    resumo = gerar_resumo_simples(transcricao)
    
    print("\n=== RESUMO DO VÍDEO ===")
    print(resumo)
    return resumo

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url_video = sys.argv[1]
        analisar_video(url_video)
    else:
        url_video = input("Digite a URL do vídeo do YouTube: ")
        analisar_video(url_video)

