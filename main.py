import os
import datetime
import subprocess
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import util


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main_window = util.get_button(self.main_window, 'login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=300)

        self.register_new_user_button_main_window = util.get_button(self.main_window, 'register', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = './log.txt'

    def add_webcam(self, label):
        if "cap" not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        if ret:
            # Flip the frame horizontally
            frame = cv2.flip(frame, 1)
        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def check_image_format(self, image_path):
        with Image.open(image_path) as img:
            print('PIL Image mode:', img.mode)
            print('PIL Image format:', img.format)
            if img.mode != 'RGB':
                img = img.convert('RGB')
                img.save(image_path)

    def login(self):
        unknown_img_path = './.tmp.jpg'
        db_dir_abs = os.path.abspath(self.db_dir)
        unknown_img_path_abs = os.path.abspath(unknown_img_path)

        # Save the current frame to an image file
        if self.most_recent_capture_arr is not None:
            # Convert to RGB (if it's not already)
            rgb_image = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)

            # Save the image in PNG format
            cv2.imwrite(unknown_img_path, cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR))

            # Check image format again
            self.check_image_format(unknown_img_path)
        else:
            util.msg_box('Error', 'No image captured. Please try again.')
            return

        try:
            # Run the face_recognition command
            output = subprocess.check_output(
                ['face_recognition', db_dir_abs, unknown_img_path_abs],
                stderr=subprocess.STDOUT
            )
            output = output.decode('utf-8')  # Ensure output is a string
            print(f'Face recognition output: {output}')

            if output.strip() == '':
                util.msg_box('ops...', 'No face recognized. Please register a new user or try again.')
                return

            name = output.split(',')[1][:-5].strip()
            if name in ['unknown_person', 'no_persons_found']:
                util.msg_box('ops...', 'Unknown user. Please register a new user or try again.')
            else:
                util.msg_box('Welcome Back', f'Welcome back, {name}.')
                with open(self.log_path, 'a') as f:
                    f.write(f'{name},{datetime.datetime.now()}\n')

        except subprocess.CalledProcessError as e:
            util.msg_box('Error', f'Error running face_recognition: {e.output.decode()}')
            print(f'Error running face_recognition: {e.output.decode()}')
        except Exception as e:
            util.msg_box('Error', f'An unexpected error occurred: {e}')
            print(f'An unexpected error occurred: {e}')
        finally:
            # Always remove the temporary image
            if os.path.exists(unknown_img_path):
                os.remove(unknown_img_path)

        # Check if the image is RGB
        print('Image shape:', self.most_recent_capture_arr.shape)
        print('Image dtype:', self.most_recent_capture_arr.dtype)
        print('Is image RGB:',
              len(self.most_recent_capture_arr.shape) == 3 and self.most_recent_capture_arr.shape[2] == 3)

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green',
                                                                      self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again',
                                                                         'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=150)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window,
                                                                'Please enter the username:')
        self.text_label_register_new_user.place(x=750, y=70)

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def start(self):
        self.main_window.mainloop()

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c")

        if name.strip() == '':
            util.msg_box('Error', 'Username cannot be empty.')
            return

        cv2.imwrite(os.path.join(self.db_dir, f'{name}.jpg'), self.register_new_user_capture)

        util.msg_box('Success!', 'User successfully registered!')

        self.register_new_user_window.destroy()


if __name__ == "__main__":
    app = App()
    app.start()
