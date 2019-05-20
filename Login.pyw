from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
import json
import hashlib
import os
from MainWidget import MainWidget 

class LoginScreen(QWidget):
    def __init__(self, nextWindow, parent=None):
        super(LoginScreen, self).__init__(parent)

        self.nextWindow = nextWindow
        self.toLoginMode()
        self.initFile()
        self.initUI()
        self.setWindowTitle("Login")
    
    def initFile(self):
        try:
            users_file = open("users.json", "r")
        except OSError as e:
            print("Error")
            users_file = open("users.json", "w")
            users = {}
            json.dump(users, users_file)

    def initUI(self):
        name_line = QLineEdit(parent=self)
        name_label = QLabel("Name: ", parent=self)
        name_label.setBuddy(name_line)

        pass_line = QLineEdit(parent=self)
        pass_line.setEchoMode(QLineEdit.Password)
        pass_label = QLabel("Password: ", parent=self)
        pass_label.setBuddy(pass_line)

        access_denied_label = QLabel("Your username or password is not correct", parent=self)
        access_denied_label.hide()

        login_btn = QPushButton("Log in", parent=self)
        register_btn = QPushButton("Register", parent=self)

        extra = 10

        # init self
        self.setFixedSize(400, 200)

        # in the middle of the screen
        name_label.move(self.width() / 4, extra)
        name_label.setFixedSize(60 , 50)
        # move to next to name_label
        name_line.move(name_label.x() + name_label.width(), name_label.y() + extra)
        name_line.setFixedSize(150, 30)

        # move below name_label
        pass_label.move(name_label.x(), name_label.y() + name_label.height() + extra)
        pass_label.setFixedSize(name_label.width(), name_label.height())
        # move next to pass label
        pass_line.move(pass_label.x() + pass_label.width(), pass_label.y() + extra)
        pass_line.setFixedSize(name_line.width(), name_line.height())

        # move below pass_label
        login_btn.setFixedSize(150, 40)
        login_btn.move(self.width() / 2 - login_btn.width() - extra / 2,
                                             pass_label.y() + pass_label.height() + extra)
        # set to login mode
        login_btn.setStyleSheet("color: blue; background-color: yellow")

        # move beside login_btn
        register_btn.setFixedSize(login_btn.width(), login_btn.height())
        register_btn.move(login_btn.x() + login_btn.width() + extra, login_btn.y())

        def check():
            # if alraeady in login mode
            if self.isLoginMode():
                if name_line.text() == '':
                    MainWidget.displayWarningMsgBox("Fill the name!", parent=self)
                    return
                if pass_line.text() == '':
                    MainWidget.displayWarningMsgBox("Fill the password!", parent=self)
                    return
                if self.login(name_line.text(), pass_line.text()):
                    self.hide()
                    self.nextWindow.activate(name_line.text())
                else:
                    pass_line.setText('')
                    MainWidget.displayWarningMsgBox('Username or password is not correct!', parent=self)
            # change to login mode
            else:
                # toggle register off
                register_btn.setStyleSheet("")
                # toggle login on
                login_btn.setStyleSheet("color: blue; background-color: yellow")
                self.toLoginMode()

        def register():
            # click 'Register' while in login mode -> turn to 'Register' mode
            if self.isLoginMode():
                # toggle login off
                login_btn.setStyleSheet("")
                # toggle register on
                register_btn.setStyleSheet("color: blue; background-color: yellow")
                self.toRegisterMode()
                
                name_line.setText('')
                pass_line.setText('')
            # click 'Register' while in register mode -> register
            else:
                # either register success or there has been such a name
                if self.register(name_line.text(),
                                pass_line.text()) == True:
                    MainWidget.displayWarningMsgBox("Register successfully!", parent=self)
                pass_line.setText('')

        login_btn.clicked.connect(check)
        register_btn.clicked.connect(register)

    def toLoginMode(self):
        self.mode = 'LOGIN'

    def isLoginMode(self):
        return self.mode == 'LOGIN'

    def toRegisterMode(self):
        self.mode = 'REGISTER'

    def isRegisterMode(self):
        return self.mode == 'REGISTER'

    def login(self, user, password):
        access = False
        user = user.lower()
        with open('users.json') as users_file:
            users = json.load(users_file)
            if user in users.keys():
                # encode to utf-8
                encode_pass = password.encode()
                # get md5 hex-hash
                hex_hash_pass = hashlib.md5(encode_pass).hexdigest()
                print("User: {} Password: {} Hash: {} try to access!".format(user, password, hex_hash_pass))
                # compare to the already hashed passworded
                if users[user] == hex_hash_pass:
                    access = True

        return access

    def register(self, user, password):
        success = False
        user = user.lower()
        if user == '' or password == '':
            MainWidget.displayWarningMsgBox("Fill the box!", parent=self)
            return success
        with open('users.json', 'r') as users_file:
            users = json.load(users_file)
            if user in users.keys():
                print("Already exist")
                MainWidget.displayWarningMsgBox("The user has already existed!", parent=self)
                return success
        with open('users.json', 'w') as users_file:
            encode_password = password.encode()
            hex_hash_pass = hashlib.md5(encode_password).hexdigest()
            users[user] = hex_hash_pass
            json.dump(users, users_file)
            os.makedirs(user.lower(), exist_ok=False)
            success = True
        return success

        