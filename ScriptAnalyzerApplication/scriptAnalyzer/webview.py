import sys

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *
from PySide.QtWebKit import QWebView, QWebPage


class WebWindow(QMainWindow):
    def __init__(self):
        super(WebWindow,self).__init__()
        Loader = QUiLoader()
        
        uiFile = QFile("C:/Qt/Qt5.0.1/Tools/QtCreator/bin/ScriptAnalyzerNew/webview.ui")
        uiFile.open(QFile.ReadOnly)
        
        self.mainWindow = Loader.load(uiFile)
        
        WebV = QWebView()
        layout = QVBoxLayout()
        layout.addWidget(WebV)
        self.mainWindow.webW.setLayout(layout)   
        WebV.load(QUrl("file:///C:/Users/Administrator/Desktop/demo.html"))
        
        #self.mainWindow.webView.show()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    newWindow = WebWindow()
    newWindow.mainWindow.show()
    sys.exit(app.exec_())        
    