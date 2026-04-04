import tkinter as tk

class KanaBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("かなボード")
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)
        self.root.columnconfigure(0, weight=1)

        # 上部フレーム for display
        top_frame = tk.Frame(root)
        top_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        top_frame.rowconfigure(0, weight=1)
        top_frame.columnconfigure(0, weight=1)

        # 表示エリア
        self.display = tk.Text(top_frame, height=3, wrap=tk.WORD, font=('Arial', 14))
        self.display.grid(row=0, column=0, sticky='nsew')

        # 下部フレーム for grid
        bottom_frame = tk.Frame(root)
        bottom_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

        # ひらがなグリッド
        self.kana = [
            ['〇', 'わ', 'ら', 'や', 'ま', 'は', 'な', 'た', 'さ', 'か', 'あ'],
            ['×', 'を', 'り', 'ゆ', 'み', 'ひ', 'に', 'ち', 'し', 'き', 'い'],
            ['ゃ', 'ん', 'る', 'よ', 'む', 'ふ', 'ぬ', 'つ', 'す', 'く', 'う'],
            ['ゅ', 'ー', 'れ', '＊', 'め', 'へ', 'ね', 'て', 'せ', 'け', 'え'],
            ['ょ', '？', 'ろ', '・', 'も', 'ほ', 'の', 'と', 'そ', 'こ', 'お'],
        ]

        # 数字
        self.numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '削除']

        # ラベルを作成
        self.labels = []
        for i, row in enumerate(self.kana):
            row_labels = []
            for j, char in enumerate(row):
                label = tk.Label(bottom_frame, text=char, font=('Arial', 20), width=3, height=2, relief=tk.RAISED)
                label.grid(row=i, column=j, padx=2, pady=2, sticky='nsew')
                label.bind('<Button-1>', lambda event, r=i, c=j: self.on_label_click(r, c))
                row_labels.append(label)
            self.labels.append(row_labels)

        # 数字ラベル
        num_labels = []
        for j, num in enumerate(self.numbers):
            label = tk.Label(bottom_frame, text=num, font=('Arial', 20), width=3, height=2, relief=tk.RAISED)
            label.grid(row=len(self.kana), column=j, padx=2, pady=2, sticky='nsew')
            label.bind('<Button-1>', lambda event, r=len(self.kana), c=j: self.on_label_click(r, c))
            num_labels.append(label)
        self.labels.append(num_labels)

        # グリッドのリサイズ対応
        for i in range(len(self.kana) + 1):
            bottom_frame.rowconfigure(i, weight=1)
        for j in range(len(self.numbers)):
            bottom_frame.columnconfigure(j, weight=1)

        # 初期フォーカス
        self.current_row = 0
        self.current_col = 0
        self.timer = None
        self.update_focus()

        # キーイベント
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<Down>', self.move_down)
        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Up>', self.move_up)

        # 説明ラベル
        instructions_frame = tk.Frame(root)
        instructions_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        label1 = tk.Label(instructions_frame, text="吹く：↓", font=('Arial', 14))
        label1.pack(side=tk.LEFT, padx=20)
        label2 = tk.Label(instructions_frame, text="吸う：→", font=('Arial', 14))
        label2.pack(side=tk.LEFT, padx=20)

    def update_focus(self):
        # 全てのラベルをデフォルト
        for row in self.labels:
            for label in row:
                label.config(bg='SystemButtonFace')

        # 現在のフォーカスをハイライト
        self.labels[self.current_row][self.current_col].config(bg='yellow')

        # タイマーリセット
        if self.timer:
            self.root.after_cancel(self.timer)
        self.timer = self.root.after(2000, self.select_char)

    def move_right(self, event):
        self.current_col = (self.current_col + 1) % len(self.labels[self.current_row])
        self.update_focus()

    def move_left(self, event):
        self.current_col = (self.current_col - 1) % len(self.labels[self.current_row])
        self.update_focus()

    def move_down(self, event):
        self.current_row = (self.current_row + 1) % len(self.labels)
        if self.current_col >= len(self.labels[self.current_row]):
            self.current_col = 0
        self.update_focus()

    def move_up(self, event):
        self.current_row = (self.current_row - 1) % len(self.labels)
        if self.current_col >= len(self.labels[self.current_row]):
            self.current_col = 0
        self.update_focus()

    def select_char(self):
        if self.current_row < len(self.kana):
            char = self.kana[self.current_row][self.current_col]
        else:
            char = self.numbers[self.current_col]
        if char == '削除':
            # 最後の文字を削除
            if self.display.get('1.0', tk.END).strip():
                self.display.delete('end-2c', 'end')
        elif char:
            self.display.insert(tk.END, char)
            self.display.see(tk.END)

    def on_label_click(self, row, col):
        self.current_row = row
        self.current_col = col
        self.update_focus(start_timer=False)
        if row < len(self.kana):
            char = self.kana[row][col]
        else:
            char = self.numbers[col]
        if char == '削除':
            if self.display.get('1.0', tk.END).strip():
                self.display.delete('end-2c', 'end')
        elif char:
            self.display.insert(tk.END, char)
            self.display.see(tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    app = KanaBoard(root)
    root.mainloop()
