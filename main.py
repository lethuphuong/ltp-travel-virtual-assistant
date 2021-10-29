"""
Put together
    - Define a list of questions and corresponding answers
    - Listen to the question and find the most suitable answer.
    If you can't find the answer, say "I don't know".
"""
import multiprocessing

import speech_recognition as sr
import pyttsx3
from thefuzz import fuzz
import cv2


def read_file(filename):
    with open(filename, mode='r', encoding='utf8') as fp:
        contents = fp.read()
        contents = contents.lower()
        return contents.splitlines()


def find_answer(ques, list_ques, list_answers):
    best_idx = 0
    best_score = -1
    for idx, ques_in_list in enumerate(list_ques):
        score = fuzz.ratio(ques.lower(), ques_in_list)
        if score > best_score:
            best_idx = idx
            best_score = score
    if best_score < 50:
        return "I don't know!"
    else:
        return list_answers[best_idx]


def say(text):
    global engine
    engine.say(text)
    engine.runAndWait()


is_running = False
engine = pyttsx3.init()


def reset():
    global is_running
    is_running = False
    print(is_running)


def communicate_with():
    global is_running
    global engine
    if is_running:
        return
    recognizer = sr.Recognizer()

    questions = read_file('data/question.txt')
    answers = read_file('data/answer.txt')

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            say("What information that you want to know?")
            print("Listening")
            audio = recognizer.listen(source, timeout=8)
            try:
                say("Just a moment!")
                question = recognizer.recognize_google(audio, language='en')
                print(question)
                answer = find_answer(question, questions, answers)
                say(answer)
                say("Do you want to continue? Please say YES or NO!")
                print("Listening")
                audio = recognizer.listen(source, timeout=8)
                question = recognizer.recognize_google(audio, language='en')
                print(question)
                if 'ye' not in question.lower():
                    say("Bye. Have a good time!")
                    is_running = False
                    break
            except sr.UnknownValueError:
                print("Don't know!!!")
            except sr.RequestError:
                print("Network Error!!!")
        reset()


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
    th = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=15, minSize=(100, 100))

        if (th is not None) and (not th.is_alive()):
            is_running = False

        if len(faces) > 0 and (not is_running):
            is_running = True
            th = multiprocessing.Process(target=communicate_with)
            th.start()

        for x, y, w, h in faces:
            cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0), thickness=2)
        cv2.imshow('frame', frame)
        key = cv2.waitKey(3)
        if (key & 0xFF) == ord('q'):
            if th is not None:
                th.terminate()
            break
    cv2.destroyAllWindows()
