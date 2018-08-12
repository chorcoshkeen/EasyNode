import pickle
import paramiko
class server(object):
    def __init__(self, server_ip, username, password, port = "22"):
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.server_ip = server_ip
        self.username = username
        self.password = password
        self.port = port
        self.name = server_ip

    def __str__(self):
        server = [self.server_ip, self.username, self.password, self.port]
        return server

class SSH(server):
    def __init__(self, server_ip, username, password, port = "22"):
        self.server_ip = server_ip
        self.username = username
        self.password = password
        self.port = port
        super().__init__(self.server_ip, self.username, self.password, self.port)
        self.conn.connect(self.server_ip, self.port,  self.username, self.password)
        print("Init complited")

    def server_command(self, command):
        self.stdin, self.stdout, self.stderr = self.conn.exec_command(command)
        print("Command sended:" + command)

    def addnodes(self, nodes, coin_cli):
        self.nodes = nodes
        for i in self.nodes:
            self.server_command(coin_cli + " addnode " +  i  +  " add")

    def ftp_send_file(self, filename):
        self.filename = filename
        ftpconn=self.conn.open_sftp()
        ftpconn.put(filename, filename)


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()        

def read_servers():
    try: 
        f = open("servers.dat", "rb")
        serversz = pickle.load(f)
    except:
        f = open("servers.dat", "wb")
        serversz = []
    f.close()
    return serversz

def add_server(added_server):
    serversz = read_servers()
    serversz.append(added_server)
    f = open("servers.dat", "wb")
    pickle.dump(serversz, f)
    f.close()

def del_server(deleted_server):
    new_servers = []
    serversz = read_servers()
    for i in serversz:
        if i.name == deleted_server:
            pass
        else:
            new_servers.append(i)
    f = open("servers.dat", "wb")
    pickle.dump(new_servers, f)
    f.close()



