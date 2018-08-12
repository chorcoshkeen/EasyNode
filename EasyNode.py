import sys  
from PyQt5 import QtWidgets, QtCore, QtGui
from ui import *    
import coins
import createSh
import servers
from os import path



class install_thread(QtCore.QThread):
    def __init__(self, server, signal, tab, parent = None):
        super().__init__(parent)
        self.serverlist = servers.read_servers()
        self.signal = signal
        self.server = server
        self.tab = tab

    def run(self):
        def read_data(signal, ssh):
            while True:
                data = self.ssh.stdout.readline()
                if data == "":
                    break
                signal.emit(data)

        try:
            if self.tab == 0:
                self.ssh = servers.SSH(self.serverlist[self.server].server_ip, self.serverlist[self.server].username, self.serverlist[self.server].password, self.serverlist[self.server].port)    
            elif self.tab == 1:
                if self.server[3] == "": self.server[3] = 22
                self.ssh = servers.SSH(self.server[0], self.server[1], self.server[2], self.server[3])
            self.ssh.ftp_send_file("mn.sh")
            self.ssh.server_command("apt-get install dos2unix")             
            read_data(self.signal, self.ssh)
            self.ssh.server_command("dos2unix mn.sh")
            read_data(self.signal, self.ssh)
            self.ssh.server_command("chmod 755 mn.sh")
            self.ssh.server_command("./mn.sh")              
            read_data(self.signal, self.ssh)

        except:
            self.signal.emit("Connection problem..")

class Dialog_masternode_install(QtWidgets.QDialog):
    server_resp_signal  = QtCore.pyqtSignal(str, name='server_resp_signal')

    def __init__(self, parent):
        super().__init__(parent)
        self.dialogUI = Install_masternode_dialog()
        self.dialogUI.setupUi(self)
        self.update_list()
        self.dialogUI.install_button_t1.clicked.connect(self.thread_stop)
        self.dialogUI.install_button_t2.clicked.connect(self.thread_stop)
        self.server_resp_signal.connect(self.logger, QtCore.Qt.QueuedConnection)
        self.dialogUI.cancel_button_t1.clicked.connect(self.install)
        self.dialogUI.cancel_button_t2.clicked.connect(self.install)    

    def update_list(self):
        self.serverlist = servers.read_servers()
        for i in range(len(self.serverlist)):
            self.dialogUI.server_list.addItem(QtWidgets.QListWidgetItem())
            self.dialogUI.server_list.item(i).setText(self.serverlist[i].server_ip)

    def install(self):
        self.tab = self.dialogUI.tabWidget.currentIndex()
        if self.tab == 0:
            self.server = self.dialogUI.server_list.currentRow()
        elif self.tab == 1:
            self.server = []
            self.server.append(self.dialogUI.ip_line.text())
            self.server.append(self.dialogUI.username_line.text())
            self.server.append(self.dialogUI.password_line.text())
            self.server.append(self.dialogUI.port_line.text())
        self.thread = install_thread(self.server, self.server_resp_signal, self.tab)
        self.thread.start()

    def logger(self, data): 
        self.tab = self.dialogUI.tabWidget.currentIndex()
        if self.tab == 0:
            self.log_widget = self.dialogUI.log_t1
        elif self.tab == 1:
            self.log_widget = self.dialogUI.log_t2
        self.log_widget.appendPlainText(data[:-2])
        c = self.log_widget.textCursor()
        c.movePosition(QtGui.QTextCursor.End)
        self.log_widget.setTextCursor(c)
        self.log_widget.ensureCursorVisible()

    def thread_stop(self):
            try:
                self.thread.quit()
                self.thread.terminate()
            except:
                pass
            self.close()

class Dialog_add_server(QtWidgets.QDialog):   
    def __init__(self, parent, update_lists_signal):
        super().__init__(parent)
        self.dialogUi = Ui_Add_server_dialog()
        self.dialogUi.setupUi(self)
        self.dialogUi.buttonBox_2.accepted.connect(self.add_server)
        self.dialogUi.buttonBox_2.rejected.connect(self.close)
        self.update_lists_signal = update_lists_signal

    def add_server(self):
        self.server_ip = self.dialogUi.ip_line.text()
        self.username = self.dialogUi.username_line.text()
        self.password = self.dialogUi.password_line.text()
        self.port = self.dialogUi.port_line.text()
        added_server = servers.server(self.server_ip, self.username, self.password, self.port)
        servers.add_server(added_server)
        self.update_lists_signal.emit("")
        self.close()

class Dialog_add_coin(QtWidgets.QDialog):
    def __init__(self, parent, update_lists_signal):
        super().__init__(parent)
        self.dialogUi = UI_addcoin_dialog()
        self.dialogUi.setupUi(self)
        self.dialogUi.buttonBox.accepted.connect(self.add_coin)
        self.dialogUi.buttonBox.rejected.connect(self.close)
        self.update_lists_signal = update_lists_signal

    def add_coin(self):
        self.name = self.dialogUi.coin_name_line.text()
        self.config_file = self.dialogUi.config_file_line.text()
        self.config_folder = self.dialogUi.config_folder_line.text()
        self.daemon = self.dialogUi.coin_daemon_line.text()
        self.cli = self.dialogUi.coin_cli_name.text()
        self.repo = self.dialogUi.coin_github_line.text()
        self.port = self.dialogUi.lineEdit_7.text()
        added_coin = coins.coin(self.name, self.config_file, self.config_folder, self.daemon, self.cli, self.repo, self.port)
        coins.add_coin(added_coin, "abu")
        self.update_lists_signal.emit("")
        self.close()


class Main_window(QtWidgets.QMainWindow):
    update_lists_signal = QtCore.pyqtSignal(str, name = "update_lists_signal")
    
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.update_lists_signal.connect(self.update_lists, QtCore.Qt.QueuedConnection)

        self.dialog_add_coin = Dialog_add_coin(self, update_lists_signal = self.update_lists_signal)
        self.dialog_mn = Dialog_masternode_install(self)
        self.addserver = Dialog_add_server(self, update_lists_signal = self.update_lists_signal)                

        self.ui.create_sh_button_mp.clicked.connect(self.get_sh)
        self.ui.create_sh_button_ac.clicked.connect(self.get_sh)
        self.ui.create_sh_button_abu.clicked.connect(self.get_sh)

        self.ui.install_masternode_button_mp.clicked.connect(self.masternode_install)
        self.ui.install_masternode_ac.clicked.connect(self.masternode_install)
        self.ui.install_masternode_button_abu.clicked.connect(self.masternode_install)

        self.ui.add_coin_button.clicked.connect(self.dialog_add_coin.exec)
        self.ui.add_server_button.clicked.connect(self.addserver.exec)
        self.ui.pushButton_2.clicked.connect(self.del_serv)
        self.ui.delete_coin_button.clicked.connect(self.del_coin)

        self.ui.tabWidget.currentChanged.connect(self.update_lists)
        self.update_lists()
        self.ui.most_popular_list.currentRowChanged.connect(self.update_info_block)
        self.ui.all_coins_list.currentRowChanged.connect(self.update_info_block)
        self.ui.added_by_user_list.currentRowChanged.connect(self.update_info_block)



    def update_lists(self):
        self.tab_index = self.ui.tabWidget.currentIndex()
        if self.tab_index == 0:
            self.tab = "mp"
            self.current_list = self.ui.most_popular_list
            self.current_name_label =  self.ui.name_label
            self.current_image_label = self.ui.img_label_mp
            self.upd_data = coins.read_coins(self.tab)

        elif self.tab_index== 1:
            self.tab = "ac"
            self.current_list = self.ui.all_coins_list
            self.current_name_label = self.ui.name_label_ac
            self.current_image_label = self.ui.img_label_ac
            self.upd_data = coins.read_coins(self.tab)

        elif self.tab_index == 2:
            self.tab = "abu"
            self.current_list = self.ui.added_by_user_list
            self.current_name_label = self.ui.coin_name_abu
            self.upd_data = coins.read_coins(self.tab)

        elif self.tab_index == 3: 
            self.current_list = self.ui.servers_list
            self.upd_data = servers.read_servers()

        self.current_list.clear()
        for i in range(len(self.upd_data)):
            self.current_list.addItem(QtWidgets.QListWidgetItem())
            self.current_list.item(i).setText(self.upd_data[i].name)

    def update_info_block(self):
        self.coinlist = coins.read_coins(self.tab)
        self.currentRow = self.current_list.currentRow()
        try:
            self.choiced = self.coinlist[self.currentRow].name
        except IndexError:
            self.choiced = "Choice coin"
        self.current_name_label.setText(self.choiced)

        if self.tab_index < 2:
            self.file_path = path.relpath("images/" + self.choiced + ".jpg")
            self.pixmap = QtGui.QPixmap(self.file_path)      
            self.current_image_label.setPixmap(self.pixmap)

    def get_sh(self):
        try:
            createSh.sh_file(self.coinlist[self.current_list.currentRow()], self.ask_masternodeprivkey())
        except AttributeError:
            pass

    def ask_masternodeprivkey(self):
        mnkey, ok = QtWidgets.QInputDialog.getText(self, 'Input MNkey','Masternode private key:')
        if ok:
            return mnkey
        
    def del_serv(self):
        self.currentRow = self.current_list.currentRow()
        try:
            servers.del_server(self.upd_data[self.currentRow].name)
        except IndexError:
            pass
        self.update_lists()
        
    def del_coin(self):
        self.currentRow = self.current_list.currentRow()
        try:
            coins.del_coin(self.upd_data[self.currentRow].name)
        except IndexError:
            pass
        self.update_lists()

    def masternode_install(self):
        self.get_sh() 
        self.dialog_mn.exec()


def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = Main_window()  
    window.show() 
    sys.exit(app.exec_())

if __name__ == '__main__':  
    main()  
