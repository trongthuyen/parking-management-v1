import socket

class Transmitter:
  client = None
  host = '127.0.0.1'
  port = 1337
  
  def __init__(self, host='127.0.0.1', port=1337) -> None:
    self.host = host
    self.port = port
    self.client = socket.socket()
    print('[+] Client socket is created.')
  
  def start_session(self):
    self.client.connect((self.host, self.port))
    print('[+] Socket is connected to {}'.format(self.host))
  
  def send_data(self, file_name, src_path=''):
    print('[CLIENT]: START - Sending...')
    self.client.send(file_name.encode())
    if file_name == '##':
      return
    src_file = src_path if len(src_path) else file_name
    f = open(src_file, 'rb')
    l = f.read()
    self.client.send(l)
    f.close()
    print('[CLIENT]: END - Sending...')
  
  def end_session(self):
    self.client.close()
