from chat import GenerateText

import os


class Parse:
    def __init__(self) -> None:
        self.gt = GenerateText()

    def startCharacter(self):
        relative_path = './character'
        directory_path = os.path.abspath(relative_path)
        os.startfile(directory_path)
    
    def startData(self):
        relative_path = './data'
        directory_path = os.path.abspath(relative_path)
        os.startfile(directory_path)

    def updateHistory(self, file):
        if file:
            with open(file.name, "r", encoding='utf-8') as f:
                text = f.read()
            self.gt.updateHistory(text)
            self.gt.file = text
            print("done")

    def updateCharacter(self):
        self.gt.updateCharacter()
        print("updateCharacter done")

    def getCharacters(self):
        folder_path = './character'
        file_names = os.listdir(folder_path)
        txt_files = [os.path.splitext(
            file_name)[0] for file_name in file_names if file_name.endswith('.txt')]
        return txt_files

    def changeCharacter(self, character):
        print(character)
        self.gt.character = character
        self.gt.initCharacter(character)
        self.gt.initHistory()

    def changePrompt(self, prompt):
        self.gt.updatePrompt(prompt)

    def Chat(self, message, history):
        return self.gt.getText(message, history)
