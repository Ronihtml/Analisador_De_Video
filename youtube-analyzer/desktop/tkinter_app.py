import io
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import sys
import json
import time
import subprocess
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database
import webbrowser

class YouTubeAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Analyzer - Desktop")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configurar tema e estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Usar um tema mais moderno
        
        # Configurar cores
        self.primary_color = "#ff0000"  # Vermelho do YouTube
        self.secondary_color = "#4285f4"  # Azul do Google
        self.bg_color = "#f5f5f5"
        self.text_color = "#333333"
        
        # Configurar estilos personalizados
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TButton", 
                             background=self.primary_color, 
                             foreground="white", 
                             font=("Segoe UI", 10, "bold"),
                             padding=10)
        self.style.map("TButton",
                       background=[("active", "#cc0000"), ("disabled", "#cccccc")],
                       foreground=[("disabled", "#999999")])
        
        self.style.configure("Secondary.TButton", 
                             background=self.secondary_color, 
                             foreground="white")
        self.style.map("Secondary.TButton",
                       background=[("active", "#3367d6")])
        
        self.style.configure("TEntry", padding=10)
        self.style.configure("Heading.TLabel", 
                             font=("Segoe UI", 16, "bold"), 
                             foreground=self.text_color)
        self.style.configure("Subheading.TLabel", 
                             font=("Segoe UI", 12), 
                             foreground=self.text_color)
        
        # Inicializar banco de dados
        self.init_database()
        
        # Criar notebook para abas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Criar abas
        self.home_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.home_frame, text="Analisar Vídeo")
        self.notebook.add(self.history_frame, text="Histórico")
        
        # Configurar abas
        self.setup_home_tab()
        self.setup_history_tab()
        
        # Vincular evento de mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Inicializar variáveis
        self.current_analysis_id = None
        
        # Verificar diretórios necessários
        self.check_directories()

    def init_database(self):
        """Inicializa o banco de dados"""
        try:
            database.inicializar_banco()
            print("Banco de dados inicializado com sucesso")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao inicializar banco de dados: {e}")
    
    def check_directories(self):
        """Verifica se os diretórios necessários existem"""
        os.makedirs('downloads', exist_ok=True)
        os.makedirs('scripts', exist_ok=True)
        os.makedirs('database', exist_ok=True)
    
    def setup_home_tab(self):
        """Configura a aba inicial de análise de vídeos"""
        # Container principal
        main_frame = ttk.Frame(self.home_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        logo_label = ttk.Label(header_frame, text="YouTube", 
                              font=("Segoe UI", 24, "bold"), 
                              foreground=self.primary_color)
        logo_label.pack(side=tk.LEFT)
        
        analyzer_label = ttk.Label(header_frame, text="Analyzer", 
                                  font=("Segoe UI", 24), 
                                  foreground=self.text_color)
        analyzer_label.pack(side=tk.LEFT)
        
        # Descrição
        description = ttk.Label(main_frame, 
                               text="Digite uma URL do YouTube para baixar, transcrever e resumir o conteúdo do vídeo",
                               style="Subheading.TLabel")
        description.pack(fill=tk.X, pady=(0, 20))
        
        # Frame para entrada de URL
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=("Segoe UI", 12))
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.analyze_button = ttk.Button(url_frame, text="Analisar Vídeo", command=self.analyze_video)
        self.analyze_button.pack(side=tk.RIGHT)
        
        # Frame para progresso
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 20))
        self.progress_frame.pack_forget()  # Esconder inicialmente
        
        progress_label = ttk.Label(self.progress_frame, text="Processando Vídeo", style="Subheading.TLabel")
        progress_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Passos do progresso
        self.steps_frame = ttk.Frame(self.progress_frame)
        self.steps_frame.pack(fill=tk.X)
        
        # Criar indicadores de passos
        self.step_indicators = []
        step_texts = ["Baixando áudio do YouTube", 
                     "Transcrevendo áudio com Whisper", 
                     "Gerando resumo"]
        
        for i, text in enumerate(step_texts):
            step_frame = ttk.Frame(self.steps_frame)
            step_frame.pack(fill=tk.X, pady=5)
            
            indicator = ttk.Label(step_frame, text="○", font=("Segoe UI", 14), foreground="#cccccc")
            indicator.pack(side=tk.LEFT, padx=(0, 10))
            
            step_label = ttk.Label(step_frame, text=text)
            step_label.pack(side=tk.LEFT)
            
            self.step_indicators.append((indicator, step_label))
        
        # Frame para erro
        self.error_frame = ttk.Frame(main_frame)
        self.error_frame.pack(fill=tk.X, pady=(0, 20))
        self.error_frame.pack_forget()  # Esconder inicialmente
        
        error_header = ttk.Frame(self.error_frame, style="TFrame")
        error_header.pack(fill=tk.X, pady=(0, 10))
        
        error_icon = ttk.Label(error_header, text="✕", font=("Segoe UI", 14), foreground=self.primary_color)
        error_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        error_title = ttk.Label(error_header, text="Erro", font=("Segoe UI", 12, "bold"), foreground=self.primary_color)
        error_title.pack(side=tk.LEFT)
        
        self.error_message = ttk.Label(self.error_frame, text="", wraplength=600)
        self.error_message.pack(fill=tk.X)
        
        # Frame para resumo
        self.summary_frame = ttk.Frame(main_frame)
        self.summary_frame.pack(fill=tk.BOTH, expand=True)
        self.summary_frame.pack_forget()  # Esconder inicialmente
        
        summary_header = ttk.Frame(self.summary_frame)
        summary_header.pack(fill=tk.X, pady=(0, 10))
        
        summary_title = ttk.Label(summary_header, text="Resumo do Vídeo", style="Subheading.TLabel")
        summary_title.pack(side=tk.LEFT)
        
        self.copy_button = ttk.Button(summary_header, text="Copiar", 
                                     style="Secondary.TButton",
                                     command=self.copy_summary)
        self.copy_button.pack(side=tk.RIGHT)
        
        self.view_details_button = ttk.Button(summary_header, text="Ver Detalhes", 
                                             style="Secondary.TButton",
                                             command=self.view_details)
        self.view_details_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Área de texto para o resumo
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, 
                                                    wrap=tk.WORD, 
                                                    font=("Segoe UI", 11),
                                                    height=10)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        self.summary_text.config(state=tk.DISABLED)  # Inicialmente desabilitado
        
        # Análises recentes
        self.recent_frame = ttk.Frame(main_frame)
        self.recent_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        recent_label = ttk.Label(self.recent_frame, text="Análises Recentes", style="Subheading.TLabel")
        recent_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Lista de análises recentes
        self.recent_list_frame = ttk.Frame(self.recent_frame)
        self.recent_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Carregar análises recentes
        self.load_recent_analyses()
    
    def setup_history_tab(self):
        """Configura a aba de histórico"""
        # Container principal
        main_frame = ttk.Frame(self.history_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Cabeçalho
        header_label = ttk.Label(main_frame, text="Histórico de Análises", style="Heading.TLabel")
        header_label.pack(anchor=tk.W, pady=(0, 10))
        
        description = ttk.Label(main_frame, 
                               text="Veja todas as análises de vídeos realizadas anteriormente",
                               style="Subheading.TLabel")
        description.pack(anchor=tk.W, pady=(0, 20))
        
        # Frame de busca
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 12))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        search_button = ttk.Button(search_frame, text="Buscar", 
                                  style="Secondary.TButton",
                                  command=self.search_analyses)
        search_button.pack(side=tk.RIGHT)
        
        # Frame para lista de análises
        self.analyses_canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        self.analyses_canvas.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.analyses_canvas, orient="vertical", command=self.analyses_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.analyses_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.analyses_frame = ttk.Frame(self.analyses_canvas)
        self.analyses_canvas.create_window((0, 0), window=self.analyses_frame, anchor="nw", tags="self.analyses_frame")
        
        self.analyses_frame.bind("<Configure>", lambda e: self.analyses_canvas.configure(
            scrollregion=self.analyses_canvas.bbox("all")))
        
        # Mensagem quando não há análises
        self.empty_label = ttk.Label(self.analyses_frame, 
                                    text="Nenhuma análise encontrada", 
                                    font=("Segoe UI", 12))
        
        # Carregar análises
        self.load_analyses()
    
    def on_tab_changed(self, event):
        """Manipula o evento de mudança de aba"""
        tab_id = self.notebook.index(self.notebook.select())
        
        if tab_id == 1:  # Aba de histórico
            self.load_analyses()
    
    def load_recent_analyses(self):
        """Carrega as análises recentes na aba inicial"""
        # Limpar frame atual
        for widget in self.recent_list_frame.winfo_children():
            widget.destroy()
        
        # Obter análises recentes
        try:
            analyses = database.listar_analises(limite=5)
            
            if not analyses:
                empty_label = ttk.Label(self.recent_list_frame, 
                                       text="Nenhuma análise recente", 
                                       font=("Segoe UI", 12))
                empty_label.pack(pady=20)
                return
            
            # Criar cards para cada análise
            for analysis in analyses:
                self.create_analysis_card(self.recent_list_frame, analysis, compact=True)
            
        except Exception as e:
            print(f"Erro ao carregar análises recentes: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar análises recentes: {e}")
    
    def load_analyses(self):
        """Carrega todas as análises na aba de histórico"""
        # Limpar frame atual
        for widget in self.analyses_frame.winfo_children():
            widget.destroy()
        
        # Obter análises
        try:
            if hasattr(self, 'search_var') and self.search_var.get():
                analyses = database.buscar_analises(self.search_var.get())
            else:
                analyses = database.listar_analises(limite=50)
            
            if not analyses:
                self.empty_label.pack(pady=20)
                return
            else:
                self.empty_label.pack_forget()
            
            # Criar cards para cada análise
            for analysis in analyses:
                self.create_analysis_card(self.analyses_frame, analysis)
            
        except Exception as e:
            print(f"Erro ao carregar análises: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar análises: {e}")
    
    def create_analysis_card(self, parent, analysis, compact=False):
        """Cria um card para uma análise"""
        card = ttk.Frame(parent, style="TFrame")
        card.pack(fill=tk.X, pady=5, padx=5)
        
        # Adicionar borda
        card_border = ttk.Frame(card, style="TFrame")
        card_border.pack(fill=tk.X, expand=True, padx=1, pady=1)
        
        # Conteúdo do card
        card_content = ttk.Frame(card_border, style="TFrame")
        card_content.pack(fill=tk.X, expand=True)
        
        # Cabeçalho do card
        header = ttk.Frame(card_content, style="TFrame")
        header.pack(fill=tk.X, padx=10, pady=10)
        
        title = ttk.Label(header, 
                         text=analysis['titulo'][:50] + ('...' if len(analysis['titulo']) > 50 else ''),
                         font=("Segoe UI", 12, "bold"))
        title.pack(side=tk.LEFT)
        
        # Formatar data
        try:
            date_obj = datetime.strptime(analysis['data_analise'], '%Y-%m-%d %H:%M:%S.%f')
            date_str = date_obj.strftime('%d/%m/%Y %H:%M')
        except:
            date_str = analysis['data_analise']
        
        date = ttk.Label(header, text=date_str, foreground="#666666")
        date.pack(side=tk.RIGHT)
        
        # Conteúdo do card
        content = ttk.Frame(card_content, style="TFrame")
        content.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Informações
        info = ttk.Frame(content, style="TFrame")
        info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        url_frame = ttk.Frame(info, style="TFrame")
        url_frame.pack(fill=tk.X, pady=2)
        
        url_label = ttk.Label(url_frame, text="URL:", font=("Segoe UI", 10, "bold"))
        url_label.pack(side=tk.LEFT, padx=(0, 5))
        
        url_value = ttk.Label(url_frame, 
                             text=analysis['url'][:40] + ('...' if len(analysis['url']) > 40 else ''),
                             foreground="#4285f4",
                             cursor="hand2")
        url_value.pack(side=tk.LEFT)
        url_value.bind("<Button-1>", lambda e, url=analysis['url']: webbrowser.open(url))
        
        duration_frame = ttk.Frame(info, style="TFrame")
        duration_frame.pack(fill=tk.X, pady=2)
        
        duration_label = ttk.Label(duration_frame, text="Duração:", font=("Segoe UI", 10, "bold"))
        duration_label.pack(side=tk.LEFT, padx=(0, 5))
        
        duration_value = ttk.Label(duration_frame, text=analysis['duracao_video'])
        duration_value.pack(side=tk.LEFT)
        
        # Botões de ação
        if not compact:
            actions = ttk.Frame(content, style="TFrame")
            actions.pack(side=tk.RIGHT)
            
            view_button = ttk.Button(actions, 
                                    text="Ver Detalhes", 
                                    style="Secondary.TButton",
                                    command=lambda id=analysis['id']: self.open_analysis_details(id))
            view_button.pack(side=tk.LEFT, padx=(0, 5))
            
            delete_button = ttk.Button(actions, 
                                      text="Excluir", 
                                      style="TButton",
                                      command=lambda id=analysis['id']: self.delete_analysis(id))
            delete_button.pack(side=tk.LEFT)
        else:
            # Versão compacta para a aba inicial
            view_button = ttk.Button(content, 
                                    text="Ver Detalhes", 
                                    style="Secondary.TButton",
                                    command=lambda id=analysis['id']: self.open_analysis_details(id))
            view_button.pack(side=tk.RIGHT)
    
    def analyze_video(self):
        """Inicia o processo de análise de vídeo"""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showerror("Erro", "Por favor, digite uma URL do YouTube")
            return
        
        if not ("youtube.com" in url or "youtu.be" in url):
            messagebox.showerror("Erro", "Por favor, digite uma URL válida do YouTube")
            return
        
        # Resetar UI
        self.reset_ui()
        
        # Mostrar progresso
        self.progress_frame.pack(fill=tk.X, pady=(0, 20))
        self.update_step_status(0)
        
        # Desabilitar botão de análise
        self.analyze_button.config(state=tk.DISABLED)
        
        # Iniciar análise em uma thread separada
        threading.Thread(target=self.run_analyzer, args=(url,), daemon=True).start()
    
    def run_analyzer(self, url):
        """Executa o analisador em uma thread separada"""
        try:
            # Limpar arquivos de processamento anteriores
            for arquivo in ["processamento_concluido.txt", "resultado_completo.json", "ultimo_resumo.txt"]:
                caminho = os.path.join("downloads", arquivo)
                if os.path.exists(caminho):
                    os.remove(caminho)
            
            # Caminho para o script Python
            script_path = os.path.join(os.getcwd(), 'scripts', 'youtube_analyzer.py')
            
            if not os.path.exists(script_path):
                self.show_error("Script de análise não encontrado")
                return
            
            # Executar o script Python como um processo separado
            process = subprocess.Popen(
                [sys.executable, script_path, url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Ler a saída do processo em tempo real
            for line in process.stdout:
                print(f"Script output: {line.strip()}")
                
                if "Baixando áudio do YouTube" in line or "Baixando áudio do vídeo" in line:
                    self.root.after(0, lambda: self.update_step_status(0))
                elif "Transcrevendo áudio" in line or "Iniciando transcrição do áudio" in line:
                    self.root.after(0, lambda: self.update_step_status(1))
                elif "Gerando resumo do conteúdo" in line:
                    self.root.after(0, lambda: self.update_step_status(2))
            
            # Aguardar a conclusão do processo
            process.wait()
            
            # Ler qualquer erro do processo
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"Erro do processo: {stderr_output}")
            
            # Verificar se houve erro no processo
            if process.returncode != 0:
                self.root.after(0, lambda: self.show_error(f"Erro ao processar o vídeo: {stderr_output}"))
                return
            
            # Aguardar até que o arquivo de sinalização seja criado (máximo 30 segundos)
            max_wait = 30
            wait_time = 0
            while not os.path.exists(os.path.join("downloads", "processamento_concluido.txt")) and wait_time < max_wait:
                time.sleep(1)
                wait_time += 1
            
            if not os.path.exists(os.path.join("downloads", "processamento_concluido.txt")):
                self.root.after(0, lambda: self.show_error("Tempo limite excedido ao processar o vídeo"))
                return
            
            # Ler o resumo do arquivo JSON
            resumo_texto = ""
            titulo_video = ""
            duracao = ""
            
            try:
                resultado_file = os.path.join("downloads", "resultado_completo.json")
                if os.path.exists(resultado_file):
                    with open(resultado_file, "r", encoding="utf-8") as f:
                        resultado = json.load(f)
                        resumo_texto = resultado.get("resumo", "")
                        titulo_video = resultado.get("titulo", "")
                        duracao = resultado.get("duracao", "")
            except Exception as e:
                print(f"Erro ao ler arquivo JSON: {e}")
                
                # Tentar ler do arquivo de texto simples
                try:
                    resumo_file = os.path.join("downloads", "ultimo_resumo.txt")
                    if os.path.exists(resumo_file):
                        with open(resumo_file, "r", encoding="utf-8") as f:
                            resumo_texto = f.read()
                except Exception as e:
                    print(f"Erro ao ler arquivo de texto: {e}")
            
            # Se temos um resumo, mostre-o
            if resumo_texto:
                # Salvar no banco de dados
                analise_id = database.salvar_analise(
                    url=url,
                    titulo=titulo_video or "Vídeo de teste",
                    resumo=resumo_texto,
                    duracao_video=duracao or "5:00"
                )
                
                self.current_analysis_id = analise_id
                
                # Mostrar o resumo na interface
                self.root.after(0, lambda: self.show_summary(resumo_texto))
                
                # Atualizar a lista de análises recentes
                self.root.after(0, self.load_recent_analyses)
            else:
                # Se não encontramos o resumo, gere uma mensagem de erro
                resumo_texto = "Não foi possível gerar um resumo detalhado para este vídeo. O YouTube pode estar bloqueando o acesso ao conteúdo."
                
                # Salvar no banco de dados mesmo assim
                analise_id = database.salvar_analise(
                    url=url,
                    titulo=titulo_video or "Título não disponível",
                    resumo=resumo_texto,
                    duracao_video=duracao or "Desconhecida"
                )
                
                self.current_analysis_id = analise_id
                
                # Mostrar o resumo na interface
                self.root.after(0, lambda: self.show_summary(resumo_texto))
                
                # Atualizar a lista de análises recentes
                self.root.after(0, self.load_recent_analyses)
            
        except Exception as e:
            print(f"Erro ao executar o analisador: {e}")
            self.root.after(0, lambda: self.show_error(str(e)))
        finally:
            # Reabilitar botão de análise
            self.root.after(0, lambda: self.analyze_button.config(state=tk.NORMAL))
    
    def update_step_status(self, current_step):
        """Atualiza o status dos passos de progresso"""
        for i, (indicator, label) in enumerate(self.step_indicators):
            if i < current_step:
                # Completado
                indicator.config(text="✓", foreground="#4caf50")
                label.config(foreground=self.text_color)
            elif i == current_step:
                # Ativo
                indicator.config(text="●", foreground=self.secondary_color)
                label.config(foreground=self.text_color)
            else:
                # Pendente
                indicator.config(text="○", foreground="#cccccc")
                label.config(foreground="#666666")
    
    def show_error(self, message):
        """Mostra uma mensagem de erro"""
        self.progress_frame.pack_forget()
        self.summary_frame.pack_forget()
        
        self.error_frame.pack(fill=tk.X, pady=(0, 20))
        self.error_message.config(text=message)
    
    def show_summary(self, summary_text):
        """Mostra o resumo do vídeo"""
        self.progress_frame.pack_forget()
        self.error_frame.pack_forget()
        
        self.summary_frame.pack(fill=tk.BOTH, expand=True)
        
        # Atualizar texto do resumo
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary_text)
        self.summary_text.config(state=tk.DISABLED)
        
        # Marcar todos os passos como concluídos
        self.update_step_status(3)
    
    def reset_ui(self):
        """Reseta a interface do usuário"""
        self.progress_frame.pack_forget()
        self.error_frame.pack_forget()
        self.summary_frame.pack_forget()
    
    def copy_summary(self):
        """Copia o resumo para a área de transferência"""
        summary_text = self.summary_text.get(1.0, tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(summary_text)
        
        # Mostrar mensagem de confirmação
        messagebox.showinfo("Copiado", "Resumo copiado para a área de transferência!")
    
    def view_details(self):
        """Abre a tela de detalhes da análise atual"""
        if self.current_analysis_id:
            self.open_analysis_details(self.current_analysis_id)
    
    def open_analysis_details(self, analysis_id):
        """Abre uma janela com os detalhes da análise"""
        try:
            analysis = database.obter_analise(analysis_id)
            if not analysis:
                messagebox.showerror("Erro", "Análise não encontrada")
                return
            
            # Criar janela de detalhes
            details_window = tk.Toplevel(self.root)
            details_window.title("Detalhes da Análise")
            details_window.geometry("800x600")
            details_window.minsize(700, 500)
            
            # Container principal
            main_frame = ttk.Frame(details_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Cabeçalho
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 20))
            
            title_label = ttk.Label(header_frame, 
                                   text=analysis['titulo'], 
                                   font=("Segoe UI", 16, "bold"),
                                   wraplength=700)
            title_label.pack(anchor=tk.W)
            
            # Formatar data
            try:
                date_obj = datetime.strptime(analysis['data_analise'], '%Y-%m-%d %H:%M:%S.%f')
                date_str = date_obj.strftime('%d/%m/%Y %H:%M')
            except:
                date_str = analysis['data_analise']
            
            date_label = ttk.Label(header_frame, 
                                  text=f"Analisado em: {date_str}", 
                                  foreground="#666666")
            date_label.pack(anchor=tk.W)
            
            # Informações do vídeo
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(fill=tk.X, pady=(0, 20))
            
            url_frame = ttk.Frame(info_frame)
            url_frame.pack(fill=tk.X, pady=2)
            
            url_label = ttk.Label(url_frame, text="URL do Vídeo:", font=("Segoe UI", 10, "bold"))
            url_label.pack(side=tk.LEFT, padx=(0, 5))
            
            url_value = ttk.Label(url_frame, 
                                 text=analysis['url'],
                                 foreground="#4285f4",
                                 cursor="hand2",
                                 wraplength=700)
            url_value.pack(side=tk.LEFT)
            url_value.bind("<Button-1>", lambda e, url=analysis['url']: webbrowser.open(url))
            
            duration_frame = ttk.Frame(info_frame)
            duration_frame.pack(fill=tk.X, pady=2)
            
            duration_label = ttk.Label(duration_frame, text="Duração:", font=("Segoe UI", 10, "bold"))
            duration_label.pack(side=tk.LEFT, padx=(0, 5))
            
            duration_value = ttk.Label(duration_frame, text=analysis['duracao_video'])
            duration_value.pack(side=tk.LEFT)
            
            # Resumo
            summary_frame = ttk.Frame(main_frame)
            summary_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            summary_header = ttk.Frame(summary_frame)
            summary_header.pack(fill=tk.X, pady=(0, 10))
            
            summary_title = ttk.Label(summary_header, 
                                     text="Resumo do Vídeo", 
                                     font=("Segoe UI", 14, "bold"))
            summary_title.pack(side=tk.LEFT)
            
            copy_button = ttk.Button(summary_header, 
                                    text="Copiar", 
                                    style="Secondary.TButton",
                                    command=lambda: self.copy_text_to_clipboard(analysis['resumo']))
            copy_button.pack(side=tk.RIGHT)
            
            # Área de texto para o resumo
            summary_text = scrolledtext.ScrolledText(summary_frame, 
                                                   wrap=tk.WORD, 
                                                   font=("Segoe UI", 11),
                                                   height=10)
            summary_text.pack(fill=tk.BOTH, expand=True)
            summary_text.insert(tk.END, analysis['resumo'])
            summary_text.config(state=tk.DISABLED)
            
            # Botões de ação
            actions_frame = ttk.Frame(main_frame)
            actions_frame.pack(fill=tk.X, pady=(0, 10))
            
            back_button = ttk.Button(actions_frame, 
                                    text="Voltar", 
                                    style="Secondary.TButton",
                                    command=details_window.destroy)
            back_button.pack(side=tk.LEFT)
            
            delete_button = ttk.Button(actions_frame, 
                                      text="Excluir Análise", 
                                      style="TButton",
                                      command=lambda: self.delete_analysis_from_details(analysis_id, details_window))
            delete_button.pack(side=tk.RIGHT)
            
        except Exception as e:
            print(f"Erro ao abrir detalhes da análise: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir detalhes da análise: {e}")
    
    def copy_text_to_clipboard(self, text):
        """Copia um texto para a área de transferência"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        
        # Mostrar mensagem de confirmação
        messagebox.showinfo("Copiado", "Texto copiado para a área de transferência!")
    
    def delete_analysis(self, analysis_id):
        """Exclui uma análise"""
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir esta análise?"):
            try:
                success = database.excluir_analise(analysis_id)
                if success:
                    messagebox.showinfo("Sucesso", "Análise excluída com sucesso!")
                    self.load_analyses()
                    self.load_recent_analyses()
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir a análise")
            except Exception as e:
                print(f"Erro ao excluir análise: {e}")
                messagebox.showerror("Erro", f"Erro ao excluir análise: {e}")
    
    def delete_analysis_from_details(self, analysis_id, details_window):
        """Exclui uma análise a partir da tela de detalhes"""
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir esta análise?"):
            try:
                success = database.excluir_analise(analysis_id)
                if success:
                    messagebox.showinfo("Sucesso", "Análise excluída com sucesso!")
                    details_window.destroy()
                    self.load_analyses()
                    self.load_recent_analyses()
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir a análise")
            except Exception as e:
                print(f"Erro ao excluir análise: {e}")
                messagebox.showerror("Erro", f"Erro ao excluir análise: {e}")
    
    def search_analyses(self):
        """Busca análises pelo termo de busca"""
        self.load_analyses()

if __name__ == "__main__":
    # Configurar saída para UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    # Iniciar aplicação
    root = tk.Tk()
    app = YouTubeAnalyzerApp(root)
    root.mainloop()
