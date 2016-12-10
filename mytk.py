from Tkinter import *
import tkMessageBox


class Application_1(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.helloLabel = Label(self, text='Hello, world!')
        self.helloLabel.pack()
        self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.pack()

class Application_2(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.nameInput = Entry(self)
        self.nameInput.pack()
        self.alertButton = Button(self, text='Hello', command=self.helloBox)
        self.alertButton.pack()

    def helloBox(self):
        name = self.nameInput.get() or 'World'
        tkMessageBox.showinfo('Message', 'Hello %s' % name)



#app1 = Application_1()
# set window title
#app1.master.title('Hello World')
# Message loop This is blocking!!!
#app1.mainloop()

app2 = Application_2()
app2.master.title("Hello app2")
app2.mainloop()

