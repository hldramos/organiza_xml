import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from organizador import processar_xml  # Certifique-se de que este arquivo esteja no mesmo diretório

def selecionar_pasta_origem():
    caminho = filedialog.askdirectory()
    entrada_origem.set(caminho)

def selecionar_pasta_destino():
    caminho = filedialog.askdirectory()
    entrada_destino.set(caminho)

def iniciar_processamento():
    origem = entrada_origem.get().strip()
    destino = entrada_destino.get().strip()
    funcao = var_acao.get()
    tipo = var_tipo.get()
    data = entrada_data.get().strip()

    if not origem or not destino or not data:
        messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
        return

    botao_iniciar.config(state="disabled")
    status.set("⏳ Processando XMLs...")

    def tarefa():
        try:
            processar_xml(origem, destino, funcao, tipo, data)
            status.set("✅ Processamento concluído com sucesso!")
        except Exception as e:
            status.set("❌ Ocorreu um erro.")
            messagebox.showerror("Erro", str(e))
        finally:
            botao_iniciar.config(state="normal")

    threading.Thread(target=tarefa).start()

# === Janela principal ===
janela = tk.Tk()
janela.title("Organizador de XMLs Fiscais")
janela.geometry("560x410")
janela.resizable(False, False)

# === Variáveis ===
entrada_origem = tk.StringVar()
entrada_destino = tk.StringVar()
entrada_data = tk.StringVar(value="2024-01-01")
var_tipo = tk.StringVar(value="ALL")
var_acao = tk.StringVar(value="COPIAR")
status = tk.StringVar(value="🟡 Aguardando...")

# === Título ===
tk.Label(janela, text="🧾 Organizador de XMLs Fiscais", font=("Arial", 14, "bold")).pack(pady=10)

# === Pasta de origem ===
tk.Label(janela, text="📁 Pasta de Origem:").pack(anchor="w", padx=20)
tk.Entry(janela, textvariable=entrada_origem, width=60).pack(padx=20)
tk.Button(janela, text="Selecionar", command=selecionar_pasta_origem).pack(pady=5)

# === Pasta de destino ===
tk.Label(janela, text="📂 Pasta de Destino:").pack(anchor="w", padx=20)
tk.Entry(janela, textvariable=entrada_destino, width=60).pack(padx=20)
tk.Button(janela, text="Selecionar", command=selecionar_pasta_destino).pack(pady=5)

# === Data mínima ===
tk.Label(janela, text="🗓️ Data mínima de emissão (AAAA-MM-DD):").pack(anchor="w", padx=20)
tk.Entry(janela, textvariable=entrada_data, width=20).pack(padx=20, anchor="w", pady=5)

# === Tipo de documento ===
tk.Label(janela, text="⚙️ Tipo de Documento:").pack(anchor="w", padx=20)
tk.OptionMenu(janela, var_tipo, "ALL", "NFE", "MDFE").pack(padx=20, anchor="w")

# === Ação: Copiar ou Mover ===
tk.Label(janela, text="📌 Ação:").pack(anchor="w", padx=20, pady=(10, 0))
tk.OptionMenu(janela, var_acao, "COPIAR", "MOVER").pack(padx=20, anchor="w")

# === Botão Iniciar ===
botao_iniciar = tk.Button(janela, text="🚀 Iniciar Organização", command=iniciar_processamento, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
botao_iniciar.pack(pady=15)

# === Status ===
tk.Label(janela, textvariable=status, fg="blue", font=("Arial", 10, "italic")).pack(pady=10)

# === Iniciar loop ===
janela.mainloop()
