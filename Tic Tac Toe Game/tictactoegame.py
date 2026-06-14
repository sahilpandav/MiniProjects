import tkinter as tk
from tkinter import messagebox

window = tk.Tk()
window.title("Tic Tac Toe")

buttons = []
current_player = "X"

WIN_COMBOS = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]

def check_winner():
    for combo in WIN_COMBOS:
        a, b, c = combo

        if (buttons[a]["text"] == buttons[b]["text"] == buttons[c]["text"] and buttons[a]["text"] != ""):
            return buttons[a]["text"]
    return None

def check_draw():
    for btn in buttons:
        if btn["text"] == "":
            return False
    return True

def reset_game():
    global current_player
    current_player = "X"
    for btn in buttons:
        btn["text"] = ""

def on_click(index):
    global current_player

    if buttons[index]["text"] != "":
        return
    
    buttons[index]["text"] = current_player

    winner = check_winner()
    if winner:
        messagebox.showinfo("Game Over", f"Player {winner} wins!")
        reset_game()
        return
    
    if check_draw():
        messagebox.showinfo("Game Over", "It's a draw!")
        reset_game()
        return
    
    current_player = "O" if current_player == "X" else "X"

for i in range(9):
    btn = tk.Button(window, text="", width=10, height=3,  font=("Arial", 20),
                    command=lambda i=i: on_click(i))
    btn.grid(row=i // 3, column=i % 3)
    buttons.append(btn)

reset_btn = tk.Button(window, text="Reset", font=("Arial", 14), command=reset_game)
reset_btn.grid(row=3, column=0, columnspan=3, sticky="we")


window.mainloop()