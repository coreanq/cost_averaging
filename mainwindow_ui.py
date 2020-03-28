# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(587, 214)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.chkShowBalance = QtWidgets.QCheckBox(self.centralwidget)
        self.chkShowBalance.setObjectName("chkShowBalance")
        self.gridLayout.addWidget(self.chkShowBalance, 0, 0, 1, 2)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lblFiatBalance = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.lblFiatBalance.setFont(font)
        self.lblFiatBalance.setObjectName("lblFiatBalance")
        self.verticalLayout_2.addWidget(self.lblFiatBalance)
        self.lblFiatPercent = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.lblFiatPercent.setFont(font)
        self.lblFiatPercent.setObjectName("lblFiatPercent")
        self.verticalLayout_2.addWidget(self.lblFiatPercent)
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblCryptoBalance = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.lblCryptoBalance.setFont(font)
        self.lblCryptoBalance.setObjectName("lblCryptoBalance")
        self.verticalLayout.addWidget(self.lblCryptoBalance)
        self.lblCryptoPercent = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.lblCryptoPercent.setFont(font)
        self.lblCryptoPercent.setObjectName("lblCryptoPercent")
        self.verticalLayout.addWidget(self.lblCryptoPercent)
        self.gridLayout.addWidget(self.groupBox_2, 1, 1, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setAutoFillBackground(False)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 587, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Shannon\'s demon for upbit"))
        self.chkShowBalance.setText(_translate("MainWindow", "Show Balance?"))
        self.groupBox.setTitle(_translate("MainWindow", "Fiat"))
        self.lblFiatBalance.setText(_translate("MainWindow", "balance"))
        self.lblFiatPercent.setText(_translate("MainWindow", "percent"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Crypto"))
        self.lblCryptoBalance.setText(_translate("MainWindow", "balance"))
        self.lblCryptoPercent.setText(_translate("MainWindow", "percent"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

