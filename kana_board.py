import tkinter as tk
import tkinter.font as tkfont

class KanaBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("かなボード")
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)
        self.root.columnconfigure(0, weight=1)

        # フォント
        self.base_fontsize = 20
        self.kana_font = tkfont.Font(family='Arial', size=self.base_fontsize)

        # 上部フレーム for display
        top_frame = tk.Frame(root)
        top_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        top_frame.rowconfigure(0, weight=1)
        top_frame.columnconfigure(0, weight=1)

        # 表示エリア
        self.display = tk.Text(top_frame, height=3, wrap=tk.WORD, font=self.kana_font)
        self.display.grid(row=0, column=0, sticky='nsew')

        # 下部フレーム for grid
        bottom_frame = tk.Frame(root)
        bottom_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

        # ひらがなグリッド
        self.kana = [
            ['〇', 'わ', 'ら', 'や', 'ま', 'は', 'な', 'た', 'さ', 'か', 'あ'],
            ['×', 'を', 'り', 'ゆ', 'み', 'ひ', 'に', 'ち', 'し', 'き', 'い'],
            ['ゃ', 'ん', 'る', 'よ', 'む', 'ふ', 'ぬ', 'つ', 'す', 'く', 'う'],
            ['ゅ', 'ー', 'れ', '゛', 'め', 'へ', 'ね', 'て', 'せ', 'け', 'え'],
            ['ょ', '？', 'ろ', '゜', 'も', 'ほ', 'の', 'と', 'そ', 'こ', 'お'],
        ]

        # ひらがな→半濁点付き変換辞書
        self.handakuon_map = {
            'は': 'ぱ', 'ひ': 'ぴ', 'ふ': 'ぷ', 'へ': 'ぺ', 'ほ': 'ぽ',
        }

        # ひらがな→濁点付き変換辞書
        self.dakuon_map = {
            'か': 'が', 'き': 'ぎ', 'く': 'ぐ', 'け': 'げ', 'こ': 'ご',
            'さ': 'ざ', 'し': 'じ', 'す': 'ず', 'せ': 'ぜ', 'そ': 'ぞ',
            'た': 'だ', 'ち': 'ぢ', 'つ': 'づ', 'て': 'で', 'と': 'ど',
            'は': 'ば', 'ひ': 'び', 'ふ': 'ぶ', 'へ': 'べ', 'ほ': 'ぼ',
            'う゛': 'ゔ',
        }

        # 数字
        self.numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '削除']

        # ラベルを作成
        self.labels = []
        for i, row in enumerate(self.kana):
            row_labels = []
            for j, char in enumerate(row):
                label = tk.Label(bottom_frame, text=char, font=self.kana_font, width=3, height=2, relief=tk.RAISED)
                label.grid(row=i, column=j, padx=2, pady=2, sticky='nsew')
                label.bind('<Button-1>', lambda event, r=i, c=j: self.on_label_click(r, c))
                row_labels.append(label)
            self.labels.append(row_labels)

        # 数字ラベル
        num_labels = []
        for j, num in enumerate(self.numbers):
            label = tk.Label(bottom_frame, text=num, font=self.kana_font, width=3, height=2, relief=tk.RAISED)
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
        self.current_col = 10  # 「あ」の位置
        self.timer = None
        self.update_focus(start_timer=False)  # 初回はタイマー起動しない

        # キーイベント（常に受け取るためbind_allを使用）
        self.root.bind_all('<Right>', self.move_right)
        self.root.bind_all('<Down>', self.move_down)
        self.root.bind_all('<Left>', self.move_left)
        self.root.bind_all('<Up>', self.move_up)

        # 説明ラベル
        instructions_frame = tk.Frame(root)
        instructions_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        label1 = tk.Label(instructions_frame, text="吹く：←", font=('Arial', 14))
        label1.pack(side=tk.LEFT, padx=20)
        label2 = tk.Label(instructions_frame, text="吸う：↓", font=('Arial', 14))
        label2.pack(side=tk.LEFT, padx=20)

        # リサイズイベント
        self.root.bind('<Configure>', self.on_resize)

    def on_resize(self, event):
        # ウィンドウ幅・高さからフォントサイズを決定
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        # ひらがな・数字グリッドの最大行・列数
        max_row = len(self.labels)
        max_col = max(len(row) for row in self.labels)
        # 目安: 横幅の1/col数, 高さの1/(行数+2)の0.5倍程度
        size_w = max(10, int(w / (max_col * 1.5)))
        size_h = max(10, int(h / ((max_row + 2) * 1.5)))
        new_size = min(size_w, size_h)
        # 80%に調整
        new_size = int(new_size * 0.8)
        if new_size < 10:
            new_size = 10
        self.kana_font.configure(size=new_size)
        self.display.configure(font=self.kana_font)

    def update_focus(self, start_timer=False):
        # 全てのラベルをデフォルト
        for row in self.labels:
            for label in row:
                label.config(bg='SystemButtonFace')

        # 現在のフォーカスをハイライト
        self.labels[self.current_row][self.current_col].config(bg='yellow')

        # タイマーリセット
        if self.timer:
            self.root.after_cancel(self.timer)
        if start_timer:
            self.timer = self.root.after(3000, self.select_char)

    def move_right(self, event):
        self.current_col = (self.current_col + 1) % len(self.labels[self.current_row])
        self.update_focus(start_timer=True)

    def move_left(self, event):
        self.current_col = (self.current_col - 1) % len(self.labels[self.current_row])
        self.update_focus(start_timer=True)

    def move_down(self, event):
        self.current_row = (self.current_row + 1) % len(self.labels)
        if self.current_col >= len(self.labels[self.current_row]):
            self.current_col = 0
        self.update_focus(start_timer=True)

    def move_up(self, event):
        self.current_row = (self.current_row - 1) % len(self.labels)
        if self.current_col >= len(self.labels[self.current_row]):
            self.current_col = 0
        self.update_focus(start_timer=True)

    def select_char(self):
        if self.current_row < len(self.kana):
            char = self.kana[self.current_row][self.current_col]
        else:
            char = self.numbers[self.current_col]
        if char == '削除':
            # 最後の文字を削除
            if self.display.get('1.0', tk.END).strip():
                self.display.delete('end-2c', 'end')
        elif char == '゛':
            # 直前の文字を濁点付きに変換
            text = self.display.get('1.0', tk.END)
            if text.strip():
                last = text.rstrip('\n')[-1]
                if last in self.dakuon_map:
                    self.display.delete('end-2c', 'end')
                    self.display.insert(tk.END, self.dakuon_map[last])
        elif char == '゜':
            # 直前の文字を半濁点付きに変換
            text = self.display.get('1.0', tk.END)
            if text.strip():
                last = text.rstrip('\n')[-1]
                if last in self.handakuon_map:
                    self.display.delete('end-2c', 'end')
                    self.display.insert(tk.END, self.handakuon_map[last])
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
        elif char == '゛':
            text = self.display.get('1.0', tk.END)
            if text.strip():
                last = text.rstrip('\n')[-1]
                if last in self.dakuon_map:
                    self.display.delete('end-2c', 'end')
                    self.display.insert(tk.END, self.dakuon_map[last])
        elif char == '゜':
            text = self.display.get('1.0', tk.END)
            if text.strip():
                last = text.rstrip('\n')[-1]
                if last in self.handakuon_map:
                    self.display.delete('end-2c', 'end')
                    self.display.insert(tk.END, self.handakuon_map[last])
        elif char:
            self.display.insert(tk.END, char)
            self.display.see(tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    root.state('zoomed')  # 起動時にウィンドウを最大化
    app = KanaBoard(root)
    root.mainloop()
