from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window

# 背景顏色 (白色)
Window.clearcolor = (1, 1, 1, 1)

class MyApp(App):
    def build(self):
        # 垂直排列容器
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # 標題
        self.label = Label(
            text='Kivy 測試成功！',
            font_name="C:/Windows/Fonts/msgothic.ttc",  # ✅ 支援中文/日文
            font_size='24sp',
            color=(0, 0, 0, 1)  # 黑色字
        )

        # 按鈕
        button = Button(
            text='點我變更文字',
            font_name="C:/Windows/Fonts/msgothic.ttc",  # ✅ 支援中文/日文
            font_size='20sp',
            size_hint=(1, 0.3),
            background_color=(0.2, 0.6, 1, 1)  # 藍色按鈕
        )
        button.bind(on_press=self.change_text)

        # 加入畫面
        layout.add_widget(self.label)
        layout.add_widget(button)

        return layout

    def change_text(self, instance):
        self.label.text = '你按了按鈕！'

# 啟動App
if __name__ == '__main__':
    MyApp().run()
