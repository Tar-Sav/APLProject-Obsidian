import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, simpledialog
import re, os, threading, datetime, configparser
import Obsidian_Parser
from Semantics import SemanticAnalyzer
from Interpreter import Interpreter

# ── Themes ────────────────────────────────────────────────────────────────────
# LIGHT = clean, airy default  |  DARK = synthwave neon fun mode

# Light mode — soft warm whites with slate accents
LIGHT = {
    "bg":        "#F7F5F0",
    "panel":     "#EDE9E0",
    "surface":   "#FDFCF8",
    "surface2":  "#EAE6DC",
    "border":    "#D4CEC0",
    "gutter_bg": "#EAE6DC",
    "gutter_fg": "#A09880",
    "text":      "#2C2A24",
    "text_dim":  "#6B6558",
    "text_muted":"#B0A898",
    "insert":    "#6366F1",
    "accent":    "#6366F1",
    "success":   "#3D7A4A",
    "warning":   "#A0620A",
    "error":     "#C0262E",
    "info":      "#7A7060",
    "run_fg":    "#3D7A4A",
    "clear_fg":  "#7A7060",
    "help_fg":   "#A0620A",
    "save_fg":   "#6366F1",
    "open_fg":   "#7C3AED",
    "ai_fg":     "#7C3AED",
    "status_bg": "#DDD8CE",
    "status_fg": "#9A9080",
    "highlight": "#E0DDFF",
}

# Dark mode — synthwave neon: hot pinks, electric purples, cyan on deep midnight
DARK = {
    "bg":        "#0D0D1A",
    "panel":     "#13102B",
    "surface":   "#0A0A18",
    "surface2":  "#1A1535",
    "border":    "#3D2F6E",
    "gutter_bg": "#1A1535",
    "gutter_fg": "#5A4A8A",
    "text":      "#F0E6FF",
    "text_dim":  "#9D7FC0",
    "text_muted":"#5A4A8A",
    "insert":    "#FF6AC1",
    "accent":    "#FF6AC1",
    "success":   "#3DFFB0",
    "warning":   "#FFD166",
    "error":     "#FF4DA6",
    "info":      "#7A5FA0",
    "run_fg":    "#3DFFB0",
    "clear_fg":  "#7A5FA0",
    "help_fg":   "#FFD166",
    "save_fg":   "#00D4FF",
    "open_fg":   "#BF5FFF",
    "ai_fg":     "#FF6AC1",
    "status_bg": "#080812",
    "status_fg": "#5A4A8A",
    "highlight": "#2D1F5A",
}

SYNTAX = {                          # token: (pattern, neon-dark, warm-light)
    "keyword":  (r'\b(if|else|then|while|for|print)\b', "#FF6AC1", "#7C3AED"),
    "datatype": (r'\b(int|float|char|bool|string)\b',   "#00D4FF", "#2563EB"),
    "boolean":  (r'\b(true|false)\b',                   "#FF4DA6", "#C0262E"),
    "string":   (r'"[^"]*"',                            "#3DFFB0", "#3D7A4A"),
    "char":     (r"'.'",                                "#FFD166", "#A0620A"),
    "number":   (r'\b\d+(?:\.\d+)?\b',                 "#FF9F43", "#C05010"),
    "comment":  (r'#[^\n]*',                            "#5A4A8A", "#A09880"),
    "operator": (r'==|!=|>=|<=|[+\-*/=><]',            "#BF5FFF", "#6366F1"),
}

REFERENCE = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OBSIDIAN  —  Syntax Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DATA TYPES
  int x = 5;       float y = 3.14;
  string s = "hi"; char c = 'A';
  bool b = true;

DECLARATION / ASSIGNMENT
  int x;       (declares, default 0)
  int x = 5;   (declare + assign)
  x = 10;      (assign, must be declared first)

PRINT          print(x);  print("hello");

OPERATORS      + - * /   == != > < >= <=

IF / ELSE
  if (cond) { ... } else { ... }

WHILE          while (cond) { ... }

FOR            for (int i=0; i<10; i=i+1) { ... }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NOT ALLOWED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✗ Use before declare   ✗ Duplicate declaration
  ✗ Missing ;            ✗ Missing { }
  ✗ Type mismatch        ✗ Division by zero
  ✗ char > 1 character   ✗ -bool
  ✗ do { }               ✗ // comments (use #)
"""

CLAUDE_PROMPT = """\
You are an execution simulator for a custom language called Obsidian.
Rules: int/float/string/char/bool types; declare before use; print(x) outputs;
if/else, while, for loops; blocks use {}; statements end with ;; comments use #.

For each simulation:
1. Trace each step as:  [STEP N] description
2. Variable changes shown inline.
3. Print output as:     OUTPUT: value
4. Errors as:           ERROR: explanation
5. Finish with:         SUMMARY — final variable states

Be concise and technical. No padding.
"""

# ── Persistent state ──────────────────────────────────────────────────────────
T            = LIGHT
current_theme = "light"
current_file  = None
is_modified   = False
api_key       = ""
ai_history    = []

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".obsidian_config")

def _load_cfg():
    global api_key
    c = configparser.ConfigParser()
    c.read(CONFIG_PATH)
    api_key = c.get("claude", "api_key", fallback="")

def _save_cfg():
    c = configparser.ConfigParser()
    c["claude"] = {"api_key": api_key}
    try:
        with open(CONFIG_PATH, "w") as f: c.write(f)
    except Exception: pass

_load_cfg()

# ── Editor ────────────────────────────────────────────────────────────────────
class Editor(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        self.lines = tk.Text(self, width=4, font=("Courier New", 12),
                             state="disabled", relief="flat", bd=0, padx=8, pady=6)
        self.lines.pack(side="left", fill="y")
        self.sep = tk.Frame(self, width=1)
        self.sep.pack(side="left", fill="y")
        self.text = tk.Text(self, font=("Courier New", 12), relief="flat",
                            bd=0, undo=True, padx=14, pady=6, wrap="none")
        self.text.pack(side="left", fill="both", expand=True)
        vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        vsb.pack(side="right", fill="y")
        self.text.config(yscrollcommand=vsb.set)
        self.vsb = vsb
        for name in SYNTAX: self.text.tag_configure(name)
        self.text.bind("<KeyRelease>", lambda e: (mark_modified(), self._highlight()))
        self._theme(); self._highlight()

    def _theme(self):
        self.config(bg=T["panel"])
        self.lines.config(bg=T["gutter_bg"], fg=T["gutter_fg"])
        self.sep.config(bg=T["border"])
        self.text.config(bg=T["surface"], fg=T["text"],
                         insertbackground=T["insert"],
                         selectbackground=T["highlight"],
                         selectforeground=T["text"])
        self.vsb.config(bg=T["surface2"], troughcolor=T["surface"],
                        activebackground=T["accent"])
        ci = 2 if current_theme == "light" else 1
        for name, vals in SYNTAX.items():
            self.text.tag_configure(name, foreground=vals[ci])

    def _highlight(self):
        code = self.text.get("1.0", tk.END)
        for name, (pat, *_) in SYNTAX.items():
            self.text.tag_remove(name, "1.0", tk.END)
            for m in re.finditer(pat, code):
                self.text.tag_add(name, f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        self.lines.config(state="normal")
        self.lines.delete("1.0", tk.END)
        self.lines.insert("1.0", "\n".join(str(i) for i in range(1, code.count("\n")+2)))
        self.lines.config(state="disabled")

    def get(self):    return self.text.get("1.0", tk.END).strip()
    def set(self, s): self.text.delete("1.0", tk.END); self.text.insert("1.0", s); self._highlight()
    def clear(self):  self.text.delete("1.0", tk.END); self._highlight()
    def apply_theme(self): self._theme()

# ── Helpers ───────────────────────────────────────────────────────────────────
def mark_modified():
    global is_modified
    if not is_modified:
        is_modified = True; _title()

def _title():
    n = os.path.basename(current_file) if current_file else "untitled.obs"
    root.title(f"Obsidian IDE  —  {n}{' •' if is_modified else ''}")

def _out(text="", tag=None):
    output.config(state="normal")
    if text == "":
        output.delete("1.0", tk.END)
    elif tag:
        output.insert(tk.END, text, tag)
    else:
        output.insert(tk.END, text)
    output.config(state="disabled")
    output.see(tk.END)

def status(msg, color=None):
    status_lbl.config(text=f"  {msg}", fg=color or T["status_fg"])

# ── Run ───────────────────────────────────────────────────────────────────────
def run():
    code = editor.get()
    _out()
    if not code: return _out("Nothing to run.\n", "info")
    status("Running…", T["warning"]); root.update_idletasks()
    ast, err = Obsidian_Parser.run(code)
    if err: return (_out(err.errorString()+"\n","error"), status("Parse error.", T["error"]))
    errs = SemanticAnalyzer().analyze(ast)
    if errs:
        for e in errs: _out(e.errorString()+"\n", "error")
        return status(f"{len(errs)} semantic error(s).", T["error"])
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): result, err = Interpreter().interpret(ast)
    printed = buf.getvalue()
    if printed: _out(printed)
    elif result is not None: _out(str(result)+"\n")
    else: _out("Done.\n", "info")
    if err: _out(err.errorString()+"\n","error"); status("Runtime error.", T["error"])
    else: status("Ran successfully.", T["success"])

# ── File ops ──────────────────────────────────────────────────────────────────
def new_file():
    global current_file, is_modified
    if is_modified and not messagebox.askyesno("Unsaved changes", "Discard changes?"): return
    editor.clear(); current_file = None; is_modified = False; _title()
    status("New file.", T["info"])

def open_file():
    global current_file, is_modified
    p = filedialog.askopenfilename(filetypes=[("Obsidian","*.obs"),("Text","*.txt"),("All","*.*")])
    if not p: return
    try:
        editor.set(open(p, encoding="utf-8").read())
        current_file = p; is_modified = False; _title()
        status(f"Opened  {os.path.basename(p)}", T["accent"])
    except Exception as e: messagebox.showerror("Open failed", str(e))

def save_file():
    if current_file: _write(current_file)
    else: save_as()

def save_as():
    global current_file
    p = filedialog.asksaveasfilename(defaultextension=".obs",
        filetypes=[("Obsidian","*.obs"),("Text","*.txt"),("All","*.*")])
    if p: _write(p); current_file = p; _title()

def _write(path):
    global is_modified
    try:
        open(path,"w",encoding="utf-8").write(editor.get())
        is_modified = False; _title()
        status(f"Saved  {os.path.basename(path)}", T["success"])
    except Exception as e: messagebox.showerror("Save failed", str(e))

# ── Theme ─────────────────────────────────────────────────────────────────────
def toggle_theme():
    global T, current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    T = LIGHT if current_theme == "light" else DARK
    theme_btn.config(text="🌙  Neon" if current_theme=="dark" else "☀  Light", fg=T["warning"])
    _apply_theme()

def _apply_theme():
    root.configure(bg=T["bg"])
    editor.apply_theme()
    output.config(bg=T["surface"], fg=T["success"], selectbackground=T["highlight"])
    output.tag_configure("error", foreground=T["error"])
    output.tag_configure("info",  foreground=T["info"])
    bar.config(bg=T["panel"]); bar_inner.config(bg=T["panel"])
    for btn, key in btn_map:
        btn.config(bg=T["surface2"], fg=T[key], activebackground=T[key], activeforeground=T["bg"])
    theme_btn.config(bg=T["surface2"], activebackground=T["warning"], activeforeground=T["bg"])
    status_bar.config(bg=T["status_bg"])
    status_lbl.config(bg=T["status_bg"], fg=T["status_fg"])
    hint_lbl.config(bg=T["status_bg"], fg=T["text_muted"])
    out_frame.config(bg=T["border"]); out_hdr.config(bg=T["panel"], fg=T["text_muted"])
    _title()

# ── Help window ───────────────────────────────────────────────────────────────
help_win = None

def toggle_help():
    global help_win
    if help_win:
        try: help_win.destroy()
        except tk.TclError: pass
        help_win = None; help_btn.config(text="?  Help"); return
    help_win = tk.Toplevel(root)
    help_win.title("Obsidian — Syntax Guide")
    help_win.configure(bg=T["surface2"]); help_win.resizable(False, True)
    root.update_idletasks()
    help_win.geometry(f"300x{root.winfo_height()}+{root.winfo_x()+root.winfo_width()+6}+{root.winfo_y()}")
    hdr = tk.Frame(help_win, bg=T["panel"], pady=8); hdr.pack(fill="x")
    tk.Label(hdr, text="◆  Syntax Guide", font=("Courier New",11,"bold"),
             bg=T["panel"], fg=T["accent"], padx=14).pack(side="left")
    def _close():
        global help_win
        try: help_win.destroy()
        except: pass
        help_win = None; help_btn.config(text="?  Help")
    tk.Button(hdr, text="✕", command=_close, font=("Courier New",10,"bold"),
              bg=T["panel"], fg=T["error"], relief="flat", bd=0, padx=10,
              cursor="hand2", activebackground=T["error"], activeforeground=T["bg"]
              ).pack(side="right", padx=6)
    tk.Frame(help_win, height=1, bg=T["border"]).pack(fill="x")
    t = scrolledtext.ScrolledText(help_win, font=("Courier New",10),
        bg=T["surface2"], fg=T["text_dim"], relief="flat", bd=0,
        padx=14, pady=10, wrap="word", state="normal")
    t.insert("1.0", REFERENCE); t.config(state="disabled"); t.pack(fill="both", expand=True)
    help_btn.config(text="✕  Help")
    help_win.protocol("WM_DELETE_WINDOW", _close)

# ── Claude AI window ──────────────────────────────────────────────────────────
ai_win = None

CLAUDE_MODELS = ["claude-haiku-4-5-20251001", "claude-sonnet-4-5"]

def _call_claude(code):
    try:
        from anthropic import Anthropic, RateLimitError
    except ModuleNotFoundError:
        return "ERROR: anthropic package not found.\nRun: pip install anthropic"

    prompt = f"Simulate:\n```\n{code}\n```"
    for model in CLAUDE_MODELS:
        try:
            client = Anthropic(api_key=api_key)
            r = client.messages.create(
                model=model, max_tokens=1024,
                system=CLAUDE_PROMPT,
                messages=[{"role":"user","content":prompt}],
            )
            return f"[Model: {model}]\n\n{r.content[0].text}"
        except RateLimitError:
            continue
        except Exception as e:
            return f"ERROR contacting Claude ({model}): {e}"
    return "ERROR: All Claude models hit rate limits. Please wait and try again."

def open_ai_window():
    global ai_win
    if ai_win:
        try: ai_win.lift(); ai_win.focus_force(); return
        except tk.TclError: ai_win = None

    ai_win = tk.Toplevel(root)
    ai_win.title("Obsidian — AI Simulation")
    ai_win.configure(bg=T["bg"]); ai_win.minsize(420, 400)
    root.update_idletasks()
    ai_win.geometry(f"500x{root.winfo_height()}+{root.winfo_x()+root.winfo_width()+6}+{root.winfo_y()}")

    # Header
    hdr = tk.Frame(ai_win, bg=T["panel"], pady=8); hdr.pack(fill="x")
    tk.Label(hdr, text="✨  AI Execution Simulator", font=("Courier New",11,"bold"),
             bg=T["panel"], fg=T["ai_fg"], padx=14).pack(side="left")
    tk.Label(hdr, text="Claude by Anthropic", font=("Courier New",9),
             bg=T["panel"], fg=T["text_muted"], padx=4).pack(side="left")

    def _close():
        global ai_win
        try: ai_win.destroy()
        except: pass
        ai_win = None; ai_btn.config(text="✨  AI Sim")

    tk.Button(hdr, text="✕", command=_close, font=("Courier New",10,"bold"),
              bg=T["panel"], fg=T["error"], relief="flat", bd=0, padx=10,
              cursor="hand2", activebackground=T["error"], activeforeground=T["bg"]
              ).pack(side="right", padx=6)
    tk.Frame(ai_win, height=1, bg=T["border"]).pack(fill="x")

    # API key bar
    key_bar = tk.Frame(ai_win, bg=T["surface2"], pady=6); key_bar.pack(fill="x")
    key_var = tk.StringVar(value="✔ API key loaded" if api_key else "No API key set")
    key_lbl = tk.Label(key_bar, textvariable=key_var, font=("Courier New",9),
                       bg=T["surface2"], fg=T["success"] if api_key else T["error"], padx=14)
    key_lbl.pack(side="left")

    def _set_key():
        global api_key
        k = simpledialog.askstring("Anthropic API Key",
            "Enter your Anthropic API key:\n(console.anthropic.com/settings/keys)\n\nSaved automatically.",
            show="*", parent=ai_win)
        if k and k.strip():
            api_key = k.strip(); _save_cfg()
            key_var.set("✔ API key saved"); key_lbl.config(fg=T["success"])
            status("Anthropic API key saved.", T["success"])

    tk.Button(key_bar, text="⚙  Set Key", command=_set_key,
              font=("Courier New",9,"bold"), bg=T["surface2"], fg=T["warning"],
              relief="flat", padx=10, pady=3, cursor="hand2", bd=0,
              activebackground=T["warning"], activeforeground=T["bg"]
              ).pack(side="right", padx=10)
    tk.Frame(ai_win, height=1, bg=T["border"]).pack(fill="x")

    # Output
    tk.Label(ai_win, text="  SIMULATION OUTPUT", font=("Courier New",9,"bold"),
             bg=T["panel"], fg=T["text_muted"], anchor="w", pady=4).pack(fill="x")
    sim = scrolledtext.ScrolledText(ai_win, font=("Courier New",11),
        bg=T["surface"], fg=T["text"], relief="flat", bd=0,
        padx=14, pady=10, state="disabled", wrap="word")
    sim.tag_configure("step",    foreground=T["accent"])
    sim.tag_configure("output",  foreground=T["success"])
    sim.tag_configure("error",   foreground=T["error"])
    sim.tag_configure("summary", foreground=T["warning"])
    sim.pack(fill="both", expand=True)
    tk.Frame(ai_win, height=1, bg=T["border"]).pack(fill="x")

    # History
    tk.Label(ai_win, text="  HISTORY", font=("Courier New",9,"bold"),
             bg=T["panel"], fg=T["text_muted"], anchor="w", pady=4).pack(fill="x")
    hist = scrolledtext.ScrolledText(ai_win, font=("Courier New",10),
        bg=T["surface2"], fg=T["text_dim"], relief="flat", bd=0,
        padx=14, pady=6, state="disabled", wrap="word", height=5)
    hist.pack(fill="x")
    tk.Frame(ai_win, height=1, bg=T["border"]).pack(fill="x")

    # Run bar
    run_bar = tk.Frame(ai_win, bg=T["panel"], pady=8); run_bar.pack(fill="x")
    spin_var = tk.StringVar()
    tk.Label(run_bar, textvariable=spin_var, font=("Courier New",10),
             bg=T["panel"], fg=T["warning"], padx=14).pack(side="left")

    def _render(text):
        sim.config(state="normal"); sim.delete("1.0", tk.END)
        for line in text.splitlines():
            s = line.strip()
            tag = ("step" if s.startswith("[STEP") else
                   "output" if s.startswith("OUTPUT:") else
                   "error"  if s.startswith("ERROR:") else
                   "summary" if s.startswith("SUMMARY") else None)
            sim.insert(tk.END, line+"\n", tag or "")
        sim.config(state="disabled"); sim.see(tk.END)

    def _refresh_hist():
        hist.config(state="normal"); hist.delete("1.0", tk.END)
        for e in reversed(ai_history[-20:]):
            hist.insert(tk.END, f"[{e['timestamp']}]  ")
            hist.insert(tk.END, e['code'][:60].replace("\n"," ")+"…\n")
        hist.config(state="disabled")

    def _simulate():
        code = editor.get()
        if not code: return messagebox.showinfo("No Code","Write some code first.",parent=ai_win)
        if not api_key: return messagebox.showwarning("No Key","Set your API key first.",parent=ai_win)
        sim_btn.config(state="disabled"); spin_var.set("⏳ Simulating…")
        def _work():
            result = _call_claude(code)
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            ai_history.append({"timestamp":ts,"code":code,"result":result,
                                "status":"err" if result.startswith("ERROR") else "ok"})
            ai_win.after(0, lambda: (_render(result), _refresh_hist(),
                                     spin_var.set(""), sim_btn.config(state="normal"),
                                     status("AI simulation complete.", T["ai_fg"])))
        threading.Thread(target=_work, daemon=True).start()

    sim_btn = tk.Button(run_bar, text="✨  Simulate with Claude", command=_simulate,
                        font=("Courier New",10,"bold"), bg=T["surface2"], fg=T["ai_fg"],
                        relief="flat", padx=14, pady=5, cursor="hand2", bd=0,
                        activebackground=T["ai_fg"], activeforeground=T["bg"])
    sim_btn.pack(side="right", padx=10)

    _refresh_hist()
    ai_btn.config(text="✕  AI Sim")
    ai_win.protocol("WM_DELETE_WINDOW", _close)

# ── Window ────────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("Obsidian IDE  —  untitled.obs")
root.configure(bg=T["bg"]); root.geometry("960x700"); root.minsize(700, 500)

bar = tk.Frame(root, bg=T["panel"], pady=6); bar.pack(fill="x")
tk.Label(bar, text="◆ OBSIDIAN", font=("Courier New",11,"bold"),
         bg=T["panel"], fg=T["accent"], padx=14).pack(side="left")
bar_inner = tk.Frame(bar, bg=T["panel"]); bar_inner.pack(side="right", padx=8)

editor = Editor(root); editor.pack(fill="both", expand=True)

out_frame = tk.Frame(root, bg=T["border"], pady=1); out_frame.pack(fill="x")
out_hdr = tk.Label(out_frame, text="  OUTPUT", font=("Courier New",9,"bold"),
                   bg=T["panel"], fg=T["text_muted"], padx=4, pady=4, anchor="w")
out_hdr.pack(fill="x")
output = scrolledtext.ScrolledText(root, height=8, font=("Courier New",12),
    bg=T["surface"], fg=T["success"], relief="flat", bd=0, padx=14, pady=8, state="disabled")
output.tag_configure("error", foreground=T["error"])
output.tag_configure("info",  foreground=T["info"])
output.pack(fill="x")

status_bar = tk.Frame(root, bg=T["status_bg"], pady=3); status_bar.pack(fill="x", side="bottom")
status_lbl = tk.Label(status_bar, text="  Ready.", font=("Courier New",9),
                      bg=T["status_bg"], fg=T["status_fg"], anchor="w")
status_lbl.pack(side="left")
hint_lbl = tk.Label(status_bar, font=("Courier New",9), anchor="e",
                    text="Ctrl+Enter Run  •  Ctrl+G AI  •  Ctrl+S Save  •  Ctrl+O Open   ",
                    bg=T["status_bg"], fg=T["text_muted"])
hint_lbl.pack(side="right")

FBTN = ("Courier New", 10, "bold")
def _btn(text, cmd): 
    b = tk.Button(bar_inner, text=text, command=cmd, font=FBTN, bg=T["surface2"],
                  relief="flat", padx=12, pady=5, cursor="hand2", bd=0)
    b.pack(side="left", padx=4); return b

run_btn   = _btn("▶  Run",    run)
save_btn  = _btn("⬇  Save",   save_file)
open_btn  = _btn("⬆  Open",   open_file)
new_btn   = _btn("✦  New",    new_file)
clear_btn = _btn("✕  Clear",  editor.clear)
ai_btn    = _btn("✨  AI Sim", open_ai_window)
help_btn  = _btn("?  Help",   toggle_help)
theme_btn = tk.Button(bar_inner, text="🌙  Neon", command=toggle_theme, font=FBTN,
                      bg=T["surface2"], fg=T["warning"], relief="flat", padx=12, pady=5,
                      cursor="hand2", bd=0, activebackground=T["warning"], activeforeground=T["bg"])
theme_btn.pack(side="left", padx=4)

btn_map = [(run_btn,"run_fg"),(save_btn,"save_fg"),(open_btn,"open_fg"),
           (new_btn,"accent"),(clear_btn,"clear_fg"),(ai_btn,"ai_fg"),(help_btn,"help_fg")]
for b, k in btn_map: b.config(fg=T[k], activebackground=T[k], activeforeground=T["bg"])

root.bind("<Control-Return>", lambda e: run())
root.bind("<Control-s>",      lambda e: save_file())
root.bind("<Control-S>",      lambda e: save_as())
root.bind("<Control-o>",      lambda e: open_file())
root.bind("<Control-n>",      lambda e: new_file())
root.bind("<Control-g>",      lambda e: open_ai_window())

_title()
status("Ready.  Ctrl+Enter to run  •  Ctrl+G to open AI simulator.", T["info"])
root.mainloop()