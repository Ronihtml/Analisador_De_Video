from flask import Flask, render_template, request, Response, jsonify, redirect, url_for
import subprocess
import os
import sys
import json
from threading import Thread
import queue
import time
import database
from pytube import YouTube

app = Flask(__name__)

# Garantir que a pasta scripts existe
os.makedirs('scripts', exist_ok=True)

# Garantir que a pasta downloads existe
os.makedirs('downloads', exist_ok=True)

# Garantir que a pasta database existe
os.makedirs('database', exist_ok=True)

# Inicializar o banco de dados
database.inicializar_banco()

@app.route('/')
def index():
    # Obter as 5 análises mais recentes para mostrar na página inicial
    analises_recentes = database.listar_analises(limite=5)
    return render_template('index.html', analises_recentes=analises_recentes)

@app.route('/historico')
def historico():
    analises = database.listar_analises(limite=20)
    return render_template('historico.html', analises=analises)

@app.route('/analise/<int:analise_id>')
def ver_analise(analise_id):
    analise = database.obter_analise(analise_id)
    if analise:
        return render_template('analise.html', analise=analise)
    return redirect(url_for('historico'))

@app.route('/buscar', methods=['GET'])
def buscar():
    termo = request.args.get('termo', '')
    if termo:
        analises = database.buscar_analises(termo)
    else:
        analises = []
    return render_template('busca.html', analises=analises, termo=termo)

@app.route('/excluir/<int:analise_id>', methods=['POST'])
def excluir(analise_id):
    sucesso = database.excluir_analise(analise_id)
    return redirect(url_for('historico'))

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL do YouTube é obrigatória"}), 400
    
    # Criar uma fila para comunicação entre threads
    message_queue = queue.Queue()
    
    def run_analyzer():
        try:
            # Obter informações do vídeo
            try:
                yt = YouTube(url)
                titulo_video = yt.title
                duracao = str(yt.length) + " segundos"
            except Exception as e:
                print(f"Erro ao obter informações do vídeo: {e}")
                titulo_video = "Título não disponível"
                duracao = "Desconhecida"
            
            # Caminho para o script Python
            script_path = os.path.join(os.getcwd(), 'scripts', 'youtube_analyzer.py')
            
            # Executar o script Python como um processo separado
            process = subprocess.Popen(
                [sys.executable, script_path, url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Processar a saída em tempo real
            current_step = 0
            resumo_encontrado = False
            resumo_buffer = []
            titulo_encontrado = False
            duracao_encontrada = False
            
            for line in process.stdout:
                print(line, end='')  # Imprimir no console do servidor
                
                if "Baixando áudio do vídeo" in line:
                    current_step = 0
                    message_queue.put(json.dumps({"step": current_step}) + "\n")
                elif "Título do vídeo:" in line:
                    titulo_video = line.replace("Título do vídeo:", "").strip()
                    titulo_encontrado = True
                elif "Duração do vídeo:" in line:
                    duracao = line.replace("Duração do vídeo:", "").strip()
                    duracao_encontrada = True
                elif "Iniciando transcrição do áudio" in line:
                    current_step = 1
                    message_queue.put(json.dumps({"step": current_step}) + "\n")
                elif "Gerando resumo do conteúdo" in line:
                    current_step = 2
                    message_queue.put(json.dumps({"step": current_step}) + "\n")
                elif "=== RESUMO DO VÍDEO ===" in line:
                    resumo_encontrado = True
                    continue  # Pular esta linha e começar a coletar o resumo
                elif resumo_encontrado and not line.startswith("Erro:"):
                    # Coletar linhas após o marcador de resumo
                    resumo_buffer.append(line.strip())
            
            # Se coletamos linhas de resumo, envie-as
            resumo_texto = ""
            if resumo_buffer:
                resumo_texto = " ".join(resumo_buffer)
                message_queue.put(json.dumps({"summary": resumo_texto}) + "\n")
                
                # Salvar no banco de dados
                analise_id = database.salvar_analise(
                    url=url,
                    titulo=titulo_video,
                    resumo=resumo_texto,
                    duracao_video=duracao
                )
                message_queue.put(json.dumps({"analise_id": analise_id}) + "\n")
                
                # Enviar sinal de conclusão para atualizar a UI
                message_queue.put(json.dumps({"step": 3}) + "\n")  # Isso indica que todos os passos foram concluídos
            else:
                # Se não encontramos o resumo nas linhas após o marcador, gere um resumo simples
                resumo_texto = "Não foi possível gerar um resumo detalhado para este vídeo. O YouTube pode estar bloqueando o acesso ao conteúdo."
                message_queue.put(json.dumps({"summary": resumo_texto}) + "\n")
                
                # Salvar no banco de dados mesmo assim
                analise_id = database.salvar_analise(
                    url=url,
                    titulo=titulo_video,
                    resumo=resumo_texto,
                    duracao_video=duracao
                )
                message_queue.put(json.dumps({"analise_id": analise_id}) + "\n")
                
                # Enviar sinal de conclusão para atualizar a UI
                message_queue.put(json.dumps({"step": 3}) + "\n")
            
            # Verificar erros
            stderr_output = process.stderr.read()
            if stderr_output and not "FP16 is not supported" in stderr_output:  # Ignorar o aviso FP16
                print(f"Erro: {stderr_output}")
                if "403: Forbidden" in stderr_output:
                    message_queue.put(json.dumps({"error": "O YouTube está bloqueando o download deste vídeo. Tente outro vídeo ou tente novamente mais tarde."}) + "\n")
                else:
                    message_queue.put(json.dumps({"error": stderr_output}) + "\n")
            
            # Verificar código de saída
            process.wait()
            if process.returncode != 0 and not resumo_texto:
                message_queue.put(json.dumps({"error": f"Processo saiu com código {process.returncode}"}) + "\n")
            
            # Sinalizar o fim da fila
            message_queue.put(None)
            
        except Exception as e:
            print(f"Erro ao executar o analisador: {e}")
            message_queue.put(json.dumps({"error": str(e)}) + "\n")
            message_queue.put(None)
    
    # Iniciar o processamento em uma thread separada
    thread = Thread(target=run_analyzer)
    thread.daemon = True
    thread.start()
    
    # Função geradora para streaming da resposta
    def generate():
        while True:
            message = message_queue.get()
            if message is None:
                break
            yield message
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/favicon.ico')
def favicon():
    # Retornar um favicon vazio para evitar o erro 404
    return '', 204

@app.errorhandler(Exception)
def handle_error(e):
    print(f"Erro na aplicação: {e}")
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
