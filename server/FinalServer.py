'''
DIRSEARCH <directory> <filename>
    DIRSEARCH looks for the file in the given directory or its
    subdirectories. If it finds the file, it sends back the location.
DOWNLOAD <filename>
    DOWNLOAD requires the full file path, or at least the relative path,
    of the file. It sends the contents of the file across the network.
UPLOAD <filename>
    UPLOAD requires the full file path, or at least the relative path,
    where the user wants to locate the file. It reads the file contents
    from across the network connection.
CLOSE
    CLOSE ends the connection

'''

import os, re, socket, threading, struct
from ctypes import *
from urllib import urlopen

def read_file(filename):

    f = open(filename,'r')
    data  = f.read()
    return data

def create_file(filename, data):

    f = open(filename,'w')

    f.write(data)
    f.close()
    return

def recv_data(sock):

    a = sock.recv(4)
    data_len = struct.unpack('!I',a)[0]
    data = sock.recv(data_len)

    return data

def send_data(sock,data):

    data_len = struct.pack('!I',len(data))
    sock.send(data_len)
    sock.send(data)

    return

def search_directory(file_name): #DIRSEARCH

    s = re.compile(file_name)

    for root,dirs,files in os.walk(os.getcwd()): # generator
        for i in files:
            if(re.search(s,i)):
                return os.path.join(root,i)
    return -1

def send_file_contents(file_name,usersock,userinfo): #DOWNLOAD

    data = read_file(file_name)

    send_data(usersock,data)

    return 0

def receive_file_contents(file_name,usersock):#UPLOAD

    data = recv_data(usersock)
    create_file(file_name,data)

    return 0

def handle_connection(usersock,userinfo):


    continua = True

    while(continua == True):

        the_order = recv_data(usersock).upper()

        if(the_order == "DIRSEARCH"):

            data = search_directory(recv_data(usersock))

            if(data == -1):
                send_data(usersock,"FILE NOT FOUND!")
            else:
                send_data(usersock,data)

        if(the_order == "DOWNLOAD"):
            send_file_contents(recv_data(usersock),usersock,userinfo)

        if(the_order == "UPLOAD"):
            receive_file_contents(recv_data(usersock),usersock)

        if(the_order == "CLOSE"):
            continua = False

    return


def main():

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('',10009))
    sock.listen(0)
    conn, addr = sock.accept()
    print "New Client: " + str(addr)

    threading.Thread(None,handle_connection,None,(conn,addr)).start()

    return

main()
