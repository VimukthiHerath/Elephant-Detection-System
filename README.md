# Elephant Detection and Alert System

## Overview
This project implements a real-time elephant detection and alerting system using an ESP32-CAM, TensorFlow's MobileNetV2, Firebase, and Telegram for notifications. The system captures images via an ESP32-CAM, processes them using a pre-trained MobileNetV2 model to detect elephants, and sends alerts if an elephant is detected.

## Features
- **Real-Time Detection**: Uses an ESP32-CAM to capture images and a MobileNetV2 model for detection.
- **Firebase Integration**: Updates detection results in real-time to a Firebase Realtime Database.
- **Telegram Alerts**: Sends instant notifications to a configured Telegram chat when an elephant is detected.
- **Display Interface**: Shows the camera feed with detection status using OpenCV.

## Technologies Used
- **TensorFlow** and **Keras**: For loading and using the MobileNetV2 pre-trained model.
- **Firebase**: To store and update detection results.
- **ESP32-CAM**: For capturing live images.
- **OpenCV**: For image processing and display.
- **Telegram Bot API**: For sending real-time alerts.

## Project Structure
```
.
|-- main.py                 # Main script for running the detection system
|-- requirements.txt        # Python dependencies
|-- firebaseElephantdetection/
    |-- alicode/
        |-- elephant-detection-821c5-firebase-adminsdk.json  # Firebase credentials
```

## Setup Instructions

### Prerequisites
- Python 3.6 or higher
- ESP32-CAM with appropriate firmware
- Firebase project with a Realtime Database
- Telegram Bot API credentials

### Steps to Recreate the Project

#### 1. **Firebase Setup**
1. Create a Firebase project.
2. Set up a Realtime Database.
3. Download the service account key and place it in the `firebaseElephantdetection/alicode/` directory.
4. Note the database URL and update it in the `main.py` script.

#### 2. **Telegram Bot Setup**
1. Create a Telegram bot using BotFather and obtain the bot token.
2. Get the chat ID where alerts will be sent.
3. Update the bot token and chat ID in the `main.py` script.

#### 3. **ESP32-CAM Setup**
1. Flash the ESP32-CAM with the appropriate firmware to capture images.
2. Note the IP address of the ESP32-CAM.
3. Update the `esp32_cam_url` variable in the `main.py` script with the ESP32-CAM IP address.

#### 4. **Python Environment Setup**
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/elephant-detection.git
    cd elephant-detection
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

#### 5. **Running the Project**
1. Ensure the ESP32-CAM is connected and streaming images.
2. Run the main script:
    ```bash
    python main.py
    ```
3. The system will start capturing images, processing them, and sending alerts if an elephant is detected.

## Code Explanation

### 1. **Firebase Initialization**
```python
cred = credentials.Certificate('path/to/firebase-adminsdk.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-database-url.firebaseio.com'
})
```
Initializes the Firebase app with the provided credentials and database URL.

### 2. **Model Loading**
```python
model = MobileNetV2(weights='imagenet')
```
Loads the pre-trained MobileNetV2 model from TensorFlow.

### 3. **Telegram Alert Function**
```python
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    ...
```
Sends a notification to the configured Telegram chat.

### 4. **Elephant Prediction Function**
```python
def predict_elephant(frame):
    img = cv2.resize(frame, (224, 224))
    img_array = np.expand_dims(img, axis=0)
    img_array = preprocess_input(img_array)
    predictions = model.predict(img_array)
    decoded_predictions = decode_predictions(predictions, top=3)[0]
    ...
```
Processes the image frame and predicts whether an elephant is detected.

### 5. **Firebase Update Function**
```python
def update_firebase(elephant_detected, confidence):
    ref = db.reference('elephant_detection')
    data = {
        'detected': elephant_detected,
        'confidence': confidence,
        'timestamp': time.time()
    }
    ref.set(data)
    ...
```
Updates the Firebase Realtime Database with the detection results.

### 6. **Main Loop**
```python
while True:
    try:
        img_resp = requests.get(esp32_cam_url)
        img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        frame = cv2.imdecode(img_arr, -1)
        elephant_detected, confidence = predict_elephant(frame)
        if elephant_detected:
            update_firebase(elephant_detected, confidence)
            message = f"🚨 Elephant Alert! Detected with {confidence:.2f}% confidence."
            send_telegram_alert(message)
        ...
    except Exception as e:
        print(f"Error: {e}")
        break
```
Continuously captures images from the ESP32-CAM, processes them, and updates Firebase and Telegram based on the detection results.

## Future Enhancements
- Fine-tune the model for better accuracy.
- Add additional notification channels such as SMS or email.
- Integrate physical deterrents or alarms.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.

## Contact
For questions or feedback, please open an issue or contact the project owner.
