import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from organizador import processar_xml

ctk.set_appearance_mode("System")  # "Light", "Dark", or "System"
ctk.set_default_color_theme("blue")

def callback_progresso(atual, total):
    progresso = atual / total
    barra_progresso.set(progresso)

def callback_log(mensagem):
    caixa_logs.insert("end", mensagem + "\n")
    caixa_logs.see("end")


def selecionar_pasta(var):
    caminho = filedialog.askdirectory()
    var.set(caminho)


def iniciar_processamento():
    origem = entrada_origem.get().strip()
    destino = entrada_destino.get().strip()
    data = entrada_data.get().strip()
    tipo = tipo_doc.get()
    acao = acao_arquivo.get()

    if not origem or not destino or not data:
        messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
        return

    botao_iniciar.configure(state="disabled")
    status.set("🔄 Processando...")

    def tarefa():
        try:
            processar_xml(origem, destino, acao, tipo, data)
            status.set("✅ Concluído com sucesso!")
        except Exception as e:
            status.set("❌ Erro no processamento.")
            messagebox.showerror("Erro", str(e))
        finally:
            botao_iniciar.configure(state="normal")

    threading.Thread(target=tarefa).start()


# === Janela principal ===
app = ctk.CTk()
app.title("Organizador de XMLs Fiscais")
app.geometry("600x700")
app.resizable(False, False)

# === Variáveis ===
entrada_origem = ctk.StringVar()
entrada_destino = ctk.StringVar()
entrada_data = ctk.StringVar(value="2024-01-01")
tipo_doc = ctk.StringVar(value="ALL")
acao_arquivo = ctk.StringVar(value="COPIAR")
status = ctk.StringVar(value="🕓 Aguardando...")

# === Layout ===
ctk.CTkLabel(
    app, text="🧾 Organizador de XMLs", font=ctk.CTkFont(size=20, weight="bold")
).pack(pady=15)

frame = ctk.CTkFrame(app)
frame.pack(pady=5, padx=20, fill="both", expand=True)

# Pasta de Origem
ctk.CTkLabel(frame, text="📁 Pasta de Origem").pack(anchor="w", pady=(10, 0))
ctk.CTkEntry(frame, textvariable=entrada_origem, width=460).pack()
ctk.CTkButton(
    frame, text="Selecionar", command=lambda: selecionar_pasta(entrada_origem)
).pack(pady=5)

# Pasta de Destino
ctk.CTkLabel(frame, text="📂 Pasta de Destino").pack(anchor="w", pady=(10, 0))
ctk.CTkEntry(frame, textvariable=entrada_destino, width=460).pack()
ctk.CTkButton(
    frame, text="Selecionar", command=lambda: selecionar_pasta(entrada_destino)
).pack(pady=5)

# Data mínima
ctk.CTkLabel(frame, text="🗓️ Data mínima (AAAA-MM-DD)").pack(anchor="w", pady=(10, 0))
ctk.CTkEntry(frame, textvariable=entrada_data).pack()

# Tipo de Documento
ctk.CTkLabel(frame, text="⚙️ Tipo de Documento").pack(anchor="w", pady=(10, 0))
ctk.CTkOptionMenu(frame, variable=tipo_doc, values=["ALL", "NFE", "MDFE"]).pack()

# Ação
ctk.CTkLabel(frame, text="📌 Ação").pack(anchor="w", pady=(10, 0))
ctk.CTkOptionMenu(frame, variable=acao_arquivo, values=["COPIAR", "MOVER"]).pack()

# Status
ctk.CTkLabel(
    frame,
    textvariable=status,
    text_color="lightblue",
    font=ctk.CTkFont(size=12, weight="normal"),
).pack(pady=10)

# Botão iniciar
botao_iniciar = ctk.CTkButton(
    frame,
    text="🚀 Iniciar Organização",
    command=iniciar_processamento,
    height=40,
    width=220,
    font=ctk.CTkFont(size=14, weight="bold"),
    fg_color="#1e90ff",
    hover_color="#1c86ee",
)
botao_iniciar.pack(pady=10)

ctk.CTkLabel(app,text=None, font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)

# Loop
app.mainloop()
