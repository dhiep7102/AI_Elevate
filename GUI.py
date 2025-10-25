# gui.py
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from collector import collect_all
from analyzer import summarize_articles
# from notifier import send_email, send_telegram

def run_analysis(topic, output_box, run_button):
    run_button.config(state=tk.DISABLED)
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, f"🚀 Running InsightFlow AI for topic: {topic}\n\n")

    try:
        articles = collect_all(topic)
        if not articles:
            output_box.insert(tk.END, "[Main] No articles found.\n")
            return

        summary = summarize_articles(articles, topic)

        subject = f"InsightFlow AI - {topic.title()} Daily Summary"

        output_box.insert(tk.END, f"✅ Summary generated successfully:\n\n{summary}\n")

        # if send_email_var.get():
        #     send_email(subject, summary)
        #     output_box.insert(tk.END, "\n📧 Email sent.\n")
        #
        # if send_telegram_var.get():
        #     send_telegram(f"📢 {subject}\n\n{summary}")
        #     output_box.insert(tk.END, "\n📲 Telegram message sent.\n")

        output_box.insert(tk.END, "\n✅ Done.\n")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        output_box.insert(tk.END, f"\n❌ Error: {e}\n")

    finally:
        run_button.config(state=tk.NORMAL)

def start_analysis(topic_entry, output_box, run_button):
    topic = topic_entry.get().strip()
    if not topic:
        messagebox.showwarning("Warning", "Please enter a topic first!")
        return

    thread = threading.Thread(
        target=run_analysis,
        args=(topic, output_box, run_button),
        daemon=True
    )
    thread.start()

def create_gui():
    root = tk.Tk()
    root.title("🧠 InsightFlow AI – Real-time News Analyzer")
    root.geometry("720x560")

    ttk.Label(root, text="Enter Topic:", font=("Segoe UI", 11)).pack(pady=10)
    topic_entry = ttk.Entry(root, width=60)
    topic_entry.insert(0, "global economy")
    topic_entry.pack()

    options_frame = ttk.Frame(root)
    options_frame.pack(pady=5)
    # send_email_var = tk.BooleanVar(value=False)
    # send_telegram_var = tk.BooleanVar(value=False)
    # ttk.Checkbutton(options_frame, text="Send Email", variable=send_email_var).grid(row=0, column=0, padx=10)
    # ttk.Checkbutton(options_frame, text="Send Telegram", variable=send_telegram_var).grid(row=0, column=1, padx=10)

    run_button = ttk.Button(root, text="Run Analysis",
        command=lambda: start_analysis(topic_entry, output_box, run_button)
    )
    run_button.pack(pady=10)

    output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=85, height=25, font=("Consolas", 10))
    output_box.pack(padx=10, pady=10)

    ttk.Label(root, text="© 2025 InsightFlow AI", font=("Segoe UI", 9)).pack(side=tk.BOTTOM, pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()


