from threading import Thread
from tkinter import Button, Tk, Label

from playsound3 import playsound
from playsound3.playsound3 import Sound

SOUND_PATH = "sound/alarm.mp3"

class Alert:
    def __init__(self, message: str):
        self.message = message
        self.sound = None
        self.t_sound = None
        self.ringing = True

    def show(self):
        # Start ringing in a separate thread
        self.t_sound = Thread(target=self.ring)
        self.t_sound.start()

        # Show the alert window
        root = Tk()
        root.protocol("WM_DELETE_WINDOW", lambda: self.stop_ringing(root))
        root.title("Alert")
        root.geometry("300x300")
        Label(root, text=self.message).pack(pady=20)
        Button(root, text="Stop Alert", command=lambda: self.stop_ringing(root)).pack(pady=10)
        root.mainloop()
    

    def stop_ringing(self, root):
        self.ringing = False
        if self.sound and self.sound.is_alive():
            self.sound.stop()
            print("Alert sound stopped.")
        root.destroy()

    def ring(self):
        print("Alert sound is ringing...")
        while self.ringing:
            self.sound = playsound(SOUND_PATH, block=False)
            while self.sound.is_alive() and self.ringing:
                pass  # Wait for sound to finish or stop flag
        print("Stopped ringing.")

