import socket
import zipfile
import os
from threading import Thread
from utils.constants import *
from utils.global_config import thread_buffer
import numpy as np

class Receiver:
  client = None
  host = HOST
  port = PORT
  is_done = False
  
  def __init__(self, host=HOST, port=PORT) -> None:
    self.host = host
    self.port = port
    self.client = socket.socket()
    print('[+] Client socket is created.')
  
  def start_session(self):
    self.client.bind(('', self.port))
    print('[+] Socket is binded to {}'.format(self.port))
  
  def send_data(self, file_name):
    self.client.send(file_name.encode())
    f = open(file_name, 'rb')
    l = f.read()
    self.client.sendall(l)
    f.close()

  def listen(self, num_of_slayer=1):
    self.client.listen(num_of_slayer)
    print('[+] Waiting for connection...')
    # self.receive_data()

  def handle_read(self, connection, address, callback_fn=None):
    print('[+] Got connection from {}'.format(address[0]))
    msg = connection.recv(1024).decode()
    if msg == '##':
      self.is_done = True
      return
    filename = msg
    f = open(filename, 'wb')
    l = connection.recv(1024)
    while(l):
      f.write(l)
      l = connection.recv(1024)
    f.close()
    with zipfile.ZipFile(filename, 'r') as file:
      # file.printdir()
      print(file.namelist())
      images = file.namelist()
      file.extractall()
    
    if callback_fn != None:
      images = np.unique(images)
      callback_fn(images)
    connection.close()
    os.remove(filename)

  def receive_data(self, callback_fn=None):
    try:
      while not self.is_done:
        print('[+] Waiting for receiving...')
        con, addr = self.client.accept()
        thread = Thread(target=self.handle_read, args=(con, addr, callback_fn))
        thread.start()
        thread.join()
    except KeyboardInterrupt:
      return

  def end_session(self):
    self.client.close()
