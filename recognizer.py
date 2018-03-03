import face_recognition
import cv2
import os
import sqlite3


class recognizer:

    def __init__(self):
        self.encodings = []
        self.videoCapture = None
        self.names = []
        self.conn = None
        self.filePath = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

    def createConnection(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

    def insertInDB(self, name, imagePath, cursor):
        query = cursor.execute(
            'SELECT Name from faces where Name = ?', (name, ))
        if not query.fetchall():
            cursor.execute(
                'INSERT INTO faces (Name, ImagePath) VALUES (?, ?)', (name, imagePath,))

    def loadImages(self):
        db_file = os.path.join(self.filePath, 'data.db')
        self.createConnection(db_file)
        db = self.conn.cursor()
        db.execute("CREATE TABLE IF NOT EXISTS faces(`Name`  TEXT, \
                                                     `id`    INTEGER DEFAULT 0 PRIMARY KEY AUTOINCREMENT, \
                                                     `ImagePath` TEXT)")
        imageDirectory = os.path.join(self.filePath, 'images')
        db.execute('SELECT * FROM faces')
        for person in db.fetchall():
            image = face_recognition.load_image_file(
                os.path.join(imageDirectory, person[2]))
            encoding = face_recognition.face_encodings(image)[0]
            self.encodings.append(encoding)
            # name = imageFile.split('.')[0].replace('_', ' ')
            self.names.append(person[0])
            # self.insertInDB(name, imageFile, db)

        print self.names
        self.conn.commit()
        self.conn.close()

    def startVideoCapture(self, devNum):
        try:
            self.videoCapture = cv2.VideoCapture(devNum)
        except:
            print "Error starting capture!"
            exit()

    def start(self, devNum):
        self.loadImages()
        self.startVideoCapture(devNum)

        while True:
            ret, frame = self.videoCapture.read()

            if frame is None:
                print "Failed to get frames!"
                exit()

            rgbFrame = frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(rgbFrame)
            face_encodings = face_recognition.face_encodings(
                rgbFrame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(
                    self.encodings, face_encoding)

                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.names[first_match_index]

                cv2.rectangle(frame, (left, top),
                              (right, bottom), (0, 0, 255), 2)

                cv2.rectangle(frame, (left, bottom - 35),
                              (right, bottom), (0, 0, 255), -1)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6),
                            font, 1.0, (255, 255, 255), 1)

            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.videoCapture.release()
        cv2.destroyAllWindows()


def main():
    obj = recognizer()
    obj.start(0)

if __name__ == "__main__":
    main()
