import face_recognition
import cv2
import getpass
import os
import pyttsx3
import datetime
from reportlab.pdfgen import canvas
import mediapipe as mp

# === Voice Output Engine ===
engine = pyttsx3.init()
def speak(text):
    print("🔊", text)
    engine.say(text)
    engine.runAndWait()

# === User Profile ===
USER = {
    "name": "Varshitha",
    "account": "ACC123456",
    "last_login": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

# === Speak Greeting ===
speak(f"Welcome {USER['name']} to Face ATM")

# === Blink Detection ===
def detect_blink():
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
    cap = cv2.VideoCapture(0)
    blink_count = 0
    speak("Please blink your eyes to verify you're real")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)

        if result.multi_face_landmarks:
            blink_count += 1
            if blink_count > 5:
                break

        cv2.putText(frame, "Blink 5 times to authenticate", (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.imshow("👁 Blink Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    speak("Blink detection successful")

# === Stranger Alert ===
def log_stranger(frame):
    if not os.path.exists("intruders"):
        os.makedirs("intruders")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"intruders/intruder_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    speak("🚨 Stranger alert! Unrecognized face captured.")

# === Face Authentication ===
def verify_face():
    if not os.path.exists("known_face.jpg"):
        speak("Face image not found. Please add 'known_face.jpg'")
        exit()

    known_image = face_recognition.load_image_file("known_face.jpg")
    known_encoding = face_recognition.face_encodings(known_image)[0]

    cap = cv2.VideoCapture(0)
    speak("Scanning your face. Please face the camera.")
    scanned = False
    start_time = datetime.datetime.now()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)

        for enc in encodings:
            match = face_recognition.compare_faces([known_encoding], enc)[0]
            if match:
                cap.release()
                cv2.destroyAllWindows()
                speak("Face verified successfully.")
                return True
            else:
                if not scanned:
                    log_stranger(frame)
                    scanned = True

        # Scan timeout after 10 seconds
        if (datetime.datetime.now() - start_time).seconds > 10:
            break

        cv2.putText(frame, "🔍 Scanning Face...", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imshow("🔒 Face Scan", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return False

# === Transaction Logger ===
def log_transaction(action, amount):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("transactions.txt", "a", encoding='utf-8') as f:
        f.write(f"[{now}] {action}: ₹{amount}\n")

# === Generate PDF ===
def generate_pdf():
    c = canvas.Canvas("bank_statement.pdf")
    c.setFont("Helvetica", 14)
    c.drawString(100, 800, "Bank Statement")
    c.drawString(100, 780, f"Name: {USER['name']}")
    c.drawString(100, 760, f"Account: {USER['account']}")

    if os.path.exists("transactions.txt"):
        with open("transactions.txt", "r", encoding='utf-8') as file:
            y = 740
            for line in file.readlines():
                c.drawString(100, y, line.strip())
                y -= 20
    else:
        c.drawString(100, 740, "No transactions yet.")
    c.save()
    speak("PDF bank statement saved.")

# === ATM Main Logic ===
balance = 5000

# Login
if verify_face():
    pin = getpass.getpass("Enter PIN: ")
    if pin != "1234":
        speak("Wrong PIN. Access Denied.")
        exit()
    else:
        speak("PIN Verified. Access Granted.")
else:
    speak("Face not recognized. Exiting.")
    exit()

# Show Profile
print("\n🧑 User Profile")
print(f"Name: {USER['name']}")
print(f"Account: {USER['account']}")
print(f"Last Login: {USER['last_login']}")
print()

# ATM Menu
while True:
    print("\n💳 ATM MENU")
    print("1. Check Balance")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Transaction History")
    print("5. PDF Bank Statement")
    print("6. Exit")
    choice = input("Enter your choice: ")

    if choice == "1":
        speak(f"Your balance is ₹{balance}")
    elif choice == "2":
        amount = int(input("Enter deposit amount: "))
        balance += amount
        log_transaction("Deposit", amount)
        speak(f"₹{amount} deposited.")
    elif choice == "3":
        speak("Re-authenticating face and blinking...")
        if verify_face():
            detect_blink()
            amount = int(input("Enter withdrawal amount: "))
            if amount <= balance:
                balance -= amount
                log_transaction("Withdraw", amount)
                speak(f"₹{amount} withdrawn successfully.")
            else:
                speak("Insufficient balance.")
        else:
            speak("Face not matched again.")
    elif choice == "4":
        if os.path.exists("transactions.txt"):
            with open("transactions.txt", "r", encoding='utf-8') as f:
                print("\n📄 Transaction History")
                print(f.read())
        else:
            speak("No transaction history found.")
    elif choice == "5":
        generate_pdf()
    elif choice == "6":
        speak("Thank you for using our ATM. Goodbye!")
        break
    else:
        speak("Invalid option. Please try again.")