from Tkinter import *


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.CreateWidgets()

    def ckbt_response(self):
        self.chkbt.flash()

    def CreateWidgets(self):
        self.chkbt = Checkbutton(self, text='The ckbt')  # Pass self as Master
        self.chkbt.pack()



app1 = Application()
app1.master.title('ckbt')
app1.mainloop()


