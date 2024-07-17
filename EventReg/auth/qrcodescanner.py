import cv2
import pyzbar.pyzbar as pyzbar
from mysql.connector import connection
dict = {
  'user': 'root',
  'host': 'localhost',
  'database': 'flask'
}
conn = connection.MySQLConnection(**dict)

cap = cv2.VideoCapture(0)

uname = ""
while True:
    _, frame = cap.read()
    cv2.imshow("Frame", frame)

    decodedobject = pyzbar.decode(frame)
    for obj in decodedobject:
        uname = obj.data.decode("utf-8")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM event1 WHERE name = %s", (uname,))
        user = cursor.fetchone()

        if user:
            print("Pass is valid for event")
            print(user[1])
        else:
            print("Pass is invalid for event")
    key = cv2.waitKey(1)
    if key == 27:
        break
