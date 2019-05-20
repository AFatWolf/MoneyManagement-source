from PyQt5.QtWidgets import *
from MainWidget import MainWidget
from Login import LoginScreen

def execute():
    app = QApplication([])
    app.setStyle("Fusion")
    mainWidget = MainWidget()

    def beforeQuit():
      if mainWidget.isRunning:
           mainWidget.save()
      print("Hey im quitting")

    app.aboutToQuit.connect(beforeQuit)

    loginWindow = LoginScreen(mainWidget)
    loginWindow.show()
   
    app.exec_()


if __name__ == "__main__":
    execute()
        

