import socket
import os
from datetime import datetime
import threading
from binascii import *

class mirror:

    def __init__(self,porta_tcp_receber,porta_tcp_enviar):
        self.porta_tcp_receber = porta_tcp_receber
        self.porta_tcp_enviar = porta_tcp_enviar
        nome_pasta_logs = 'log_mirror'
        nome_arquivo_log = 'log_' + str(datetime.now().replace(microsecond=0)).replace(' ', '_').replace(':', '').replace(
            '-', '') + '.txt'
        pct = ''
        try:
            os.mkdir(nome_pasta_logs)
        except:
            pass
        self.th_lista = []
        self.arquivo_log = open(nome_pasta_logs+'//'+nome_arquivo_log,'w',0)
        print "Escutando porta TCP: "+ str(self.porta_tcp_receber)
        print "Redirecionando para porta TCP: "+ str(self.porta_tcp_enviar)

    def start_recebe(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', self.porta_tcp_receber)
        sock.bind(server_address)
        sock.listen(1)
        i = 0
        while True:
            try:
                nome_thread = threading.Thread(target = self.cria_lista_conexoes,args=(sock,server_address,  ))
                self.th_lista.append(nome_thread)
                nome_thread.start()
            except:
                pass
            self.finaliza_conexoes(i)
            i = i+1

    def cria_lista_conexoes(self, sock, server_address ):
        while True:
            connection, client_address = sock.accept()
            r_client_address = ('localhost', self.porta_tcp_enviar)
            sock_cliente = socket.create_connection(r_client_address)
            try:
                while True:
                    try:
                        self.pct = connection.recv(1024)
                        if len(self.pct)>0:
                            try:
                                sock_cliente.send(self.pct)
                                th_replica = threading.Thread(target= self.replica_comandos, args=(sock_cliente,connection,client_address,r_client_address, ))
                                th_replica.start()
                                print "Recebido: " + self.prefixo_log(client_address)+ " " + hexlify(self.pct)
                                self.arquivo_log.write("Recebido: " + self.prefixo_log(client_address)+ " " + hexlify(self.pct) +"\n")
                                print 'Enviado: ' + self.prefixo_log(r_client_address)+' '+hexlify(self.pct)
                                self.arquivo_log.write('Enviado: ' + self.prefixo_log(r_client_address)+' '+ hexlify(self.pct)+"\n")
                            except:
                                sock.close()
                                self.th_replica.join(1)
                                break
                                pass
                    except:
                        pass
                        try:
                            connection, client_address = sock_cliente.accept()
                        except:
                            print "conexao encerrada pelo cliente: " + str(client_address)
                            self.arquivo_log.write(self.prefixo_log(server_address) + 'conexao encerrada pelo cliente: ' + str(client_address)+"\n")
                            break

            finally:
                connection.close()

    def replica_comandos(self,sock_cliente,connection,client_address,r_client_address):
        while True:
            try:
                data = sock_cliente.recv(1024)
                connection.send(data)
                self.arquivo_log.write('Enviado de '+ str(r_client_address) + " para " + str(client_address) +': '+ hexlify(data)+"\n")
                print 'Enviado de '+ str(r_client_address) + " para " + str(client_address) +': '+ hexlify(data)
            except:
                pass

    def finaliza_conexoes(self,i):
        if self.th_lista[i].isAlive():
            self.th_lista[i].join(1)

    def prefixo_log(self,server_address):
        prefixo = str(server_address) + ' ' + str(datetime.now()) + ': '
        return prefixo


if __name__ == "__main__":
    nome_arquivo_log = 'log_' + str(datetime.now().replace(microsecond=0)).replace(' ', '_').replace(':', '').replace(
        '-', '') + '.txt'
    arquivo_cfg = open('config.txt', 'r')
    porta_tcp_receber = int(arquivo_cfg.readline().replace('porta_tcp_receber','').replace(' ','').replace('=',''))
    porta_tcp_enviar = int(arquivo_cfg.readline().replace('porta_tcp_enviar=','').replace(' ','').replace('=',''))
    arquivo_cfg.close()
    mirror = mirror(porta_tcp_receber,porta_tcp_enviar)
    thread_recebe = threading.Thread(target=mirror.start_recebe)
    thread_recebe.start()


