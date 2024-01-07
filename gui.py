import cv2
import numpy as np
from time import sleep
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

width_min = 80
height_min = 80
offset = 10
pos_line = 550
delay = 600
detec = []
car = 0  

def pega_centro(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy

def select_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
    if file_path:
        cap = cv2.VideoCapture(file_path)
        return cap
    else:
        return None

root = tk.Tk()
root.title("Deteksi Kendaraan")
root.geometry("1300x900")

# Label untuk memilih video
video_label = tk.Label(root, text="Silahkan Pilih Video:")
video_label.pack(pady=10)

# Fungsi untuk memulai pendeteksian
def start_detection():
    global car  #car sebagai variabel global

    selected_video = select_video()
    if selected_video:
        cap = selected_video
        subtraction = cv2.createBackgroundSubtractorMOG2()

        # kanvas untuk video
        canvas = tk.Canvas(root, width=1280, height=720)
        canvas.pack()

        while True:
            ret, frame1 = cap.read()
            if not ret:
                break

            time = float(1/delay)
            sleep(time)

            grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(grey, (3, 3), 5)

            img_sub = subtraction.apply(blur)
            dilat = cv2.dilate(img_sub, np.ones((5, 5)))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            expand = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)
            expand = cv2.morphologyEx(expand, cv2.MORPH_CLOSE, kernel)
            contour, h = cv2.findContours(expand, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            cv2.line(frame1, (25, pos_line), (1200, pos_line), (255, 127, 0), 3)
            for (i, c) in enumerate(contour):
                (x, y, w, h) = cv2.boundingRect(c)
                validate_outline = (w >= width_min) and (h >= height_min)
                if not validate_outline:
                    continue

                cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)

                center = pega_centro(x, y, w, h)
                detec.append(center)
                cv2.circle(frame1, center, 4, (0, 0, 255), -1)

                for (x, y) in detec:
                    if y < (pos_line+offset) and y > (pos_line-offset):
                        car += 1
                        cv2.line(frame1, (25, pos_line), (1200, pos_line), (0, 127, 255), 3)
                        detec.remove((x, y))
                        print("Kendaraan terhitung: "+str(car))
            if (0 <= car <= 10):
                cv2.putText(frame1, "Kendaraan Terhitung: "+str(car), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
            elif (11 <= car <= 20):
                cv2.putText(frame1, "Kendaraan Terhitung: "+str(car), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 5)
            elif (21 <= car <= 30):
                cv2.putText(frame1, "Kendaraan Terhitung: "+str(car), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
            elif (car >= 31):
                cv2.putText(frame1, "PARKIRAN FULL", (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

            frame_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            frame_tk = ImageTk.PhotoImage(Image.fromarray(frame_rgb))

            canvas.create_image(0, 0, anchor=tk.NW, image=frame_tk)
            canvas.image = frame_tk

            root.update()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        cap.release()

# Button untuk pilih video
start_button = tk.Button(root, text="Pilih Video", command=start_detection)
start_button.pack(pady=20)

root.mainloop()
