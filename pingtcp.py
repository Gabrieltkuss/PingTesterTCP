import socket
import time
import customtkinter as vk
from tkinter import *
import threading
from queue import Queue

def tcp_ping():
    host = ipEntry.get()
    port = int(portEntry.get())

    logBox.delete(1.0, END)

    global stop_test
    stop_test = False

    # Variáveis para armazenar métricas
    pings = []
    packet_loss_count = 0
    packet_sent_count = 0

    # Fila para atualizar a interface gráfica
    log_queue = Queue()

    def update_log():
        while not log_queue.empty():
            message = log_queue.get()
            logBox.insert(END, message)
            logBox.see(END)

        if not stop_test:
            logBox.after(100, update_log)  # Verifica a fila novamente após 100ms

    def send_pings():
        nonlocal packet_sent_count, packet_loss_count

        while not stop_test:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)

                start_time = time.time()
                s.connect((host, port))
                end_time = time.time()

                rtt = (end_time - start_time) * 1000
                pings.append(rtt)

                message = f"Pacote SYN enviado para {host}:{port}.\n Tempo de retorno: {rtt:.6f} ms.\n"
                log_queue.put(message)

            except Exception as e:
                packet_loss_count += 1
                message = f"Erro ao enviar pacote SYN para {host}:{port}: {e}\n"
                log_queue.put(message)
            finally:
                packet_sent_count += 1
                s.close()

            time.sleep(1)

    global ping_thread
    ping_thread = threading.Thread(target=send_pings)
    ping_thread.start()

    logBox.after(100, update_log)  # Inicia a verificação da fila

    def calculate_metrics():
        nonlocal packet_sent_count, packet_loss_count

        if packet_sent_count > 0:
            packet_loss_percent = (packet_loss_count / packet_sent_count) * 100
        else:
            packet_loss_percent = 0

        if pings:
            min_ping = min(pings)
            max_ping = max(pings)
            avg_ping = sum(pings) / len(pings)
        else:
            min_ping = max_ping = avg_ping = 0

        metrics = f"""
        Resultados:
        -------------
        Pacotes Enviados: {packet_sent_count}
        Pacotes Perdidos: {packet_loss_count}
        Porcentagem de Perda de Pacotes: {packet_loss_percent:.2f}%
        Ping Mínimo: {min_ping:.2f} ms
        Ping Médio: {avg_ping:.2f} ms
        Ping Máximo: {max_ping:.2f} ms
        """
        log_queue.put(metrics)

    def stop_and_calculate():
        global stop_test
        stop_test = True
        ping_thread.join()
        calculate_thread = threading.Thread(target=calculate_metrics)
        calculate_thread.start()

    stopButton.configure(command=stop_and_calculate)

def stop_test():
    global stop_test
    stop_test = True
    ping_thread.join()

def clear_logs():
    logBox.delete(1.0, END)

def on_enter(event):
    tcp_ping_threaded()

def tcp_ping_threaded():
    threading.Thread(target=tcp_ping).start()

def clearButton_threaded():
    threading.Thread(target=clear_logs).start()

ipp = vk.CTk()
ipp.title("Pinger TCP Tester")
vk.set_appearance_mode("dark")
vk.set_default_color_theme("dark-blue")
ipp.geometry("550x300")
ipp.resizable(False, False)
ipp.attributes("-alpha", 0.9)

ipLabel = vk.CTkLabel(ipp, text="IP:", font=("Century Gothic", 20), fg_color="transparent")
ipLabel.place(x=95, y=10)

ipEntry = vk.CTkEntry(ipp, width=200, fg_color="black")
ipEntry.place(x=120, y=15)

portLabel = vk.CTkLabel(ipp, text="Porta:", font=("Century Gothic", 20), fg_color="transparent")
portLabel.place(x=61, y=40)

portEntry = vk.CTkEntry(ipp, width=100, fg_color="black")
portEntry.place(x=120, y=45)
portEntry.bind("<Return>", on_enter)

testButton = vk.CTkButton(ipp, text="Iniciar Teste", width=100, fg_color="#002663", command=lambda: tcp_ping_threaded())
testButton.place(x=15, y=80)

stopButton = vk.CTkButton(ipp, text="Parar Teste", width=100, fg_color="#8b0000", command=lambda: stop_test)
stopButton.place(x=15, y=110)

clearButton = vk.CTkButton(ipp, text="Limpar Logs", width=100, fg_color="#8b0000", command=lambda: clearButton_threaded())
clearButton.place(x=15, y=140)

logBox = vk.CTkTextbox(ipp, height=200, width=410, wrap="word")
logBox.place(x=120, y=80)

CreditosLabel = vk.CTkLabel(ipp, text="Desenvolvido por Gabriel Kuss\nIdealizador Saulo Nogueira", font=("Century Gothic", 10), fg_color="transparent")
CreditosLabel.place(x=380, y=5)

ipp.mainloop()
