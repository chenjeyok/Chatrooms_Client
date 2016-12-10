import threading
import socket
import sys
import time
import select
import Tkinter as tk    # Python Official GUI Library
import Queue


if(len(sys.argv) < 3):
    print "Usage: python client.py server_ip server_port "
    sys.exit()

HOST = sys.argv[1]
PORT = int(sys.argv[2])


class Client(tk.Frame):
    def __init__(self, master=None):
        # Initalize Main Window
        tk.Frame.__init__(self, master)
        self.pack()

        # Initialize GUI Widgets
        self.CreateLogin()
        self.CreateUserList()

        # Initialize Communication threads
        try:
            self.CreateSocket()
            threading.Thread(target=self.CreateSender, args=()).start()
            threading.Thread(target=self.CreateReceiv, args=()).start()
            threading.Thread(target=self.MessageHandler, args=()).start()
        except Exception, emsg:
            print '[401]Init', str(emsg)

    def CreateSocket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(100)  # Related to broken socket judgement
            self.sock.connect((HOST, PORT))
            print "[000]Connected to server"
        except:
            print "[400]Unable to connect"
            raise

    def CreateSender(self):
        print '[001]Sender thread start'
        self.Send_Queue = Queue.Queue()
        while True:
            try:
                if not self.Send_Queue.empty():
                    Message = self.Send_Queue.get()
                    print Message
                    self.sock.send(Message)
                else:
                    time.sleep(0.1)
            except Exception, emsg:
                print '[430]Sender', str(emsg)
                time.sleep(1)

        print '[439]Sender down'
        return

    def CreateReceiv(self):
        print '[002]Receive thread start'
        self.Recv_Queue = Queue.Queue()
        while True:
            try:
                rlist = [self.sock]
                rlist, wlist, xlist = select.select(rlist, [], [])

                for sock in rlist:
                    Message = sock.recv(512)
                    # Assume connection broken if recv empty msg
                    if not Message:
                        raise IOError
                    # Put Message into Recv Queue
                    else:
                        print Message
                        self.Recv_Queue.put(Message)

            except IOError, emsg:
                print '[440]Receive empty data'
                time.sleep(1)
                # self.BrokenSocketHandler()

            except Exception, emsg:
                print '[441]Receive ', str(emsg)
                time.sleep(1)

        print '[449]Receiver down'
        return

    def MessageHandler(self):
        print '[003]Message Handler thread start'
        while True:
            try:
                if not self.Recv_Queue.empty():
                    Message = self.Recv_Queue.get()
                    Header = Message[0:5]

                    # Connection Success
                    if '[200]' in Header:
                        pass

                    # Login Success
                    elif '[201]' in Header:
                        self.button_1.config(state='normal')
                        self.button_2.config(state='disabled')
                        self.button_3.config(state='normal')
                        self.button_4.config(state='normal')
                        self.button_5.config(state='normal')

                    # UserString
                    elif '[202]'in Header:
                        UserString = Message[5:]
                        self.listbox_1_cv.set(UserString)

                    elif '[203]'in Header:
                        # start a new chatting window
                        pass

                    elif '[204]'in Header:
                        # connection alive
                        pass

                    elif '[205]'in Header:
                        # Put Broadcast MSG on Board
                        pass

                    elif '[206]'in Header:
                        pass

                    elif '[207]'in Header:
                        pass
                else:
                    time.sleep(1)

            except KeyboardInterrupt:
                raise
            except Exception, emsg:
                print '[450]Msg Handler', str(emsg)

        print '[459]Msg Handler down'
        return

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
        self.button_1 = tk.Button(self.label_1, text='B1 Logout', command=self.button_1_handler, width=15, height=3, state='disabled')
        self.button_1.bind('<Enter>', self.button_1_enter_handler)
        self.button_1.grid(row=2, column=0, rowspan=1, columnspan=1)

    # Label 1
        # - Button 2 Login
        self.button_2 = tk.Button(self.label_1, text='B2 Login', command=self.button_2_handler, width=15, height=3)
        self.button_2.grid(row=2, column=1, rowspan=1, columnspan=1 )

    def CreateUserList(self):
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
        self.button_3 = tk.Button(self.label_2, text='B3 Show Users', command=self.button_3_handler, width=15, height=3, state='disabled')
        self.button_3.grid(row=0, column=1, rowspan=1, columnspan=1)

    # Label 2
        # - Button 4
        self.button_4 = tk.Button(self.label_2, text='B4 Clear Users', command=self.button_4_handler, width=15, height=3, state='disabled')
        self.button_4.grid(row=1, column=1, rowspan=1, columnspan=1)

    # Label 2
        # - Button 5
        self.button_5 = tk.Button(self.label_2, text='B5 Chat With', command=self.button_5_handler, width=15, height=3, state='disabled')
        self.button_5.grid(row=2, column=1, rowspan=1, columnspan=1)

    # Button 1  Logout
    def button_1_handler(self):
        self.Send_Queue.put('[390]Logout:'+self.username)
        self.button_1.config(state='disabled')
        self.button_2.config(state='normal')
        self.button_3.config(state='disabled')
        self.button_4.config(state='disabled')
        self.button_5.config(state='disabled')
        self.listbox_1_cv.set('')
        print '[B01]Logout'

    # Button 1 Mouse Enter Handler
    # Event Handler takes 2 args:(self, event)
    def button_1_enter_handler(self, event):
        pass

    # Button 2 Click Handler
    # Nothing
    def button_2_handler(self):
        self.username = self.entry_1.get()
        if ':' in self.username:
            print '[B02]Illegal username'
        elif len(self.username) not in range(5, 20):
            print '[B02]Username too short or too long'
        else:
            # send username to login
            self.Send_Queue.put('[300]'+self.username)
            print '[B02]Login Request:', self.username

    # Button 3 Click Handler
    # Show Users when clicked
    def button_3_handler(self):
        self.Send_Queue.put('[350]User List Request')
        print '[B03]Show users'

    # Button 4 Click Handler
    # Clear Users when clicked
    def button_4_handler(self):
        s = ('')
        self.listbox_1_cv.set(s)
        print '[B04]Clear users'

    # Button 5 Click Handler
    # Pop a new window Chatting With
    def button_5_handler(self):
        try:
            choose_index = self.listbox_1.curselection()[0]
            peername = self.listbox_1.get(choose_index)
            if peername != self.username:
                self.Send_Queue.put('[310]'+peername)
                print '[B05]Chat Request', peername
            else:
                print '[B05]Not to Yourself', peername
        except Exception, emsg:
            print '[450]B05 ', str(emsg)

    # Entry 2 Password Return Handler
    # Print * mask passwd in terminal
    # Clear the entry (up to 50 chars)
    def entry_2_return_handler(self, event):
        print '[Ret]Password ', self.entry_2.get()
        self.entry_2.delete(first=0, last=50)


C1 = Client()
C1.master.title('Chatting Rooms Client')
C1.mainloop()
