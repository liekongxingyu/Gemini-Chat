import datetime
import re
import google.generativeai as genai
import pyperclip
import os


class GenerateText:
    def __init__(self) -> None:
        with open('./settings/normal.txt', 'r', encoding='utf-8') as file:
            normal = file.read()
        self.normal = normal
        with open('./settings/jailBreak.txt', 'r', encoding='utf-8') as file:
            jailBreak = file.read()
        self.jailBreak = jailBreak
        with open('./settings/api_lists.txt', 'r') as file:
            # 逐行读取文件内容并存储在列表中
            self.api_lists = file.readlines()
        for i in range(len(self.api_lists)):
            self.api_lists[i] = self.api_lists[i].replace('\n', '')
        self.modelName = 'gemini-1.5-pro'
        self.count = 0
        self.modelFlag = 0
        self.character = 'normal'
        self.store_path = "./data/"
        self.file = None
        self.initContents()

    def configure_model(self):
        genai.configure(api_key=self.api_lists[self.modelFlag])
        self.model = genai.GenerativeModel(self.modelName)

    def changeModels(self):
        # 更新 modelFlag 以实现轮转
        self.modelFlag = (self.modelFlag + 1) % len(self.api_lists)
        self.configure_model()

    def initContents(self):
        self.contents = [
            {
                'role': 'user',
                'parts': [
                    {'text': self.normal}
                ]
            },
            {
                'role': 'model',
                'parts': [
                    {'text': "收到，谨遵您的旨意"}
                ]
            }
        ]

    def initCharacter(self, character):
        print(character)
        with open(f"./character/{character}.txt", encoding='utf-8') as file:
            self.prompt = file.read()
        self.contents.append({
            'role': 'user',
            'parts': [
                {'text': self.prompt}
            ],
        })
        self.contents.append({
            'role': 'model',
            'parts': [
                {'text': "好的，现在开始角色扮演"}
            ]
        })

    def updateCharacter(self):
        self.contents.append({
            'role': 'user',
            'parts': [
                {'text': "请允许我重述一下角色性格，以防你忘记，"
                 "然后接着刚刚的对话就好"+self.prompt}
            ],
        })
        self.contents.append({
            'role': 'model',
            'parts': [
                {'text': "好的，我了解了，我们继续刚才的对话"}
            ]
        })

    def updateHistory(self, text):
        user_pattern = r"user:(.*?)$(?:\nuser:|\n"+self.character+":|\Z)"
        model_pattern = r""+self.character + \
            ":(.*?)$(?:\nuser:|\n"+self.character+":|\Z)"

        # 查找所有匹配项
        user_dialogues = []
        model_dialogues = []

        for match in re.finditer(user_pattern, text, re.DOTALL | re.MULTILINE):
            dialogue = match.group(1).strip()
            user_dialogues.append(dialogue)

        for match in re.finditer(model_pattern, text, re.DOTALL | re.MULTILINE):
            dialogue = match.group(1).strip()
            model_dialogues.append(dialogue)

        for user_dia, model_dia in zip(user_dialogues, model_dialogues):
            self.contents.append({
                'role': 'user',
                'parts': [{'text': user_dia}]
            })

            self.contents.append({
                'role': 'model',
                'parts': [{'text': model_dia}]
            })

        return user_dialogues, model_dialogues

    def initHistory(self):
        self.store_path = "./data/"
        self.store_path = self.store_path + self.character
        if not os.path.exists(self.store_path):
            os.mkdir(self.store_path)

        date = datetime.datetime.now()
        self.file_name = date.strftime('%Y-%m-%d-%H-%M-%S')

    def addHistory(self, text, reply):
        if self.store_path == "./data/":
            self.store_path = self.store_path + self.character
            if not os.path.exists(self.store_path):
                os.mkdir(self.store_path)
            date = datetime.datetime.now()
            self.file_name = date.strftime('%Y-%m-%d-%H-%M-%S')

        if self.file:
            with open(f"{self.store_path}/{self.character}-{self.file_name}.txt", 'a', encoding='utf-8') as cntt:
                cntt.write(self.file)
                cntt.write('\n')  # 可选的换行符，视具体需求而定
            self.file = None

        with open(f"{self.store_path}/{self.character}-{self.file_name}.txt", 'a', encoding='utf-8') as cntt:
            cntt.write('user: ' + text + '\n')
        with open(f"{self.store_path}/{self.character}-{self.file_name}.txt", 'a', encoding='utf-8') as cntt:
            cntt.write(self.character + ': ' + reply + '\n')

    def updatePrompt(self, prompt):
        print(prompt)
        if prompt != 'None':
            if prompt == 'normal':
                self.CPrompt = self.normal
            else:
                self.CPrompt = self.jailBreak
            self.contents.append({
                'role': 'user',
                'parts': [
                    {'text': "请允许我重述一下设定，以防你忘记，"
                     "然后接着刚刚的对话就好"+self.CPrompt}
                ],
            })
            self.contents.append({
                'role': 'model',
                'parts': [
                    {'text': "好的，我了解了，我们继续刚才的对话"}
                ]
            })

    def getText(self, text, history):
        user_dias = None
        model_dias = None

        self.changeModels()

        if len(history) == 0:
            if self.count == 0:
                self.count = 1
                if self.file:
                    user_dias, model_dias = self.updateHistory(self.file)
            else:
                self.initContents()
                self.initHistory()
                if self.character:
                    self.initCharacter(self.character)
                if self.file:
                    user_dias, model_dias = self.updateHistory(self.file)

        # print("history1 : ")
        # print(history)

        user_content = {
            'role': 'user',
            'parts': [
                {'text': text}
            ],
        }
        self.contents.append(user_content)

        safety_settings = [
            {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_NONE'},
            {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_NONE'},
            {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
             'threshold': 'BLOCK_NONE'},
            {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
             'threshold': 'BLOCK_NONE'}
        ]
        try:
            response = self.model.generate_content(
                contents=self.contents,
                safety_settings=safety_settings,
            )
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.contents.pop()
            response = None
            print(text)
            pyperclip.copy(text)

        if response:

            model_content = {
                'role': 'model',
                'parts': [
                    {'text': response.text}
                ]
            }

            self.contents.append(model_content)

            if user_dias is not None and model_dias is not None:
                for user_dia, model_dia in zip(user_dias, model_dias):
                    history.append([user_dia, model_dia])

            history.append([text, response.text])

            self.addHistory(text, response.text)

        # print("history2 : ")
        # print(history)

        # print("Current contents :  ")
        # print(self.contents)
        # print("\n\n")
        # print("\n\n")
        return "", history


# gen = GenerateText()
# gen.__init__()
# gen.getText("你好啊")
