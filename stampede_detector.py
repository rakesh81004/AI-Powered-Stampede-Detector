import cv2
import smtplib
from email.message import EmailMessage
from ultralytics import YOLO
import threading
import time 

# --- CONFIGURATION ---
model = YOLO("yolov8n.pt")
WEBCAM_INDEX = 0

# --- STAMPEDE ALERT CONFIGURATION ---
REGION_NAME = "Region 234"
ALERT_THRESHOLD = 8 
PERSON_CLASS_ID = 0      # COCO class ID for 'person' (used for accurate counting)
ALERT_COLOR = (0, 0, 255) # Red for alert box/text

# --- EMAIL CONFIGURATION (YOUR DETAILS) ---
SENDER_EMAIL = "sureshsuresh95176@gmail.com"
APP_PASSWORD = "vzujsvzlkatytgwe" 
RECIPIENT_POLICE = "rakesh8102004@gmail.com"
RECIPIENT_CONTROL = "yogiagash510@gmail.com"
# --------------------------------------------------------

# *** NEW LIFETIME ALERT FLAG ***
# This flag is set to True once the first alert is successfully sent.
# It ensures only ONE email is ever sent per program execution.
alert_sent_lifetime = False 
# -------------------------------

def format_alert_message(recipient_id, count):
    """Generates the rich, bold HTML content for the alert email."""
    
    html_content = f"""\
    <html>
        <body>
            <p><strong>🚨 IMMEDIATE ACTION REQUIRED 🚨</strong></p>
            <p>Dear {recipient_id} Team,</p>
            <p>Our Stampede Detection System has identified a critical situation.</p>
            <p><strong>⚠️ HIGH CROWD DENSITY ALERT ⚠️</strong></p>
            <ul>
                <li><strong>Area:</strong> {REGION_NAME}</li>
                <li><strong>Current Person Count:</strong> {count} people (Exceeds Threshold of {ALERT_THRESHOLD})</li>
                <li><strong>Status:</strong> Severe Density Alert. Potential Stampede Risk.</li>
            </ul>
            <p>Please dispatch personnel immediately for crowd management.</p>
            <p>Thank you for your prompt response.</p>
            <p>-- Automated Security System</p>
        </body>
    </html>
    """
    return html_content

def send_alert_email(recipient, recipient_id, count):
    """Sends an email notification to a specific recipient and sets the lifetime flag."""
    global alert_sent_lifetime
    
    try:
        msg = EmailMessage()
        msg['Subject'] = f"CRITICAL STAMPEDE ALERT - {REGION_NAME}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        
        msg.set_content(f"ALERT: Count {count} in {REGION_NAME} exceeds threshold!")
        msg.add_alternative(format_alert_message(recipient_id, count), subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        
        # *** PERMANENTLY SET THE FLAG ON SUCCESS ***
        alert_sent_lifetime = True 

        print(f"\n✅ EMAIL SENT (Threaded): To {recipient_id} ({recipient}) about HIGH STAMPEDE ALERT in the REGION of {REGION_NAME}.")

    except Exception as e:
        print(f"\n❌ ERROR (Threaded): Failed to send email alert to {recipient_id}. Error: {e}")

def run_stampede_detector():
    """Initializes and runs the YOLOv8 stampede detection loop with single-shot alerts."""
    global alert_sent_lifetime

    cap = cv2.VideoCapture(WEBCAM_INDEX)
    if not cap.isOpened():
        print(f"Error: Could not open webcam at index {WEBCAM_INDEX}. Check if another application is using it.")
        return

    print("Stampede Detector running. Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame from webcam.")
            break

        results = model(frame, verbose=False) 
        detected_boxes = results[0].boxes if results and results[0] else []
        
        # --- COUNT FILTERING: Count ONLY people (class=0) ---
        person_count = 0
        for r in detected_boxes:
            class_id = int(r.cls[0].cpu().numpy())
            if class_id == PERSON_CLASS_ID:
                person_count += 1
        # ----------------------------------------------------

        
        # --- SINGLE-SHOT ALERT MECHANISM ---
        # 1. Check if the threshold is met
        # 2. Check if the alert has NOT been sent yet in this program execution
        if person_count > ALERT_THRESHOLD and not alert_sent_lifetime:
            
            # Send alert via threads. The function will set alert_sent_lifetime = True upon success.
            thread_police = threading.Thread(
                target=send_alert_email, 
                args=(RECIPIENT_POLICE, "Police Station E2", person_count)
            )
            thread_control = threading.Thread(
                target=send_alert_email, 
                args=(RECIPIENT_CONTROL, "Central Control Room", person_count)
            )
            
            thread_police.start()
            thread_control.start()
        
        # Determine current display status: High Alert is active if (count > threshold) AND (the alert was sent)
        is_alerting = person_count > ALERT_THRESHOLD and alert_sent_lifetime
        
        current_alert_state = "!! 🚨 STAMPEDE RISK 🚨 !!" if is_alerting else "Normal Density"
        count_color = ALERT_COLOR if is_alerting else (0, 255, 0)
        # -----------------------------
        

        # --- Display ---
        # Line 1: Project Name and Region
        cv2.putText(frame, f"STAMPEDE DETECTOR - {REGION_NAME}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Line 2: Alert Status
        cv2.putText(frame, f"Status: {current_alert_state}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, count_color, 2)
                    
        # Line 3: Object Count (ONLY PEOPLE COUNT IS DISPLAYED HERE)
        cv2.putText(frame, f"People Count: {person_count}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, count_color, 2)
        # ----------------------------------------

        # Loop through ALL detected objects for drawing boxes
        for r in detected_boxes:
            x1, y1, x2, y2 = r.xyxy[0].cpu().numpy()
            class_id = int(r.cls[0].cpu().numpy())
            label = model.names[class_id]
            
            # Box color depends on the alert status
            box_color = ALERT_COLOR if is_alerting else (255, 0, 0) 

            # Draw the bounding box and label
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), box_color, 2)
            cv2.putText(frame, label, (int(x1), int(y1)-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2)

        cv2.imshow("Stampede Detection System", frame)

        # Termination Mechanism: Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # --- Cleanup ---
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_stampede_detector()