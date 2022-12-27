import os
import shutil
import sys
import platform
from argparse import ArgumentParser
import re
import time
import datetime
import json
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller

dataPath = os.path.join(os.path.dirname(__file__), 'GUI/data.json')
settingPath = os.path.join(os.path.dirname(__file__), 'settings.json')

class loadData:
    def __init__(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                self.data = json.load(f) # read from file
            except:
                self.data = {}

    def verifyUserData(self):
        if("userID" not in self.data):
            print("Error: invalidate verification. userID is not found.")
            return False
        elif("password" not in self.data):
            print("Error: invalidate verification. password is not found.")
            return False
        else:
            return True

class writeData:
    def __init__(self, path):
        self.path = path

    def __del__(self):
        with open(self.path, 'w', encoding = 'utf-8') as f:
            json.dump(self.data, f, ensure_ascii = False, indent=4)

    def overrideAll(self, key, values):
        self.data = {}
        self.data[key] = values

    def override(self, key, value):
        with open(self.path, 'r', encoding = 'utf-8') as f:
            try:
                self.data = json.load(f) # read from file
                self.data.update(dict(zip([key], [value])))
            except:
                self.data = dict(zip([key], [value]))

    def update(self, key, values):
        with open(self.path, 'r', encoding = 'utf-8') as f:
            try:
                self.data = json.load(f) # read from file
            except:
                self.data = {}
            if type(values) == list:
                if key in self.data:
                    self.data[key].extend(values) # extend values
                else:
                    self.data[key] = values # make new key and set values
            elif type(values) == dict:
                if key in self.data:
                    self.data[key].update(values) # update values
                else:
                    self.data[key] = values # make new key and set values
            else:
                sys.exit("Error: value must be a list or dict.")

class userInterface:
    def __init__(self):
        self.__settings=loadData(settingPath).data["userInterface"]
        self.__root=tk.Tk()
        self.__root.resizable(0, 0)

    def position(self, mode):
        if self.__settings[mode]["position"] == "center":
            self.__position = f'{str(int((self.__root.winfo_screenwidth() - self.__settings[mode]["x"])/2))}+{str(int((self.__root.winfo_screenheight() - self.__settings[mode]["y"])/2))}'
        else:
            self.__position = str(self.__settings[mode]["position"])
        return self.__position

    def register(self):
        def __callback(__root, __ID, __password):
            if len(__password) != 0 and len(__ID) == 7 and len(re.findall(r'^[0-9]+$',__ID)) != 0:
                writeData(dataPath).override("userID", __ID)
                writeData(dataPath).override("password", __password)
                message=messagebox.showinfo("情報", "登録完了\nクラスリストを取得します。")
                if message == "ok":
                    __root.destroy()
            else:
                messagebox.showwarning("確認", "入力エラー","学籍番号が7桁の整数でないかパスワードが入力されていません。")
        
        self.__root.title("ユーザー登録")
        self.__root.geometry(f'{self.__settings["default"]["x"]}x{self.__settings["default"]["y"]}+{self.position("default")}')
        tk.Label(text="学籍番号", width=self.__settings["default"]["input-width"]).place(x=12,y=40)
        tk.Label(text="パスワード", width=self.__settings["default"]["input-width"]).place(x=12,y=80)
        __inputID=tk.Entry(width=self.__settings["default"]["label-width"])
        __inputID.place(x=100,y=40)
        __inputPassword=tk.Entry(width=self.__settings["default"]["label-width"], show="*")
        __inputPassword.place(x=100,y=80)
        tk.Button(text="登録", width=self.__settings["default"]["input-width"], command=lambda: __callback(self.__root, __inputID.get(), __inputPassword.get())).place(x=205,y=120)
        self.__root.mainloop()
    
    def __checkBool(self, __classSelectBool, __classesKey):
        __selectedClasses = []
        for i in range(len(__classSelectBool)):
            if __classSelectBool[i].get() == True:
                __selectedClasses.append(__classesKey[i])
        try:
            self.__root.destroy()
        except:
            pass
        return __selectedClasses

    def askUpdateList(self, classList):
        __select1 = messagebox.askyesnocancel("確認", "全授業のデータを更新しますか?\n(一部の授業のみ更新したい場合はいいえを選択してください。)")
        if __select1 == None:
            quit()
        elif __select1 == True:
            return classList.keys()
        elif __select1 == False:
            __classSelectBool = {}
            __classesKey=[]
            __classesName=[]
            self.__root.title("科目選択")
            self.__root.geometry(f'{self.__settings["default"]["x"]}x{24*(len(classList)+4)}+{self.position("default")}')
            for __key in classList.keys():
                __classesKey.extend([__key])
                __classesName.extend([classList[__key]])
            for i in range(len(__classesKey)):
                __classSelectBool[i] = tk.BooleanVar()
                __check = tk.Checkbutton(self.__root, variable = __classSelectBool[i], text = __classesName[i])
                __check.place(x=50, y=24*(i+1))
            __boolCheck = tk.Button(self.__root, text = "確認", command = lambda: self.__checkBool(__classSelectBool, __classesKey))
            __cancel = tk.Button(self.__root, text = "キャンセル", command = lambda: quit())
            __boolCheck.place(x=50, width = 100, y=24*(len(__classSelectBool)+2))
            __cancel.place(x=self.__settings["default"]["x"] - 150, width = 100, y=24*(len(__classSelectBool)+2))
            self.__root.mainloop()
            return self.__checkBool(__classSelectBool, __classesKey)
        else:
            quit()

class browserControl:
    def __init__(self, userData):
        self.userData = userData
        self.browser = webdriver.Chrome()
        __chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        print(platform.system())
        if platform.system() == 'Windows':
            self.driver_path = f'./{__chrome_ver}/chromedriver.exe'
            if not os.path.exists(self.driver_path):
                chromedriver_autoinstaller.install(True)
            __options = webdriver.ChromeOptions()
            __options.add_argument(f"user-data-dir={os.path.join(os.path.dirname(__file__), 'Chrome')}")
            __options.add_argument("--profile-directory=Profile HWC")
            __options.add_experimental_option("excludeSwitches", ["enable-logging"])
            self.browser = webdriver.Chrome(service=fs.Service(executable_path=self.driver_path), options = __options)
        elif platform.system() == 'MacOS':
            self.browser = webdriver.Chrome()

    def login(self):
        self.browser.get("https://webclass.tcu.ac.jp/")
        self.browser.find_element(By.XPATH, value="//a[@onclick=\"callSSOWebClass('JAPANESE')\"]").click()
        self.browser.switch_to.window(self.browser.window_handles[-1])
        try:
            self.browser.find_element(By.XPATH, value="//input[@class='input_id']").send_keys("g"+self.userData["userID"])
            self.browser.find_element(By.XPATH, value="//input[@class='input_pass']").send_keys(self.userData["password"])
            self.browser.find_element(By.ID, value="login").click()
            if "https://sso.tcu.ac.jp/idp/Authn/External" in self.browser.current_url:
                print("Error: invalidate verification")
                userInterface().register()
        except:
            pass

    def getClassList(self):
        self.login()
        time.sleep(3)
        __classes = self.browser.find_elements(By.XPATH, value="//table[@id='schedule-table']//tr/td")
        classes = {}
        acs = ""
        for __class in __classes:
            __className = re.sub(r"\n|\((月|火|水|木|金|土).+?\)|[0-9]限|»|_sa[a-z][0-9]+|_sb[a-z][0-9]+|_ya[a-z][0-9]+|_yb[a-z][0-9]+|新着メッセージ\(\d+\)|締切が近い課題があります。| ",'', __class.text)
            if __className:
                __href = __class.find_element(By.TAG_NAME, value="a").get_attribute("href")
                __classID = re.sub(r"https://webclass.tcu.ac.jp/webclass/course.php/[0-9][0-9]|/login\?acs_=.*", '', __href)
                __acs = re.sub(r"https://webclass.tcu.ac.jp/.*/login\?acs_=", '', __href)
                classes.update(zip([__classID],[__className]))
                acs = __acs
        writeData(dataPath).override("acs", acs)
        writeData(dataPath).override("classList", classes)

    def getClassDetails(self, saID):
        def __getDetails():
            __classDetails = {}
            time.sleep(3)
            __itemList = self.browser.find_elements(By.CSS_SELECTOR, value=".list-group-item.cl-contentsList_listGroupItem")
            for __item in __itemList:
                __details = __item.text.splitlines()
                __href = __item.find_element(By.TAG_NAME, value="a").get_attribute("href")
                if __href.find("do_contents.php") != -1:
                    __active = True
                else:
                    __active = False
                __href = re.sub(r"https://webclass.tcu.ac.jp/webclass/|course.php/^[0-9].?s[a-z].?[0-9].?/contents/|course.php/^[0-9].?y[a-z].?[0-9].?/contents/|do_contents.php\?|reset_status=1&|set_contents_id=|/\?acs_=.*","",__href)
                __slashPosition = __href.rfind("/")
                if __slashPosition != -1:
                    __href = __href[__slashPosition+1:]
                try:
                    __details.remove([s for s in __details if '利用回数' in s][0])
                except:
                    pass
                try:
                    __details.remove("New")
                except:
                    pass
                try:
                    __details.remove("詳細")
                except:
                    pass
                __detail = {
                    "id": __year+__class,
                    "name": __details[0],
                    "type": __details[1],
                    "active": __active
                }
                if len(__details) >= 3 and __details[2].find("利用可能期間") != -1:
                    __detail["start"] = __details[2][7:23]
                    __detail["end"] = __details[2][26:]
                __classDetails[__href] = __detail
            writeData(dataPath).update("classDetails", __classDetails)

        self.login()
        __saID = saID
        __acs = self.userData["acs"]
        __year = str(datetime.datetime.today().year)[2:4]
        if type(__saID) == str:
            __saID = [__saID]
        for __class in __saID:
            __classURL = f"https://webclass.tcu.ac.jp/webclass/course.php/{__year}{__class}/login?acs_={__acs}"
            self.browser.get(__classURL)
            __getDetails()

################################################################
"""

loadData(dataPath).data
    Reading data from the dataPath.

writeData(dataPath).overrideAll(<key>, <value>)
    Write data to the dataPath (No hold old data).

writeData(dataPath).override(<key>, <value>)
    Write data to the dataPath (Hold old data).

writeData(dataPath).update(<key>, <values>)
    Write data to the dataPath (Only extend).

"""
################################################################

class get_args():
    def __init__(self, userData):
        self.argParser = ArgumentParser()

        self.userData = userData

        self.argParser.add_argument("-c", "--classlist", type=str,
            default = None,
            help="クラスリストの更新を実施する際に --classlist True, 実施しない場合に --classlist False をつけて実行してください。"
        )

        self.argParser.add_argument("-u", "--update", type=str,
            default = "",
            help="更新する項目を引数に渡します。 科目をすべて更新する場合 all, 科目を一部更新する場合 sa/sb*********, ya/yb*********, デフォルトでは確認されます。, また複数選択したい場合は空白を挟まずにsa******sa******sa******のように入力してください。"
        )

        self.updateConfig = {
            "updateClass": self.argParser.parse_args().classlist,
            "updateList": self.argParser.parse_args().update
        }

    def updateClassList(self):
        #Return True or False due to the updateConfig parameter.
        if self.updateConfig["updateClass"] == 'True' or not "classList" in self.userData:
            return True
        elif self.updateConfig["updateClass"] == 'False' and "classList" in self.userData:
            return False
        else:
            return messagebox.askyesnocancel("確認", "クラスリストを更新しますか？")

    def updateClassDetails(self):
        #Return List of update Class details.
        self.rawUpdateArg = self.updateConfig["updateList"]

        self.updateList = []

        if self.rawUpdateArg == "all":
            self.updateList = list(self.userData["classList"].keys())
        elif len(self.rawUpdateArg) % 9 == 0 and self.rawUpdateArg != None:
            for i in range(int(len(self.rawUpdateArg)/9)+1):
                self.updateList.append(self.rawUpdateArg[(i-1)*9:i*9])
        else:
            userInterface().askUpdateList(self.userData["classList"])

        self.updateList = list(filter(None, self.updateList))

        return self.updateList


class __main__:
    print("Checker is running")
    try:
        shutil.rmtree("./Chrome")
    except FileNotFoundError:
        pass

    try:
        userData=loadData(dataPath).data
    except FileNotFoundError:
        with open(dataPath, "w") as f:
            f.write("")
        userData = {}

    if len(userData) == 0:
        userInterface().register()
        userData=loadData(dataPath).data

    updateClassList = get_args(userData).updateClassList()
    updateClassDetails = get_args(userData).updateClassDetails()

    if updateClassList:
        browserControl(userData).getClassList()
        userData=loadData(dataPath).data
    elif updateClassList == None:
        quit()

    if len(updateClassDetails) != 0:
        browserControl(userData).getClassDetails(updateClassDetails)
    else:
        quit()

    try:
        shutil.rmtree("./Chrome")
    except FileNotFoundError:
        pass