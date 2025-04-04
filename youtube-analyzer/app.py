from flask import Flask, render_template, request, Response, jsonify
import subprocess
import os
import sys
import json
from threading import Thread
import queue
import time

app = Flask(__name__)

# Garantir que a pasta scripts existe
os.makedirs('scripts', exist_ok=True)

# Garantir que a pasta downloads existe
os.makedirs('downloads', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

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
            
            for line in process.stdout:
                print(line, end='')  # Imprimir no console do servidor
                
                if "Baixando áudio do vídeo" in line:
                    current_step = 0
                    message_queue.put(json.dumps({"step": current_step}) + "\n")
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
            if resumo_buffer:
                resumo_texto = " ".join(resumo_buffer)
                message_queue.put(json.dumps({"summary": resumo_texto}) + "\n")
            else:
                # Se não encontramos o resumo nas linhas após o marcador, gere um resumo simples
                message_queue.put(json.dumps({"summary": "Não foi possível gerar um resumo detalhado. Aqui está um trecho da transcrição."}) + "\n")
            
            # Verificar erros
            stderr_output = process.stderr.read()
            if stderr_output and not "FP16 is not supported" in stderr_output:  # Ignorar o aviso FP16
                print(f"Erro: {stderr_output}")
                message_queue.put(json.dumps({"error": stderr_output}) + "\n")
            
            # Verificar código de saída
            process.wait()
            if process.returncode != 0:
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

@app.errorhandler(Exception)
def handle_error(e):
    print(f"Erro na aplicação: {e}")
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True)

