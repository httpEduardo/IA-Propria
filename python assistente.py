import os
import json
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from transformers import pipeline

KNOWLEDGE_FILE = "knowledge_base.json"

def load_knowledge():
    if os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def save_knowledge(knowledge_base):
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=4)

def interpret_command_local(command, knowledge_base):
    command = command.strip().lower()
    if command in knowledge_base:
        return knowledge_base[command]
    else:
        return None

def generate_response_with_pipeline(user_input, pipe, conversation_history):
    # Instruções do sistema em inglês (troque para português se quiser, lembre que o GPT-2 original é em inglês)
    system_instructions = (
        "You are a helpful, polite, and informative AI assistant. "
        "You speak English and answer user questions in a clear and coherent manner. "
        "Avoid unnecessary repetition. "
        "If the user greets you, greet them back and offer help. "
        "If the user asks about everyday things, the weather, or news, try to give a generic helpful answer. "
        "If you don't know something, say you are not sure, but try to assist anyway."
    )

    short_history = conversation_history[-6:]
    prompt = f"[System]\n{system_instructions}\n\n" + "\n".join(short_history) + f"\nUser: {user_input}\nAI:"

    result = pipe(
        prompt,
        max_length=200,
        do_sample=True,
        top_p=0.9,
        temperature=0.7,
        repetition_penalty=1.2,
        truncation=True
    )

    generated_text = result[0]['generated_text']

    if "AI:" in generated_text:
        parts = generated_text.split("AI:")
        response = parts[-1].strip()
    else:
        response = generated_text.strip()

    response = " ".join(response.split())
    return response

def process_command():
    global log_area, knowledge_base, pipe, conversation_history
    user_input = entry.get().strip()
    if not user_input:
        return

    log_area.insert(tk.END, f"You: {user_input}\n")
    entry.delete(0, tk.END)

    response = interpret_command_local(user_input, knowledge_base)
    if response is not None:
        log_area.insert(tk.END, f"AI: {response}\n")
        conversation_history.append("User: " + user_input)
        conversation_history.append("AI: " + response)
    else:
        response = generate_response_with_pipeline(user_input, pipe, conversation_history)
        log_area.insert(tk.END, f"AI: {response}\n")
        conversation_history.append("User: " + user_input)
        conversation_history.append("AI: " + response)

    log_area.see(tk.END)

def send_command_on_enter(event):
    process_command()

if __name__ == "__main__":
    knowledge_base = load_knowledge()

    # Aqui adicionamos o token fornecido:
    # Substitua "gpt2" pelo modelo privado que você quer acessar.
    # Por exemplo: pipe = pipeline("text-generation", model="username/private-model", use_auth_token="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")
    pipe = pipeline("text-generation", model="gpt2", use_auth_token="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")

    conversation_history = []
    conversation_history.append("AI: Hello! How can I help you?")

    root = tk.Tk()
    root.title("Local AI Assistant")
    root.geometry("600x700")
    root.configure(bg="#2E0249")

    custom_font = ("Arial", 12, "bold")
    entry_bg = "#3E065F"
    entry_fg = "white"
    text_bg = "#5A189A"
    text_fg = "white"
    button_bg = "#9A0680"
    button_fg = "white"

    entry_frame = tk.Frame(root, bg="#2E0249")
    entry_frame.pack(pady=10)

    entry = tk.Entry(entry_frame, width=40, font=custom_font, bg=entry_bg, fg=entry_fg, bd=2, relief="flat", insertbackground="white")
    entry.pack(side=tk.LEFT, padx=10)

    send_button = tk.Button(entry_frame, text="Send", command=process_command, font=custom_font, bg=button_bg, fg=button_fg, relief="flat")
    send_button.pack(side=tk.LEFT)

    log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=25, font=custom_font, bg=text_bg, fg=text_fg, relief="flat")
    log_area.pack(pady=10)
    log_area.insert(tk.END, "AI: Hello! How can I help you?\n")

    entry.bind("<Return>", send_command_on_enter)

    root.mainloop()
