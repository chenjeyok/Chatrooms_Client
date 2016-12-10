import Tkinter as tk


class Client(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.CreateLogin()
        self.CreateWidgets()


    def CreateLogin(self):
        # Label 1
        self.label_1 = tk.LabelFrame(self, text='Label 1 Login', width=300, height=50)
        self.label_1.grid(row=0, column=0, rowspan=1, columnspan=2)

        # Label 1
        # - Entry 1 Username Entry
        self.entry_1 = tk.Entry(self.label_1, text='E1 Username', width=20)
        self.entry_1.grid(row=0, column=0, rowspan=1, columnspan=1)

        # Label 1
        # - Entry 2 Password Entry
        self.entry_2 = tk.Entry(self.label_1, text='E2 Password', width=20, show='*')
        self.entry_2.bind('<Return>', self.entry_2_return_handler)
        self.entry_2.grid(row=0, column=1, rowspan=1, columnspan=1)

    def CreateWidgets(self):
        # Button 1
        self.button_1 = tk.Button(self, text='Button 1', command=self.button_1_handler, width=15, height=3)
        self.button_1.bind('<Enter>', self.button_1_enter_handler)
        self.button_1.grid(row=1, column=0, rowspan=1, columnspan=1)

        # Button 2 Disabled Button
        self.button_2 = tk.Button(self, text='Disabled Button', width=15, height=3, state='disabled')
        self.button_2.grid(row=1, column=1, rowspan=1, columnspan=1 )


        # Listbox 1 Users Online
        self.listbox_1_cv = tk.StringVar()
        self.listbox_1 = tk.Listbox(self, width=20, height=15, listvariable=self.listbox_1_cv)
        self.listbox_1.grid(row=3, column=0, rowspan=4, columnspan=1)

    # Button 1 Click Handler
    # Do most handler work in this demo

    def button_1_handler(self):
        self.button_2.config(state='active')
        s = ('Tom Jack Ben Leo BryceLoski Minner')
        self.listbox_1_cv.set(s)
        print 'Button 1 Clicked'

    # Button 1 Mouse Enter Handler
    # Event Handler takes 2 args:(self, event)
    def button_1_enter_handler(self, event):
        print 'Button 1 Mouse Enter', event.time, event.type

    # Entry 2 Password Return Handler
    # Print * mask passwd in terminal
    # Clear the entry (up to 50 chars)
    def entry_2_return_handler(self, event):
        print 'Password ', self.entry_2.get()
        self.entry_2.delete(first=0, last=50)


C1 = Client()
C1.master.title('Chatting Rooms Client')
C1.mainloop()
