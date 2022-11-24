import os
from sys import argv
from subprocess import call
from tkinter import messagebox

print("Install "+argv[1]+" modules")
class install:
    def nodejsModules():
        call('npm install -m express mime-types', shell=True)
        messagebox.showinfo("Done install", "正常にインストールが完了しました。\nrun.batを実行してください。")

    def pythonModules():
        call('python -m pip install -U pip', shell=True)
        call('pip install selenium', shell=True)
        call('pip install chromedriver-autoinstaller', shell=True)

path="C:\Program Files\Google\Chrome\Application"
if os.path.exists(path) and argv[1] == "python":
    for f in os.listdir(path):
        t=f[:f.find(".")]
        if t.isdigit():
            if int(t)<73:
                #messagebox.showwarning("Warning", "正常に動作しない可能性があります。\nGoogle Chromeを更新してください。")
                install.pythonModules()
            else:
                install.pythonModules()
elif argv[1] == "nodejs":
    install.nodejsModules()
else:
    messagebox.showerror("Error", "Google Chromeがインストールされていません。\nGoogle Chromeをインストールしてください。")