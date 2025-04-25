import tkinter as tk
import sys
import io
from tkinter_app import YouTubeAnalyzerApp

if __name__ == "__main__":
    # Configurar saída para UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    # Iniciar aplicação
    root = tk.Tk()
    app = YouTubeAnalyzerApp(root)
    root.mainloop()