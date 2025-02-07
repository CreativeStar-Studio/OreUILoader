# KEY: sk-1d46e1e124254fcfae7b6e7b5f88640e

import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import tkinter.messagebox
import webbrowser
import zipfile

from PyQt5.QtCore import Qt, QTranslator, QEventLoop, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QProgressBar, QGroupBox,
    QFileDialog
)

true = True
false = False
null = None
none = None


class OreUILoader(QWidget):

    def __init__(self):
        super().__init__()
        self.packname = none
        self.startmc = none
        self.gamepath = none
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        lang_group = QGroupBox("语言选择")
        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["  中文"])
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_combo)
        lang_group.setLayout(lang_layout)

        input_group = QGroupBox("路径输入")
        input_layout = QVBoxLayout()

        gamepath_layout = QHBoxLayout()
        self.gamepath_label = QLabel("我的世界路径:")
        self.gamepath_input = QLineEdit()
        self.gamepath_button = QPushButton("选择路径")
        self.gamepath_button.clicked.connect(self.select_game_path)
        gamepath_layout.addWidget(self.gamepath_label)
        gamepath_layout.addWidget(self.gamepath_input)
        gamepath_layout.addWidget(self.gamepath_button)

        packname_layout = QHBoxLayout()
        self.packname_label = QLabel("资源包（兼容性差）/界面包:\n\n")
        self.packname_input = QLineEdit()
        self.packname_input.setFixedSize(200,30)
        self.packname_button = QPushButton("选择文件")
        self.packname_button.clicked.connect(self.select_pack_file)
        packname_layout.addWidget(self.packname_label)
        packname_layout.addWidget(self.packname_input)
        packname_layout.addWidget(self.packname_button)

        input_layout.addLayout(gamepath_layout)
        input_layout.addLayout(packname_layout)
        input_group.setLayout(input_layout)

        startmc_layout = QHBoxLayout()
        self.startmc_checkbox = QCheckBox("是否启动我的世界")
        startmc_layout.addWidget(self.startmc_checkbox)

        startmc_widget = QWidget()
        startmc_widget.setLayout(startmc_layout)

        button_layout = QHBoxLayout()
        button = QWidget()
        button.setLayout(button_layout)
        self.startbutton = QPushButton("开始")
        self.startbutton.clicked.connect(self.start_process)
        self.restore_button = QPushButton("恢复")
        self.restore_button.clicked.connect(self.restore_files)
        button_layout.addWidget(self.startbutton)
        button_layout.addWidget(self.restore_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        main_layout.addWidget(lang_group)
        main_layout.addWidget(input_group)
        main_layout.addWidget(startmc_widget)
        main_layout.addWidget(button)
        main_layout.addWidget(self.progress_bar)
        self.setLayout(main_layout)

        self.setWindowTitle("OreUI  加载器")
        self.setGeometry(300, 300, 400, 450)
        self.setFixedSize(400, 450)
        self.setWindowIcon(QIcon('icon.ico'))
        self.progress_bar.setFormat("")

        self.setStyleSheet(""" 
            QGroupBox { 
                border: 1px solid gray; 
                border-radius: 5px; 
                margin-top: 10px; 
                padding: 10px; 
            } 
            QPushButton { 
                padding: 5px 10px; 
                background-color: #48D1CC; 
                color: white; 
                border: none; 
                border-radius: 3px; 
            } 
            QPushButton:hover { 
                background-color: #20B2AA; 
            }
            QPushButton:disabled { 
                background-color: #707f70; 
            } 
            QCheckBox { 
                margin-top: 10px; 
            } 
            QProgressBar { 
                margin-top: 10px; 
                text-align: center; 
            } 
            QProgressBar::chunk { 
                background-color: #48D1CC; 
            } 
        """)

        self.show()

    def change_language(self, index):
        translator = QTranslator()
        if index == 0:
            translator.load('translations/zh_CN.qm')
        else:
            translator.load('translations/en_US.qm')
        QApplication.instance().installTranslator(translator)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.gamepath_label.setText(self.tr(" 我的世界路径:"))
        self.packname_label.setText(self.tr("资源包（兼容性差）/UI包:"))
        self.startmc_checkbox.setText(self.tr(" 是否启动我的世界"))
        self.startbutton.setText(self.tr(" 开始"))
        self.restore_button.setText(self.tr(" 恢复"))
        self.gamepath_button.setText(self.tr(" 选择路径"))
        self.packname_button.setText(self.tr(" 选择文件"))

    def select_game_path(self):
        path = QFileDialog.getExistingDirectory(
            self,
            self.tr(" 选择我的世界路径"),
            os.getcwd()
        )
        if path:
            self.gamepath_input.setText(path)
        else:
            QMessageBox.warning(self, self.tr(" 警告"), self.tr(" 未选择任何路径"))

    def select_pack_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr(" 选择资源包/界面包文件"),
            os.getcwd(),
            "资源包 (*.mcpack);;界面包 (*.mcui)",
        )
        if file_path:
            self.packname_input.setText(file_path)
        else:
            QMessageBox.warning(self, self.tr(" 警告"), self.tr(" 未选择任何文件"))

    def start_process(self):
        gamepath = self.gamepath_input.text()
        packname = self.packname_input.text()
        startmc = self.startmc_checkbox.isChecked()

        self.gamepath = gamepath
        self.startmc = startmc
        self.packname = packname

        if not self.check_cpp_runtime():
            self.install_cpp_runtime()
        if not self.check_java():
            self.install_java()

        if packname != "" and gamepath != "":
            if packname[0:1] == "\'":
                packname = packname[1:-1]
            if packname[0:1] == "\"":
                packname = packname[1:-1]
            if packname[-1 - 1:-1] == "\'":
                packname = packname[-1:1:-1]
            if packname[-1 - 1:-1] == "\"":
                packname = packname[-1:1:-1]
            if gamepath[0:1] == "\'":
                gamepath = gamepath[1:-1]
            if gamepath[0:1] == "\"":
                gamepath = gamepath[1:-1]
            if gamepath[-1 - 1:-1] == "\'":
                gamepath = gamepath[-1:1:-1]
            if gamepath[-1 - 1:-1] == "\"":
                gamepath = gamepath[-1:1:-1]
            if packname == "" and gamepath == "":
                QMessageBox.warning(self, self.tr(" 警告"), self.tr(" 请正确输入 mcpack/mcui 文件和我的世界路径"))
                return
            if not os.path.exists(gamepath):
                QMessageBox.warning(self, self.tr(" 警告"), self.tr(" 所选的我的世界路径不存在"))
                return
            if not os.path.exists(packname):
                QMessageBox.warning(self, self.tr(" 警告"), self.tr("所选的 mcpack/mcui 文件不存在"))
                return
            self.enable_labels(false)
            temp_dir = tempfile.mkdtemp()
            try:
                with zipfile.ZipFile(rf'{packname}', 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            except zipfile.BadZipFile as e:
                QMessageBox.warning(self, "错误", f"解压文件出错: {e}")
                self.progress_bar.reset()
                self.enable_labels(true)
                return
            self.progress_bar.setValue(10)

            backup_dir = os.path.join(os.getcwd(), 'backup')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            try:
                self.backup_files(os.path.join(gamepath, 'data', 'gui', 'dist', 'hbui'), backup_dir)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"备份原文件出错: {e}")
                shutil.rmtree(temp_dir)
                self.progress_bar.reset()
                self.enable_labels(true)
                return
            self.progress_bar.setValue(30)

            if not self.check_dll_exists():
                return

            try:
                dll_path = os.path.abspath('copy_files.dll')
                cpp_dll = ctypes.WinDLL(dll_path, winmode=0)
                cpp_dll.copy_files(temp_dir.encode('utf-8'), gamepath.encode('utf-8'))
            except OSError as e:
                QMessageBox.warning(self, "错误", f"无法加载Dll文件：{dll_path}\n错误信息：{e}")
                self.enable_labels(true)
                self.progress_bar.reset()
                return

            except Exception as e:
                QMessageBox.warning(self, "错误", f"Dll调用过程中发生错误：{e}")
                self.enable_labels(true)
                self.progress_bar.reset()
                return

            self.progress_bar.setValue(50)
            delay(1200)
            self.progress_bar.setValue(0)
            self.progress_bar.setRange(0, 0)
            delay(3000)
            try:
                subprocess.run(["resources/nsudo32/NSudoLC.exe", "-U:T", "-P:E", "-UseCurrentConsole",
                                sys.executable, os.path.dirname(__file__) + r'\loadjava.py',
                                temp_dir, gamepath, "replace", os.getcwd()], check=true)
            except subprocess.CalledProcessError as e:
                QMessageBox.warning(self, "错误", f"运行提权程序出错: {e}")
                shutil.rmtree(temp_dir)
                self.progress_bar.setRange(0, 100)
                self.progress_bar.reset()
                self.enable_labels(true)
                return
            else:
                self.enable_labels(true)
                if startmc:
                    self.progress_bar.setRange(0, 100)
                    self.progress_bar.setValue(90)
                    try:
                        webbrowser.open("minecraft://")
                    except Exception as err:
                        tkinter.messagebox.showerror("错误", f"启动我的世界出错: {err}")
                        self.progress_bar.reset()
                    else:
                        self.progress_bar.setValue(100)
                        QMessageBox.information(self, "操作完成",
                                                "由于技术原因，文件复制是否成功并不可知，请您手动查看控制台或游戏界面")
                        self.progress_bar.reset()
                else:
                    self.progress_bar.setRange(0, 100)
                    self.progress_bar.setValue(100)
                    QMessageBox.information(self, "操作完成",
                                            "由于技术原因，文件复制是否成功并不可知，请您手动查看控制台或游戏界面")
                    self.progress_bar.reset()

        else:
            QMessageBox.warning(self, "错误", self.tr(" 请填写所有必填项"))

    def check_cpp_runtime(self):
        try:
            dll = ctypes.WinDLL("msvcrt.dll", winmode=0)
            return true
        except OSError:
            return false

    def install_cpp_runtime(self):
        QMessageBox.warning(self, self.tr(" 提示"), self.tr(" 检测到C++运行库缺失!"))
        """后续更新此逻辑"""

    def check_java(self):
        try:
            subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return true
        except FileNotFoundError:
            return false

    def install_java(self):
        QMessageBox.warning(self, self.tr(" 提示"), self.tr(" 检测到Java缺失!"))
        """后续更新此逻辑"""

    def backup_files(self, source, backup_dir):
        if os.path.exists(backup_dir):
            reply = QMessageBox.question(self, '确认提示', '备份目录已存在，是否替换原备份？',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        for root, dirs, files in os.walk(source):
            for file in files:
                source_file = os.path.join(root, file)
                backup_file = os.path.join(backup_dir, os.path.relpath(source_file, source))
                os.makedirs(os.path.dirname(backup_file), exist_ok=true)
                shutil.copy2(source_file, backup_file)

    def restore_files(self):
        if self.gamepath_input.text() == "":
            QMessageBox.warning(self, "警告", self.tr(" 请先填写我的世界路径"))
            return
        self.enable_labels(false)
        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, 0)
        gamepath = self.gamepath_input.text()
        backup_dir = os.path.join(os.getcwd(), 'backup')
        # target_dir = os.path.join(gamepath, 'data', 'gui', 'dist', 'hbui')
        """
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                backup_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, os.path.relpath(backup_file, backup_dir))
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                try:
                    shutil.copy2(backup_file, target_file)
                except Exception as e:
                    QMessageBox.warning(self, f"恢复文件 {os.path.basename(backup_file)}  时出错", str(e))
        """
        subprocess.run(["resources/nsudo32/NSudoLC.exe", "-U:T", "-P:E", "-UseCurrentConsole",
                        sys.executable, os.path.dirname(__file__) + "/loadjava.py",
                        backup_dir, gamepath, "restore", os.getcwd()], check=true)
        delay(15000)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "信息", "由于技术原因，文件复制是否成功并不可知，请您手动查看控制台或游戏界面")
        self.restore_button.setDisabled(true)
        self.progress_bar.reset()
        self.enable_labels(true)

    def check_dll_exists(self):
        dll_path = os.path.abspath('copy_files.dll')
        if not os.path.exists(dll_path):
            QMessageBox.warning(self, "错误", f"Dll文件不存在：{dll_path}")
            return false
        return true

    def enable_labels(self, boolean_flag: bool):
        boolean_flag = not boolean_flag
        self.gamepath_label.setDisabled(boolean_flag)
        self.gamepath_input.setDisabled(boolean_flag)
        self.restore_button.setDisabled(boolean_flag)
        self.startmc_checkbox.setDisabled(boolean_flag)
        self.packname_input.setDisabled(boolean_flag)
        self.packname_label.setDisabled(boolean_flag)
        self.gamepath_button.setDisabled(boolean_flag)
        self.packname_button.setDisabled(boolean_flag)


def delay(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec_()


if __name__ == '__main__':
    ntdll = ctypes.WinDLL("ntdll.dll", winmode=0)


    def RtlAdjustPrivilege(Privilege, Enable, CurrentThread, OldValue):
        return ntdll.RtlAdjustPrivilege(Privilege, Enable, CurrentThread, OldValue)


    SE_DEBUG_PRIVILEGE = 9
    ENABLE_PRIVILEGE = true
    CURRENT_THREAD = 0
    old_value = ctypes.byref(ctypes.c_bool())

    result = RtlAdjustPrivilege(SE_DEBUG_PRIVILEGE, ENABLE_PRIVILEGE, CURRENT_THREAD, old_value)

    if result != 0:
        tkinter.messagebox.showerror(message=f"Failed to adjust privilege. Error code: {result}")

    app = QApplication(sys.argv)
    ex = OreUILoader()
    sys.exit(app.exec_())
