import socket
import os
from datetime import datetime
import threading

class mirror:
    nome_pasta_logs = 'log_mirror'
    nome_arquivo_log = 'log_' + str(datetime.now().replace(microsecond=0)).replace(' ', '_').replace(':', '').replace(
        '-', '') + '.txt'
    rcv = ''
    try:
        os.mkdir(nome_pasta_logs)
    except:
        pass

    arquivo_cfg = open('config.txt', 'r')
    arquivo_log = open(nome_pasta_logs+'//'+nome_arquivo_log,'w',0)

    porta_tcp_receber = int(arquivo_cfg.readline().replace('porta_tcp_receber','').replace(' ','').replace('=',''))
    porta_tcp_enviar = int(arquivo_cfg.readline().replace('porta_tcp_enviar=','').replace(' ','').replace('=',''))
    arquivo_cfg.close()

    print "Escutando porta TCP: "+ str(porta_tcp_receber)
    print "Redirecionando para porta TCP: "+ str(porta_tcp_enviar)

    def start_recebe(self):
        # Criando socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Servidor
        server_address = ('localhost', self.porta_tcp_receber)
        sock.bind(server_address)
        sock.listen(1)
        while True:
            connection, client_address = sock.accept()
            try:
                while True:
                    self.pct = connection.recv(1024)
                    if self.pct:
                        print "Recebido: " + self.prefixo_log(server_address)+ " " + self.pct
                        self.arquivo_log.write(self.prefixo_log(server_address) + self.pct)
                    else:
                        self.arquivo_log.write(self.prefixo_log(server_address) + 'conexao encerrada pelo cliente: ' + client_address)
                        break
            finally:
                connection.close()

    def start_envia(self):
        while True:
            # Criando socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Cliente
            client_address = ('localhost', self.porta_tcp_enviar)
            sock = socket.create_connection(client_address)
            while True:
                try:
                    if self.pct:
                        sock.send(self.pct)
                        print 'Enviado: ' + self.prefixo_log(client_address)+' '+self.pct
                finally:
                    sock.close()

    @staticmethod
    def prefixo_log(self,server_address):
        prefixo = str(server_address) + ' ' + str(datetime) + ': '
        return prefixo


if __name__ == "__main__":
    mirror = mirror()
    thread_recebe = threading.Thread(target=mirror.start_recebe)
    thread_envia = threading.Thread(target=mirror.start_envia)
    thread_recebe.start()
    thread_envia.start()
