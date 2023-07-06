# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLayout, QMainWindow,
    QMenuBar, QPlainTextEdit, QPushButton, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(803, 254)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lblFiatBalance = QLabel(self.groupBox)
        self.lblFiatBalance.setObjectName(u"lblFiatBalance")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.lblFiatBalance.setFont(font)

        self.verticalLayout_2.addWidget(self.lblFiatBalance)

        self.lblFiatPercent = QLabel(self.groupBox)
        self.lblFiatPercent.setObjectName(u"lblFiatPercent")
        self.lblFiatPercent.setFont(font)

        self.verticalLayout_2.addWidget(self.lblFiatPercent)


        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)

        self.chkTradeOn = QCheckBox(self.centralwidget)
        self.chkTradeOn.setObjectName(u"chkTradeOn")

        self.gridLayout.addWidget(self.chkTradeOn, 0, 1, 1, 1)

        self.chkShowBalance = QCheckBox(self.centralwidget)
        self.chkShowBalance.setObjectName(u"chkShowBalance")

        self.gridLayout.addWidget(self.chkShowBalance, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout = QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lblCryptoBalance = QLabel(self.groupBox_2)
        self.lblCryptoBalance.setObjectName(u"lblCryptoBalance")
        self.lblCryptoBalance.setFont(font)

        self.verticalLayout.addWidget(self.lblCryptoBalance)

        self.lblCryptoPercent = QLabel(self.groupBox_2)
        self.lblCryptoPercent.setObjectName(u"lblCryptoPercent")
        self.lblCryptoPercent.setFont(font)

        self.verticalLayout.addWidget(self.lblCryptoPercent)


        self.gridLayout.addWidget(self.groupBox_2, 1, 1, 1, 2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.btnDeposit = QPushButton(self.centralwidget)
        self.btnDeposit.setObjectName(u"btnDeposit")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDeposit.sizePolicy().hasHeightForWidth())
        self.btnDeposit.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.btnDeposit)

        self.txtDepositAmount = QPlainTextEdit(self.centralwidget)
        self.txtDepositAmount.setObjectName(u"txtDepositAmount")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.txtDepositAmount.sizePolicy().hasHeightForWidth())
        self.txtDepositAmount.setSizePolicy(sizePolicy1)
        self.txtDepositAmount.setBackgroundVisible(False)

        self.horizontalLayout.addWidget(self.txtDepositAmount)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 2, 1, 2)

        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lblOriBalance = QLabel(self.groupBox_3)
        self.lblOriBalance.setObjectName(u"lblOriBalance")
        self.lblOriBalance.setFont(font)

        self.verticalLayout_3.addWidget(self.lblOriBalance)

        self.lblOriPercent = QLabel(self.groupBox_3)
        self.lblOriPercent.setObjectName(u"lblOriPercent")
        self.lblOriPercent.setFont(font)

        self.verticalLayout_3.addWidget(self.lblOriPercent)


        self.gridLayout.addWidget(self.groupBox_3, 1, 3, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 803, 22))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"unit cost averaging using upbit openapi", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Fiat", None))
        self.lblFiatBalance.setText(QCoreApplication.translate("MainWindow", u"balance", None))
        self.lblFiatPercent.setText(QCoreApplication.translate("MainWindow", u"percent", None))
        self.chkTradeOn.setText(QCoreApplication.translate("MainWindow", u"Trade On?", None))
        self.chkShowBalance.setText(QCoreApplication.translate("MainWindow", u"Show Balance?", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Crypto", None))
        self.lblCryptoBalance.setText(QCoreApplication.translate("MainWindow", u"balance", None))
        self.lblCryptoPercent.setText(QCoreApplication.translate("MainWindow", u"percent", None))
        self.btnDeposit.setText(QCoreApplication.translate("MainWindow", u"Deposit", None))
        self.txtDepositAmount.setPlainText(QCoreApplication.translate("MainWindow", u"220000", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"\ufeff\ucd1d \ufeff\uc790\uc0b0", None))
        self.lblOriBalance.setText(QCoreApplication.translate("MainWindow", u"balance", None))
        self.lblOriPercent.setText(QCoreApplication.translate("MainWindow", u"percent", None))
    # retranslateUi

