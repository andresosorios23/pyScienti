from PyQt5 import QtCore, QtGui, QtWidgets
import pyscienti as pys
from tkinter import filedialog
import pandas as pd

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(607, 549)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.author_btn = QtWidgets.QPushButton(self.centralwidget)
        self.author_btn.setGeometry(QtCore.QRect(50, 230, 251, 23))
        self.author_btn.setObjectName("author_btn")
        self.author_text = QtWidgets.QTextEdit(self.centralwidget)
        self.author_text.setGeometry(QtCore.QRect(50, 180, 251, 41))
        self.author_text.setObjectName("author_text")
        self.group_btn = QtWidgets.QPushButton(self.centralwidget)
        self.group_btn.setGeometry(QtCore.QRect(320, 230, 251, 23))
        self.group_btn.setObjectName("group_btn")
        self.group_text = QtWidgets.QTextEdit(self.centralwidget)
        self.group_text.setGeometry(QtCore.QRect(320, 180, 251, 41))
        self.group_text.setObjectName("group_text")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(60, 30, 501, 101))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(140, 150, 141, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(390, 150, 141, 20))
        self.label_3.setObjectName("label_3")
        self.authors_btn = QtWidgets.QPushButton(self.centralwidget)
        self.authors_btn.setGeometry(QtCore.QRect(50, 280, 521, 31))
        self.authors_btn.setObjectName("authors_btn")
        self.groups_btn = QtWidgets.QPushButton(self.centralwidget)
        self.groups_btn.setGeometry(QtCore.QRect(50, 322, 521, 31))
        self.groups_btn.setObjectName("groups_btn")
        self.com_btn = QtWidgets.QPushButton(self.centralwidget)
        self.com_btn.setGeometry(QtCore.QRect(50, 362, 521, 31))
        self.com_btn.setObjectName("com_btn")
        self.clean_btn = QtWidgets.QPushButton(self.centralwidget)
        self.clean_btn.setGeometry(QtCore.QRect(50, 430, 521, 31))
        self.clean_btn.setObjectName("clean_btn")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(50, 490, 521, 31))
        self.label_4.setText("")
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.group_text.setPlaceholderText('Inserte el enlace de GrupLAC del grupo o el código del grupo (COL##########).')
        self.author_text.setPlaceholderText('Inserte el enlace de CvLAC del investigador o el código.')
        self.author_btn.clicked.connect(self.author_xls)
        self.authors_btn.clicked.connect(self.authors_xls)
        self.group_btn.clicked.connect(self.group_xls)
        self.groups_btn.clicked.connect(self.groups_xls)
        self.com_btn.clicked.connect(self.com_xls)
        self.clean_btn.clicked.connect(pys.clean_old_files)


    def author_xls(self):
        self.label_4.setText("")
        try:
            self.label_4.setText(pys.Author(self.author_text.toPlainText()).to_xlsx())
        except:
            self.label_4.setText('Hay un problema con el enlace o código, o el perfil del investigador está vacío.')
    def group_xls(self):
        try:
            pys.Group(self.group_text.toPlainText()).to_xlsx()
        except:
            self.label_4.setText('Hay un problema con el enlace o código, o el perfil del grupo está vacío.')

    def authors_xls(self):
        self.label_4.setText(" ")
        path = filedialog.askopenfilename()
        if path:
            try:
                lista = pd.read_excel(path, sheet_name = 'Investigadores', dtype=str)
                lista = lista[lista['CvLAC'].notna()]
                pys.create_author_obj(lista['CvLAC'],True)
                pys.create_authors_xlsx()
            except:
                self.label_4.setText('Verifique que el archivo cumpla con los requisitos especificados en el manual')


    def groups_xls(self):
        self.label_4.setText("")
        path = filedialog.askopenfilename()
        if path:
            try:
                groups = pd.read_excel(path, sheet_name = 'Grupos')
                groups = groups[groups['GrupLAC'].notna()]        
                pys.create_group_obj(groups['Código'])
                pys.create_group_xls()
                pys.create_groups_resume()
            except:
                self.label_4.setText('Verifique que el archivo cumpla con los requisitos especificados en el manual')



    def com_xls(self):
        self.label_4.setText("")
        path = filedialog.askopenfilename()
        if path:
            try:
                lista = pd.read_excel(path, sheet_name = 'Investigadores', dtype=str)
                lista = lista[lista['CvLAC'].notna()]
                groups = pd.read_excel(path, sheet_name = 'Grupos')
                groups = groups[groups['GrupLAC'].notna()]

                pys.create_author_obj(lista['CvLAC'],True)
                pys.create_group_obj(groups['GrupLAC'])
                pys.create_group_xlsx_com(lista['Nombre'],lista['CvLAC'])
                pys.create_groups_resume()
                pys.create_authors_xlsx()
            except:
                self.label_4.setText('Verifique que el archivo cumpla con los requisitos especificados en el manual')

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.author_btn.setText(_translate("MainWindow", "Crear resumen de investigador"))
        self.author_text.setToolTip(_translate("MainWindow", "<html><head/><body><p><br/></p></body></html>"))
        self.group_btn.setText(_translate("MainWindow", "Crear resumen de grupo"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><img src=\":/Logo/Logo.png\"/></p></body></html>"))
        self.label_2.setText(_translate("MainWindow", "Investigadores"))
        self.label_3.setText(_translate("MainWindow", "Grupos de investigación"))
        self.authors_btn.setText(_translate("MainWindow", "Crear resúmenes de los investigadores en el archivo \"autores.xlsx\""))
        self.groups_btn.setText(_translate("MainWindow", "Crear resúmenes de los grupos en el archivo \"grupos.xlsx\""))
        self.com_btn.setText(_translate("MainWindow", "Crear resúmenes de grupos y de investigadores en el archivo \"comp.xlsx\""))
        self.clean_btn.setText(_translate("MainWindow", "Limpiar archivos antiguos"))

import pic_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
