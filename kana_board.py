import tkinter as tk
import tkinter.font as tkfont
import platform
import sys

DECIDE_MS = 4000  # カーソル・モールス共通タイマー（ミリ秒）
MODE_SWITCH_MORSE = 'ーーーーーー'  # モード切替モールス符号（ツー6回）

# 和文モールス符号対応表（・=トン、ー=ツー）
MORSE_MAP = {
    # あ行
    'あ': 'ーー・ーー', 'い': '・ー',      'う': '・・ー',    'え': 'ー・ーーー', 'お': '・ー・・・',
    # か行
    'か': '・ー・・',   'き': 'ー・ー・・', 'く': '・・・ー',  'け': 'ー・ーー',   'こ': 'ーーーー',
    # さ行
    'さ': 'ー・ー・ー', 'し': 'ーー・ー・', 'す': 'ーーー・ー', 'せ': '・ーーー・', 'そ': 'ーーー・',
    # た行
    'た': 'ー・',       'ち': '・・ー・',   'つ': '・ーー・',  'て': '・ー・ーー', 'と': '・・ー・・',
    # な行
    'な': '・ー・',     'に': 'ー・ー・',   'ぬ': '・・・・',  'ね': 'ーー・ー',   'の': '・・ーー',
    # は行
    'は': 'ー・・・',   'ひ': 'ーー・・ー', 'ふ': 'ーー・・',  'へ': '・',         'ほ': 'ー・・',
    # ま行
    'ま': 'ー・・ー',   'み': '・・ー・ー', 'む': 'ー',        'め': 'ー・・・ー',  'も': 'ー・・ー・',
    # や行
    'や': '・ーー',     'ゆ': 'ー・・ーー', 'よ': 'ーー',
    # ら行
    'ら': '・・・',     'り': 'ーー・',     'る': 'ー・ーー・', 'れ': 'ーーー',     'ろ': '・ー・ー',
    # わ行・ん
    'わ': 'ー・ー',     'を': '・ーーー',   'ん': '・ー・ー・',
    # 小文字（親字と同じ符号）
    'ゃ': '・ーー',     'ゅ': 'ー・・ーー', 'ょ': 'ーー',
    # 記号
    '゛': '・・',       '゜': '・・ーー・', 'ー': '・ーー・ー',
    '.': '・ー・ー・ー',
    '削除': '・・・ー・',
    # 数字（国際モールス符号）
    '0': 'ーーーーー',  '1': '・ーーーー',  '2': '・・ーーー',
    '3': '・・・ーー',  '4': '・・・・ー',  '5': '・・・・・',
    '6': 'ー・・・・',  '7': 'ーー・・・',  '8': 'ーーー・・',
    '9': 'ーーーー・',
}

# モールス符号 → 文字の逆引き辞書（先勝ち：通常かなが小文字より優先）
MORSE_REVERSE = {}
for _char, _code in MORSE_MAP.items():
    if _code not in MORSE_REVERSE:
        MORSE_REVERSE[_code] = _char

class KanaBoard:
    def __init__(self, root, morse_mode=False):
        self.root = root
        self.root.title("かなボード")
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)
        self.root.columnconfigure(0, weight=1)

        # フォント
        self.base_fontsize = 20
        self.kana_font = tkfont.Font(family='Arial', size=self.base_fontsize)
        self.morse_font = tkfont.Font(family='Arial', size=max(8, int(self.base_fontsize * 0.45)))

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
            ['ょ', '.', 'ろ', '゜', 'も', 'ほ', 'の', 'と', 'そ', 'こ', 'お'],
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
        self.morse_labels = []
        for i, row in enumerate(self.kana):
            row_labels = []
            for j, char in enumerate(row):
                morse = MORSE_MAP.get(char, '')
                cell = tk.Frame(bottom_frame, relief=tk.RAISED, bd=2)
                cell.grid(row=i, column=j, padx=2, pady=2, sticky='nsew')
                kana_lbl = tk.Label(cell, text=char, font=self.kana_font)
                kana_lbl.pack(expand=True, fill=tk.BOTH)
                morse_lbl = tk.Label(cell, text=morse, font=self.morse_font)
                morse_lbl.pack(expand=True, fill=tk.BOTH)
                self.morse_labels.append(morse_lbl)
                for w in (cell, kana_lbl, morse_lbl):
                    w.bind('<Button-1>', lambda event, r=i, c=j: self.on_label_click(r, c))
                row_labels.append(cell)
            self.labels.append(row_labels)

        # デフォルト背景色を保存（クロスプラットフォーム対応）
        _tmp = tk.Label(bottom_frame)
        self._default_label_bg = _tmp.cget('bg')
        _tmp.destroy()

        # 数字ラベル
        num_labels = []
        for j, num in enumerate(self.numbers):
            morse = MORSE_MAP.get(num, '')
            cell = tk.Frame(bottom_frame, relief=tk.RAISED, bd=2)
            cell.grid(row=len(self.kana), column=j, padx=2, pady=2, sticky='nsew')
            kana_lbl = tk.Label(cell, text=num, font=self.kana_font)
            kana_lbl.pack(expand=True, fill=tk.BOTH)
            morse_lbl = tk.Label(cell, text=morse, font=self.morse_font)
            morse_lbl.pack(expand=True, fill=tk.BOTH)
            self.morse_labels.append(morse_lbl)
            for w in (cell, kana_lbl, morse_lbl):
                w.bind('<Button-1>', lambda event, r=len(self.kana), c=j: self.on_label_click(r, c))
            num_labels.append(cell)
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
        # モード状態
        self.morse_mode = morse_mode
        self.morse_buffer = ''
        self.morse_timer = None
        self.on_switch_focus = False
        self.update_focus(start_timer=False)  # 初回はタイマー起動しない

        # キーイベント（常に受け取るためbind_allを使用）
        self.root.bind_all('<Right>', self.move_right)
        self.root.bind_all('<Down>', self.move_down)
        self.root.bind_all('<Left>', self.move_left)
        self.root.bind_all('<Up>', self.move_up)

        # 説明ラベル
        instructions_frame = tk.Frame(root)
        instructions_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        self.label1 = tk.Label(instructions_frame, text="吹く：←", font=('Arial', 14))
        self.label1.pack(side=tk.LEFT, padx=20)
        self.label2 = tk.Label(instructions_frame, text="吸う：↓", font=('Arial', 14))
        self.label2.pack(side=tk.LEFT, padx=20)
        self.morse_buffer_label = tk.Label(instructions_frame, text='', font=('Arial', 14),
                                           width=12, anchor='w')
        self.mode_btn = tk.Button(instructions_frame, text='モールスモードへ', font=('Arial', 14),
                                  command=self.toggle_mode)
        self.mode_btn.pack(side=tk.RIGHT, padx=20)
        # ボタンのデフォルト背景色を保存
        _tmp_btn = tk.Button(instructions_frame)
        self._default_btn_bg = _tmp_btn.cget('bg')
        _tmp_btn.destroy()
        self._apply_mode()

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
        size_h = max(10, int(h / ((max_row + 2) * 2.0)))  # セルごとに2行（かな＋符号）
        new_size = min(size_w, size_h)
        # 80%に調整
        new_size = int(new_size * 0.8)
        if new_size < 10:
            new_size = 10
        self.kana_font.configure(size=new_size)
        self.morse_font.configure(size=max(7, int(new_size * 0.45)))
        self.display.configure(font=self.kana_font)

    def update_focus(self, start_timer=False):
        # 切り替えボタンフォーカスを解除
        if self.on_switch_focus:
            self.on_switch_focus = False
            self.mode_btn.config(bg=self._default_btn_bg)
        # 全てのセルをデフォルト
        for row in self.labels:
            for cell in row:
                cell.config(bg=self._default_label_bg)
                for w in cell.winfo_children():
                    w.config(bg=self._default_label_bg)

        # 現在のフォーカスをハイライト
        cell = self.labels[self.current_row][self.current_col]
        cell.config(bg='yellow')
        for w in cell.winfo_children():
            w.config(bg='yellow')

        # タイマーリセット
        if self.timer:
            self.root.after_cancel(self.timer)
        if start_timer:
            self.timer = self.root.after(DECIDE_MS, self.select_char)

    def move_right(self, event):
        self.current_col = (self.current_col + 1) % len(self.labels[self.current_row])
        self.update_focus(start_timer=True)

    def move_left(self, event):
        if self.morse_mode:
            self.morse_input('ー')
        else:
            self.current_col = (self.current_col - 1) % len(self.labels[self.current_row])
            self.update_focus(start_timer=True)

    def move_down(self, event):
        if self.morse_mode:
            self.morse_input('・')
        else:
            # 削除ポジション（最終行・最終列）から下でモード切替ボタンへ
            if (self.current_row == len(self.labels) - 1 and
                    self.current_col == len(self.numbers) - 1):
                self._focus_switch_button()
            else:
                self.current_row = (self.current_row + 1) % len(self.labels)
                if self.current_col >= len(self.labels[self.current_row]):
                    self.current_col = 0
                self.update_focus(start_timer=True)

    def move_up(self, event):
        self.current_row = (self.current_row - 1) % len(self.labels)
        if self.current_col >= len(self.labels[self.current_row]):
            self.current_col = 0
        self.update_focus(start_timer=True)

    def _focus_switch_button(self):
        """モード切替ボタンにフォーカスを移してタイマーを起動する。"""
        self.on_switch_focus = True
        for row in self.labels:
            for cell in row:
                cell.config(bg=self._default_label_bg)
                for w in cell.winfo_children():
                    w.config(bg=self._default_label_bg)
        self.mode_btn.config(bg='yellow')
        if self.timer:
            self.root.after_cancel(self.timer)
        self.timer = self.root.after(DECIDE_MS, self._switch_from_button)

    def _switch_from_button(self):
        """タイマー経過でモード切替を実行する。"""
        self.timer = None
        self.on_switch_focus = False
        self.mode_btn.config(bg=self._default_btn_bg)
        self.toggle_mode()

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

    def toggle_mode(self):
        self.morse_mode = not self.morse_mode
        self._apply_mode()

    def _apply_mode(self):
        # 切り替えボタンフォーカスを解除
        if self.on_switch_focus:
            self.on_switch_focus = False
            self.mode_btn.config(bg=self._default_btn_bg)
        if self.morse_mode:
            for morse_lbl in self.morse_labels:
                morse_lbl.pack(expand=True, fill=tk.BOTH)
            self.label1.config(text='吹く：ー')
            self.label2.config(text='吸う：・')
            self.mode_btn.config(text='カーソルモードへ\n' + MODE_SWITCH_MORSE)
            self.morse_buffer_label.pack(side=tk.LEFT, padx=10)
            # カーソルモードのタイマーをキャンセル
            if self.timer:
                self.root.after_cancel(self.timer)
                self.timer = None
        else:
            for morse_lbl in self.morse_labels:
                morse_lbl.pack_forget()
            self.label1.config(text='吹く：←')
            self.label2.config(text='吸う：↓')
            self.mode_btn.config(text='モールスモードへ')
            # モールスモードのタイマー・バッファをクリア
            if self.morse_timer:
                self.root.after_cancel(self.morse_timer)
                self.morse_timer = None
            self.morse_buffer = ''
            self.morse_buffer_label.config(text='')
            self.morse_buffer_label.pack_forget()

    def morse_input(self, symbol):
        self.morse_buffer += symbol
        self.morse_buffer_label.config(text=self.morse_buffer)
        if self.morse_timer:
            self.root.after_cancel(self.morse_timer)
        self.morse_timer = self.root.after(DECIDE_MS, self.morse_decide)

    def _focus_char(self, char):
        """グリッド内でcharを探してフォーカスを移動する。"""
        for i, row in enumerate(self.kana):
            for j, c in enumerate(row):
                if c == char:
                    self.current_row, self.current_col = i, j
                    self.update_focus(start_timer=False)
                    return
        for j, c in enumerate(self.numbers):
            if c == char:
                self.current_row = len(self.kana)
                self.current_col = j
                self.update_focus(start_timer=False)
                return

    def morse_decide(self):
        self.morse_timer = None
        buf = self.morse_buffer
        self.morse_buffer = ''
        self.morse_buffer_label.config(text='')
        # モード切替符号（ツー6回）
        if buf == MODE_SWITCH_MORSE:
            self.toggle_mode()
            return
        # 訂正符号「ラタ」・・・ー・ → 削除
        if buf == '・・・ー・':
            if self.display.get('1.0', tk.END).strip():
                self.display.delete('end-2c', 'end')
            self._focus_char('削除')
            return
        char = MORSE_REVERSE.get(buf)
        if not char:
            return
        if char == '゛':
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
        else:
            self.display.insert(tk.END, char)
            self.display.see(tk.END)
        self._focus_char(char)

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
    morse_mode = '-m' in sys.argv
    root = tk.Tk()
    # 起動時にウィンドウを最大化（クロスプラットフォーム対応）
    if platform.system() == 'Windows':
        root.state('zoomed')
    else:
        root.attributes('-zoomed', True)
    app = KanaBoard(root, morse_mode=morse_mode)
    root.mainloop()
