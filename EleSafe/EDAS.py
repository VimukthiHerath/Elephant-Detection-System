import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
import numpy as np
import cv2
import firebase_admin
from firebase_admin import credentials, db
import time
import requests

# Initialize Firebase
cred = credentials.Certificate(r'Yourpathofthejsonfile\elephant-detection-821c5-firebase-adminsdk-ro5gr-e5cbf06dfc.json') #replace with your json file path
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://yourdataBAseURL'  # Replace with your database URL
})

# Load the pre-trained MobileNetV2 model
model = MobileNetV2(weights='imagenet')

# Telegram Bot Configuration
BOT_TOKEN = "your_bot_token"  # Replace with your Telegram bot token
CHAT_ID = "your_chat_id"      # Replace with your Telegram chat ID

def send_telegram_alert(message):
    """
    Sends a Telegram notification with the given message.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Telegram alert sent successfully")
    else:
        print(f"Failed to send alert: {response.status_code}, {response.text}")

def predict_elephant(frame):
    """
    Preprocesses the frame and predicts whether an elephant is detected.
    """
    img = cv2.resize(frame, (224, 224))
    img_array = np.expand_dims(img, axis=0)
    img_array = preprocess_input(img_array)
    
    predictions = model.predict(img_array)
    decoded_predictions = decode_predictions(predictions, top=3)[0]
    
    elephant_detected = False
    elephant_confidence = 0
    for (_, label, score) in decoded_predictions:
        if label in ['African_elephant', 'Indian_elephant']:
            elephant_detected = True
            elephant_confidence = score * 100
            break
    
    return elephant_detected, elephant_confidence

def update_firebase(elephant_detected, confidence):
    """
    Updates the Firebase database with the detection results.
    """
    ref = db.reference('elephant_detection')
    data = {
        'detected': elephant_detected,
        'confidence': confidence,
        'timestamp': time.time()  # Store the timestamp of the detection
    }
    ref.set(data)
    print("Firebase updated!")

# ESP32-CAM URL (replace with your ESP32-CAM IP address)

esp32_cam_url = 'http://111.111.1.1/capture'  # replace with your ESP32-CAM IP address

while True:
    try:
        # Get image from ESP32-CAM
        img_resp = requests.get(esp32_cam_url)
        img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        frame = cv2.imdecode(img_arr, -1)

        # Predict elephant in the frame
        elephant_detected, confidence = predict_elephant(frame)

        # Update Firebase and send Telegram alert if elephant is detected
        if elephant_detected:
            update_firebase(elephant_detected, confidence)

            # Send Telegram alert
            message = f"🚨 Elephant Alert! Detected with {confidence:.2f}% confidence."
            send_telegram_alert(message)

        # Display the frame with status
        text = f'Elephant detected! Confidence: {confidence:.2f}%' if elephant_detected else 'No elephant detected'
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if elephant_detected else (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow('Elephant Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"Error: {e}")
        break

cv2.destroyAllWindows()