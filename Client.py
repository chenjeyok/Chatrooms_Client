import socket
import select
import threading
import sys
import time
import Queue
import Tkinter as tk    # Python Official GUI Library
import tkMessageBox     # Python MessageBox GUI

# ============ SYS ARG =============

if(len(sys.argv) < 3):
    print "Usage: python client.py server_ip server_port "
    sys.exit()

HOST = sys.argv[1]
PORT = int(sys.argv[2])

# ==================================


class Client(tk.Frame):
    def __init__(self, master=None):
        # Initalize Main Window
        tk.Frame.__init__(self, master)
        self.pack()
        try:
            # Initialize GUI Widgets
            self.CreateLogin()
            self.CreateUserList()

            # Initialize Sockets
            self.CreateSocket()

            # Thread Competing Lock when tring to reconnect to server
            self.Lock = False

            # Initialize Threads
            self.CreateThreads()

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

    def CreateThreads(self):

        self.T_Sender = threading.Thread(target=self.CreateSender, args=())
        self.T_Sender.setDaemon(True)
        self.T_Sender.start()

        self.T_Receiv = threading.Thread(target=self.CreateReceiv, args=())
        self.T_Receiv.setDaemon(True)
        self.T_Receiv.start()

        self.T_MsgHnd = threading.Thread(target=self.MessageHandler, args=())
        self.T_MsgHnd.setDaemon(True)
        self.T_MsgHnd.start()

    def CreateSender(self):
        print '[001] Sender thread start'
        self.Send_Queue = Queue.Queue()
        while True:
            try:
                if not self.Send_Queue.empty():
                    Message = self.Send_Queue.get()
                    print '[Snd]' + Message
                    self.sock.send(Message)
                else:
                    time.sleep(0.1)
            except Exception, emsg:
                print '[430] Sender', str(emsg)
                self.Send_Queue.put(Message)  # Put unsent Msg back in Queue
                if self.Lock is False:
                    self.Lock = True
                    self.sock.close()
                    self.Reconnect()
                    self.Lock = False

        print '[439] Sender down'
        return

    def CreateReceiv(self):
        print '[002] Receive thread start'
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
                        print '[Rcv]' + Message
                        self.Recv_Queue.put(Message)
            except Exception, emsg:
                print '[440] Receive ', str(emsg)
                if self.Lock is False:
                    self.Lock = True
                    self.sock.close()
                    self.Reconnect()
                    self.Lock = False

        print '[449] Receiver down'
        return

    def MessageHandler(self):
        print '[003] Message Handler thread start'
        while True:
            try:
                if not self.Recv_Queue.empty():
                    Message = self.Recv_Queue.get()
                    Header = Message[0:5]

                    # Basic Connection Signals are [20X], From 200 to 209
                    if '[20' in Header:
                        # Connection Success
                        if '[200]' in Header:
                            pass

                        # Login Reply
                        elif '[201]' in Header:
                            self.button_1.config(state='normal')
                            self.button_2.config(state='disabled')
                            self.button_3.config(state='normal')
                            self.button_4.config(state='normal')
                            self.button_5.config(state='normal')

                        # UserList Update
                        elif '[202]'in Header:
                            UserList = Message[5:]
                            self.listbox_1_cv.set(UserList)

                        # Connection Query
                        elif '[204]'in Header:
                            # time.sleep(1)
                            # self.Put_to_Send_Queue("[370]Connection alive")
                            pass

                        # Broadcast Msg
                        elif '[205]'in Header:
                            # Put Broadcast MSG on Board
                            pass

                        # .
                        elif '[206]'in Header:
                            pass

                        # Logout Msg From Server
                        elif '[209]'in Header:
                            tkMessageBox.showinfo('Sorry', 'Force Offline')
                            self.button_1_handler()

                    # Chat Signals are [21X], From 210 to 215
                    elif '[21' in Header:
                        # Chat Request Confirm
                        if '[210]'in Header:
                            pass

                        # Chat Invite
                        elif '[211]'in Header:
                            Callee = (Message[5:]).rstrip().lstrip()
                            # Ask Box
                            # If no Refuse
                            # self.Send_Queue.put('[311]'+self.username)
                            # If yes Accept
                            # self.Send_Queue.put('[312]'+self.username)

                        # Chat Invite Refused
                        elif '[212]'in Header:
                            Callee = (Message[5:]).rstrip().lstrip()
                            tkMessageBox.showinfo('Sorry', Callee+' Refused Chat')

                        # Chat Invite Accepted
                        elif '[213]'in Header:
                            PeerName = (Message[5:]).rstrip().lstrip()
                            print PeerName

                        # Chat Msg
                        elif '[214]'in Header:
                            pass

                        # Chat Terminate Request
                        elif '[215]'in Header:
                            pass
                else:
                    time.sleep(0.1)

            except Exception, emsg:
                print '[450] Msg Handler', str(emsg)

        print '[459] Msg Handler down'
        return

    # Reconnect to server when wrong with socket
    def Reconnect(self):
        try:
            self.CreateSocket()
        except:
            tkMessageBox.showinfo('Sorry', 'Server Closed, Quiting')
            self.sock.close()
            self.quit()

    # Button 1  Logout
    def button_1_handler(self):
        self.Send_Queue.put('[390]Logout:'+self.username)
        self.button_1.config(state='disabled')
        self.button_2.config(state='normal')
        self.button_3.config(state='disabled')
        self.button_4.config(state='disabled')
        self.button_5.config(state='disabled')
        self.listbox_1_cv.set('')
        print '[B01] Logout'

    # Button 1 Mouse Enter Handler
    # Event Handler takes 2 args:(self, event)
    def button_1_enter_handler(self, event):
        pass

    # Button 2 User Login
    def button_2_handler(self):
        self.username = self.entry_1.get()
        if ':' in self.username:
            print '[B02] Username illegal with : '
        elif ' ' in self.username:
            print '[B02] Username illegal with blankspace'
        elif len(self.username) not in range(5, 20):
            print '[B02] Username too short or too long'
        else:
            # send username to login
            self.Send_Queue.put('[300]'+self.username)
            print '[B02] Login Request:', self.username

    # Button 3 User List Query
    def button_3_handler(self):
        self.Send_Queue.put('[350]User List Request')
        print '[B03] Show users'

    # Button 4
    def button_4_handler(self):
        pass

    # Button 5 Chat Request
    def button_5_handler(self):
        try:
            choose_index = self.listbox_1.curselection()[0]
            peername = self.listbox_1.get(choose_index)
            if peername != self.username:
                self.Send_Queue.put('[310]'+peername)
                print '[B05] Chat Request', peername
            else:
                print '[B05] Not to yourself,', peername
        except Exception, emsg:
            print '[450] B05 ', str(emsg)

    # Button 5 Quit
    def button_6_handler(self):
        print '[B06] Quit...'
        # self.Send_Queue.put('[390]Logout:'+self.username)
        self.sock.close()
        self.quit()

    # Entry 2 Password Return Handler
    def entry_2_return_handler(self, event):
        print '[Ret] Password ', self.entry_2.get()
        self.entry_2.delete(first=0, last=50)

    # Login Frame GUI
    def CreateLogin(self):
        self.labelFrame_1 = tk.LabelFrame(self, text='Label 1 Login', width=500, height=50)
        self.labelFrame_1.grid(row=0, column=0, rowspan=1, columnspan=2)
        # label_acc
        self.label_acc = tk.Label(self.labelFrame_1, text='Username', width=15, height=1)
        self.label_acc.grid(row=0, column=0, rowspan=1, columnspan=1)
        # label_pas
        self.label_pas = tk.Label(self.labelFrame_1, text='Password', width=15, height=1)
        self.label_pas.grid(row=1, column=0, rowspan=1, columnspan=1)
        # Entry 1 Username Entry
        self.entry_1 = tk.Entry(self.labelFrame_1, text='E1 Username', width=20)
        self.entry_1.grid(row=0, column=1, rowspan=1, columnspan=1)
        # Entry 2 Password Entry
        self.entry_2 = tk.Entry(self.labelFrame_1, text='E2 Password', width=20, show='*')
        self.entry_2.bind('<Return>', self.entry_2_return_handler)
        self.entry_2.grid(row=1, column=1, rowspan=1, columnspan=1)
        # Button 1 Logout
        self.button_1 = tk.Button(self.labelFrame_1, text='B1 Logout', command=self.button_1_handler, width=15, height=3, state='disabled')
        self.button_1.bind('<Enter>', self.button_1_enter_handler)
        self.button_1.grid(row=2, column=0, rowspan=1, columnspan=1)
        # Button 2 Login
        self.button_2 = tk.Button(self.labelFrame_1, text='B2 Login', command=self.button_2_handler, width=15, height=3)
        self.button_2.grid(row=2, column=1, rowspan=1, columnspan=1 )

    def CreateUserList(self):
        self.labelFrame_2 = tk.LabelFrame(self, text='Label 2 Users', width=500, height=200)
        self.labelFrame_2.grid(row=1, column=0, rowspan=1, columnspan=2)
        # Listbox 1 Users Online
        self.listbox_1_cv = tk.StringVar()
        self.listbox_1 = tk.Listbox(self.labelFrame_2, width=20, height=15, listvariable=self.listbox_1_cv)
        self.listbox_1.grid(row=0, column=0, rowspan=4, columnspan=1)
        # Button 3 UserList Query
        self.button_3 = tk.Button(self.labelFrame_2, text='B3 Show Users', command=self.button_3_handler, width=15, height=3, state='disabled')
        self.button_3.grid(row=0, column=1, rowspan=1, columnspan=1)
        # Button 4
        self.button_4 = tk.Button(self.labelFrame_2, text='B4 Clear Users', command=self.button_4_handler, width=15, height=3, state='disabled')
        self.button_4.grid(row=1, column=1, rowspan=1, columnspan=1)
        # Button 5 Chat with
        self.button_5 = tk.Button(self.labelFrame_2, text='B5 Chat With', command=self.button_5_handler, width=15, height=3, state='disabled')
        self.button_5.grid(row=2, column=1, rowspan=1, columnspan=1)
        # Button 6 Quit
        self.button_6 = tk.Button(self.labelFrame_2, text='B6 Quit App', command=self.button_6_handler, width=15, height=3)
        self.button_6.grid(row=3, column=1, rowspan=1, columnspan=1)

# Main Thread
C1 = Client()
C1.master.title('Chatting Rooms Client')
C1.mainloop()
