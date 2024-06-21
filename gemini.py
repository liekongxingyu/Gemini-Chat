import webbrowser
import gradio as gr
from parse import Parse

pa = Parse()

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="输入消息")

    with gr.Row():
        clear = gr.ClearButton([msg, chatbot])
        change_character = gr.Dropdown(
            choices=pa.getCharacters(), label="选择角色")
        change_character.change(pa.changeCharacter, inputs=change_character)
    with gr.Row():
        with gr.Column():
            btn = gr.Button(value="刷新设定")
            btn.click(fn=pa.updateCharacter)
            change_prompt = gr.Dropdown(
                choices=['normal', 'jailBreak', 'None'], label="选择预设")
            change_prompt.change(pa.changePrompt, inputs=change_prompt)
            with gr.Row():
                btn1 = gr.Button(value="角色目录")
                btn1.click(fn=pa.startCharacter)
                btn2 = gr.Button(value="数据目录")
                btn2.click(fn=pa.startData)
        with gr.Column():
            file_input = gr.File(label="上传聊天历史", file_types=['text'])
            file_input.change(fn=pa.updateHistory, inputs=file_input)

    msg.submit(pa.Chat, [msg, chatbot], [msg, chatbot])

webbrowser.open("http://127.0.0.1:7860")
demo.launch()
