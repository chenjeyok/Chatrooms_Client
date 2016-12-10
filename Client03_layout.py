import Tkinter as tk
import threading
import Queue


class Client(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()

        self.CreateLogin()
        self.CreateUsers()
        self.CreateChats()

    def CreateLogin(self):
    # Label 1
        self.label_1 = tk.LabelFrame(self, text='Label 1 Login', width=500, height=50)
        self.label_1.grid(row=0, column=0, rowspan=1, columnspan=2)
    # Label 1
        # label_acc
        self.label_acc = tk.Label(self.label_1, text='Username', width=15, height=1)
        self.label_acc.grid(row=0, column=0, rowspan=1, columnspan=1)
    # Label 1
        # label_pas
        self.label_pas = tk.Label(self.label_1, text='Password', width=15, height=1)
        self.label_pas.grid(row=1, column=0, rowspan=1, columnspan=1)
    # Label 1
        # - Entry 1 Username Entry
        self.entry_1 = tk.Entry(self.label_1, text='E1 Username', width=20)
        self.entry_1.grid(row=0, column=1, rowspan=1, columnspan=1)

    # Label 1
        # - Entry 2 Password Entry
        self.entry_2 = tk.Entry(self.label_1, text='E2 Password', width=20, show='*')
        self.entry_2.bind('<Return>', self.entry_2_return_handler)
        self.entry_2.grid(row=1, column=1, rowspan=1, columnspan=1)

    # Label 1
        # - Button 1
        self.button_1 = tk.Button(self.label_1, text='B1 Activate B2', command=self.button_1_handler, width=15, height=3)
        self.button_1.bind('<Enter>', self.button_1_enter_handler)
        self.button_1.grid(row=2, column=0, rowspan=1, columnspan=1)

    # Label 1
        # - Button 2 Login
        self.button_2 = tk.Button(self.label_1, text='B2 Login', command=self.button_2_handler, width=15, height=3, state='disabled')
        self.button_2.grid(row=2, column=1, rowspan=1, columnspan=1 )

    def CreateUsers(self):

    # Label 2
        self.label_2 = tk.LabelFrame(self, text='Label 2 Users', width=500, height=200)
        self.label_2.grid(row=1, column=0, rowspan=1, columnspan=2)

    # Label 2
        # - Listbox 1 Users Online
        self.listbox_1_cv = tk.StringVar()
        self.listbox_1 = tk.Listbox(self.label_2, width=20, height=15, listvariable=self.listbox_1_cv)
        self.listbox_1.grid(row=0, column=0, rowspan=4, columnspan=1)

    # Label 2
        # - Button 3
        self.button_3 = tk.Button(self.label_2, text='B3 Show Users', command=self.button_3_handler, width=15, height=3)
        self.button_3.grid(row=0, column=1, rowspan=1, columnspan=1)

    # Label 2
        # - Button 4
        self.button_4 = tk.Button(self.label_2, text='B4 Clear Users', command=self.button_4_handler, width=15, height=3)
        self.button_4.grid(row=1, column=1, rowspan=1, columnspan=1)

    # Label 2
        # - Button 5
        self.button_5 = tk.Button(self.label_2, text='B5 Chat With', command=self.button_5_handler, width=15, height=3)
        self.button_5.grid(row=2, column=1, rowspan=1, columnspan=1)

    def CreateChats(self):
        self.chats = {}

    # Button 1 Click Handler

    def button_1_handler(self):
        self.button_2.config(state='active')
        print 'Button 1 Clicked'

    # Button 1 Mouse Enter Handler
    # Event Handler takes 2 args:(self, event)
    def button_1_enter_handler(self, event):
        print 'Button 1 Mouse Enter', event.time, event.type

    # Button 2 Click Handler
    # Nothing
    def button_2_handler(self):
        self.username = self.entry_1.get()
        if len(self.username) in range(5, 20):
            # send username to login
            pass
            print 'Button 2 username validated'
        else:
            print 'Button 2 username invalidate'

    # Button 3 Click Handler
    # Show Users when clicked
    def button_3_handler(self):
        s = ('Lester GeorgeBizet BryceLoski BernardShaw JimmyHentrix WhoeverItis Uptownfunk')
        self.listbox_1_cv.set(s)
        print 'Button 3 show users'

    # Button 4 Click Handler
    # Clear Users when clicked
    def button_4_handler(self):
        s = ('')
        self.listbox_1_cv.set(s)
        print 'Button 4 clear users'

    # Button 5 Click Handler
    # Pop a new window Chatting With
    def button_5_handler(self):
        choose_index=self.listbox_1.curselection()[0]
        threading.Thread(target=self.ChatWindow, args=(self.listbox_1.get(choose_index), choose_index)).start()


    # Entry 2 Password Return Handler
    # Print * mask passwd in terminal
    # Clear the entry (up to 50 chars)
    def entry_2_return_handler(self, event):
        print 'Return   password ', self.entry_2.get()
        self.entry_2.delete(first=0, last=50)

    def ChatWindow(self, peer, index):
        if peer not in self.chats.keys():
            self.chats[peer] = tk.Toplevel(self)
            self.chats[peer].title(peer)
            print 'Button 5 chat window with', peer
        else:
            print 'Button 5 chat window exists', peer



C1 = Client()
C1.master.title('Chatting Rooms Client')
C1.mainloop()
