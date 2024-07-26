import tkinter as tk

from Ui.ServerUi import ServerUi


def main():
    root = tk.Tk()
    app = ServerUi(root)
    root.mainloop()

if __name__ == '__main__':
    main()
