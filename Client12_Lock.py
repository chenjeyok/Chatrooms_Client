import socket
import select
import threading
import sys
import time
import Queue
import Tkinter as tk    # Python Official GUI Library
import ttk              # Tkinter GUI V8.5 After
import tkMessageBox     # Python MessageBox GUI

# ============ SYS ARG =============

if(len(sys.argv) < 3):
    print "Usage: python client.py server_ip server_port "
    sys.exit()

HOST = sys.argv[1]
PORT = int(sys.argv[2])


# ========== CLIENT INIT ===========


class Client(tk.Frame):
    def __init__(self, master=None):
        # Initalize Main Window
        tk.Frame.__init__(self, master)
        self.pack()
        try:
            # Initialize GUI Widgets
            self.CreateLogin()
            self.CreateUserList()
            self.CreateChatList()

            # Initialize Sockets
            self.CreateSocket()

            # Thread Competing Lock when tring to reconnect to server
            self.Lock = False

            # Initialize Threads
            self.CreateThreads()

        except Exception, emsg:
            print '[401]Init', str(emsg)


# ========== SOCKET INIT ===========

    def CreateSocket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(100)  # Related to broken socket judgement
            self.sock.connect((HOST, PORT))
            print "[000] Connected to server"
        except:
            print "[400] Unable to connect"
            tkMessageBox.showinfo('Sorry', 'Unable to connect to Sever')
            self.quit()


# ========== THREADS ===========

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
        print '[002] Receiver thread start'
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
                            self.ChatPane.tab(0, text=self.username)

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
                            tkMessageBox.showinfo('Sorry', 'You\'re fored to be offline because the Server asked you to')
                            self.button_1_handler()

                    # Chat Signals are [21X], From 210 to 215
                    elif '[21' in Header:
                        # Chat Request Confirm
                        if '[210]'in Header:
                            pass

                        # Chat Invite
                        elif '[211]'in Header:
                            Caller = (Message[5:]).rstrip().lstrip()
                            Answer = tkMessageBox.askquestion(title=Caller, message='Hi, '+self.username+'\nWhat about a chat with me?')
                            if 'no' in Answer:
                                self.Send_Queue.put('[311]'+Caller)
                            elif 'yes' in Answer:
                                self.Send_Queue.put('[312]'+Caller)

                        # Chat Invite Refused
                        elif '[212]'in Header:
                            Callee = (Message[5:]).rstrip().lstrip()
                            tkMessageBox.showinfo(Callee, 'Refused your sincere offer to waste the lonely night together.\nTry another one :)')

                        # Chat Invite Accepted
                        elif '[213]'in Header:
                            PeerName = (Message[5:]).rstrip().lstrip()
                            print '[DB9]'+PeerName
                            self.CreateChatTab(PeerName)

                        # Chat Msg
                        elif '[214]'in Header:
                            Pos = Message.index(':')
                            Content = Message[Pos+1:]
                            PeerName = (Message[5:Pos]).rstrip().lstrip()
                            print '[DB8]'+PeerName+''+Content
                            if PeerName in self.ChatList.keys():
                                self.CreateScreen('<'+PeerName+'> '+time.strftime('%b-%d %H:%M', time.localtime(time.time())), PeerName)
                                self.CreateScreen('     '+Content, PeerName)
                            else:
                                self.Send_Queue.put('[215]'+PeerName)

                        # Chat Terminate Request
                        elif '[215]'in Header:
                            PeerName = (Message[5:]).rstrip().lstrip()
                            if PeerName in self.ChatList.keys():
                                self.ChatPane.forget(self.ChatList[PeerName])
                                self.ChatList.pop(PeerName)
                                tkMessageBox.showinfo(PeerName, PeerName+' Quit Chat')
                            else:
                                print '[DB7] User not in Chat'
                else:
                    time.sleep(0.1)

            except Exception, emsg:
                print '[450] Msg Handler', str(emsg)

        print '[459] Msg Handler down'
        return

# ========== UTILITY FUNCTIONS ===========

    # Reconnect to server when wrong with socket
    def Reconnect(self):
        try:
            self.CreateSocket()
        except:
            tkMessageBox.showinfo('Sorry', 'It\'s late at night and the Bar is closed, Quiting')
            self.sock.close()
            self.quit()


# ========== GUI REACT FUNCTIONS ===========

    # Button 1  Logout
    def button_1_handler(self):
        # Close Chat Tabs
        # Remove myself from others' ChatList
        for PeerName in self.ChatList.keys():
            self.Send_Queue.put('[314]'+PeerName)
            self.ChatPane.forget(self.ChatList[PeerName])
            self.ChatList.pop(PeerName)
            time.sleep(0.1)
        # Notify server the Logout
        self.Send_Queue.put('[390]'+self.username)

        self.button_1.config(state='disabled')
        self.button_2.config(state='normal')
        self.button_3.config(state='disabled')
        self.button_4.config(state='disabled')
        self.button_5.config(state='disabled')
        self.listbox_1_cv.set('')
        print '[B01] Logout'

    # Button 2 Login
    def button_2_handler(self):
        self.username = self.entry_1.get()
        self.password = self.entry_2.get()
        if ':' in self.username:
            print '[B02] Username illegal with : '
        elif ' ' in self.username:
            print '[B02] Username illegal with blankspace'
        elif len(self.username) not in range(5, 20):
            print '[B02] Username too short or too long'
        elif len(self.password) == 0:
            print '[B02] Password empty'
        else:
            # send username to login
            self.Send_Queue.put('[300]'+self.username+':'+self.password)
            print '[B02] Login Request:', self.username

    # Button 3 User List Query
    def button_3_handler(self):
        self.Send_Queue.put('[350]User List Request')
        print '[B03] Show users'

    # Button 4
    def button_4_handler(self):
        tkMessageBox.showinfo('Sorry', 'Didn\'t decide what to do with this button yet.')

    # Button 5 Chat Request
    def button_5_handler(self):
        try:
            choose_index = self.listbox_1.curselection()[0]
            PeerName = self.listbox_1.get(choose_index)
            if PeerName == self.username:
                print '[B05] Not to yourself,', PeerName
            elif PeerName in self.ChatList.keys():
                print '[B05] In Chat With', PeerName
            else:
                self.Send_Queue.put('[310]'+PeerName)
                print '[B05] Chat Request', PeerName
        except Exception, emsg:
            print '[450] B05 ', str(emsg)

    # Button 6 Quit
    def button_6_handler(self):
        print '[B06] Quit...'
        self.Lock = True
        self.sock.close()
        self.quit()

    # Button 7
    def button_7_handler(self):
        tkMessageBox.showinfo('Sorry', 'File Transmit Utility Under Developing')

    # Button 8
    def button_8_handler(self):
        tkMessageBox.showinfo('Sorry', 'Voice Utility Under Developing')

    # Button 9
    def button_9_handler(self):
        tkMessageBox.showinfo('Sorry', 'Didn\'t decide what to do with this button yet.')

    def Button_Send_handler(self, PeerName):
        Content = self.ChatList[PeerName].entry.get()
        self.ChatList[PeerName].entry.delete(0, 50)
        if len(Content) > 0:
            self.Send_Queue.put('[313]'+PeerName+':'+Content)
            self.CreateScreen('<'+self.username+'> '+time.strftime('%b-%d %H:%M', time.localtime(time.time())), PeerName)
            self.CreateScreen('    '+Content, PeerName)
            print '[DB0]'+Content
        else:
            print '[DB0]'+' Empty Content'

    def Button_Term_handler(self, PeerName):
        # close PeerName Tab
        self.ChatPane.forget(self.ChatList[PeerName])
        self.ChatList.pop(PeerName)
        # Send terminate request
        self.Send_Queue.put('[314]'+PeerName)


# ========== GUI INIT ===========

    # Login Frame GUI
    def CreateLogin(self):
        self.labelFrame_1 = tk.LabelFrame(self, text='Label 1 Login')  # , width=50, height=50)
        self.labelFrame_1.grid(row=0, column=0, rowspan=1, columnspan=2, sticky=tk.N+tk.W, pady=0, padx=4)
        # label_acc
        self.label_acc = tk.Label(self.labelFrame_1, text='Username', width=10, height=1)
        self.label_acc.grid(row=0, column=0, rowspan=1, columnspan=1)
        # label_pas
        self.label_pas = tk.Label(self.labelFrame_1, text='Password', width=10, height=1)
        self.label_pas.grid(row=1, column=0, rowspan=1, columnspan=1)
        # Entry 1 Username Entry
        self.entry_1 = tk.Entry(self.labelFrame_1, text='E1 Username', width=20)
        self.entry_1.grid(row=0, column=1, rowspan=1, columnspan=1)
        # Entry 2 Password Entry
        self.entry_2 = tk.Entry(self.labelFrame_1, text='E2 Password', width=20, show='*')
        self.entry_2.grid(row=1, column=1, rowspan=1, columnspan=1)
        # Button 1 Logout
        self.button_1 = tk.Button(self.labelFrame_1, text='B1 Logout', command=self.button_1_handler, width=10, height=1, state='disabled')
        self.button_1.grid(row=2, column=0, rowspan=1, columnspan=1)
        # Button 2 Login
        self.button_2 = tk.Button(self.labelFrame_1, text='B2 Login', command=self.button_2_handler, width=10, height=1)
        self.button_2.grid(row=2, column=1, rowspan=1, columnspan=1 )

    def CreateUserList(self):
        self.labelFrame_2 = tk.LabelFrame(self, text='Label 2 Users')
        self.labelFrame_2.grid(row=1, column=0, rowspan=1, columnspan=2, sticky=tk.W, pady=4, padx=4)
        # Listbox 1 Users Online
        self.listbox_1_cv = tk.StringVar()
        self.listbox_1 = tk.Listbox(self.labelFrame_2, width=20, height=16, listvariable=self.listbox_1_cv)
        self.listbox_1.grid(row=0, column=0, rowspan=4, columnspan=1, padx=2, pady=4)
        # Button 3 UserList Query
        self.button_3 = tk.Button(self.labelFrame_2, text='B3 Show Users', command=self.button_3_handler, width=10, height=1, state='disabled')
        self.button_3.grid(row=0, column=1, rowspan=1, columnspan=1, padx=2)
        # Button 4
        self.button_4 = tk.Button(self.labelFrame_2, text='B4 ', command=self.button_4_handler, width=10, height=1, state='disabled')
        self.button_4.grid(row=1, column=1, rowspan=1, columnspan=1)
        # Button 5 Chat with
        self.button_5 = tk.Button(self.labelFrame_2, text='B5 Chat With', command=self.button_5_handler, width=10, height=1, state='disabled')
        self.button_5.grid(row=2, column=1, rowspan=1, columnspan=1)
        # Button 6 Quit
        self.button_6 = tk.Button(self.labelFrame_2, text='B6 Quit App', command=self.button_6_handler, width=10, height=1)
        self.button_6.grid(row=3, column=1, rowspan=1, columnspan=1)

    def CreateChatList(self):
        self.ChatList = {}

        self.labelFrame_3 = tk.LabelFrame(self, text='Label 3 Chats')
        self.labelFrame_3.grid(row=0, column=2, rowspan=2, columnspan=6, sticky=tk.N, pady=4, padx=4)

        self.ChatPane = ttk.Notebook(self.labelFrame_3, width=450, height=335)
        self.ChatPane.grid(row=0, column=0, rowspan=2, columnspan=6, sticky=tk.N, pady=2, padx=2)

        self.NewUserTab = tk.Frame()  # Later Use a class to wrap this Frame as a chat box
        self.ChatPane.add(self.NewUserTab, text='New User')

    def CreateChatTab(self, PeerName):
        self.ChatList[PeerName] = tk.Frame()  # Later Use a class to wrap this Frame as a chat box
        self.AddWidgetsToFrame(self.ChatList[PeerName], PeerName)
        self.ChatPane.add(self.ChatList[PeerName], text=PeerName)
        self.ChatPane.select(self.ChatList[PeerName])

    def CreateScreen(self, Content, PeerName):
        try:
            length = len(self.ChatList[PeerName].ScreenList)
            self.ChatList[PeerName].ScreenList.append(Content)
            if length > 15:
                CurrentList = self.ChatList[PeerName].ScreenList[-16:]
            else:
                CurrentList = self.ChatList[PeerName].ScreenList
            ScreenString = ''
            for line in CurrentList:
                ScreenString = ScreenString + line + '\n'
            self.ChatList[PeerName].ChatContent.set(ScreenString)
        except Exception, emsg:
            print '[455] SCR ', str(emsg)

    def AddWidgetsToFrame(self, Frame, PeerName):
        Frame.PeerName = PeerName
        Frame.ChatContent = tk.StringVar()
        Frame.ScreenList = ['Entered Room, Now You Can Start']
        Frame.ScreenString = 'Entered Room, Now You Can Start'
        Frame.ChatContent.set(Frame.ScreenString)

        Frame.labelFrame_3_1 = tk.LabelFrame(Frame)
        Frame.labelFrame_3_2 = tk.LabelFrame(Frame)

        Frame.textWindow = tk.Label(Frame.labelFrame_3_1, width=48, height=16, textvariable=Frame.ChatContent, anchor=tk.NW, justify="left")
        Frame.button_7 = tk.Button(Frame.labelFrame_3_2, text='B7 File  ', width=9, command=self.button_7_handler)
        Frame.button_8 = tk.Button(Frame.labelFrame_3_2, text='B8 Voice ', width=9, command=self.button_8_handler)
        Frame.button_9 = tk.Button(Frame.labelFrame_3_2, text='B9       ', width=9, command=self.button_9_handler)
        Frame.Button_T = tk.Button(Frame.labelFrame_3_2, text='Terminate', command=lambda: self.Button_Term_handler(Frame.PeerName), width=9)
        Frame.entry = tk.Entry(Frame.labelFrame_3_2, width=35)
        # Frame.entry.bind('<Return>', lambda: self.Button_Send_handler(Frame.PeerName))
        Frame.send = tk.Button(Frame.labelFrame_3_2, text='Send', command=lambda: self.Button_Send_handler(Frame.PeerName), width=5)

        Frame.labelFrame_3_1.grid(row=0, column=0, sticky=tk.N)
        Frame.labelFrame_3_2.grid(row=1, column=0, sticky=tk.S)  # , sticky=tk.W)

        Frame.textWindow.grid(row=0, column=0, rowspan=1, columnspan=2, padx=4, pady=0)
        Frame.button_7.grid(row=0, column=0)
        Frame.button_8.grid(row=0, column=1)
        Frame.button_9.grid(row=0, column=2)
        Frame.Button_T.grid(row=0, column=3)
        Frame.entry.grid(row=1, column=0, columnspan=3)
        Frame.send.grid(row=1, column=3, columnspan=1)


# ========== START ===========
# Main Thread
C1 = Client()
C1.master.title('Chatting Rooms Client')
print '[004] Local button thread start'
C1.mainloop()
