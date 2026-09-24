# 🚨 AI-Powered Stampede Detection & Alert System

An **AI-based real-time crowd density monitoring system** designed to detect and prevent potential stampedes using **computer vision**, **machine learning**, and **automated alerts**.  
The system continuously analyzes live CCTV feeds, identifies crowd surges, and notifies authorities instantly via email — enabling faster response and ensuring public safety.  

![Critical Density - Stampede Detection](Critical%20Density%20-%20Stampede%20Detection%20Screenshot%20.png)

![Normal Density - Stampede Detection](Nomal%20Density%20-%20Stampede%20Detection%20Screenshot%20.png)

---

## ⚙️ Tech Stack with Integrated Features

1. 🧠 **YOLOv8 (Ultralytics)**  
   - Performs **real-time object detection and crowd counting** with deep learning.  
   - Filters detections by the `person` class (COCO ID: 0) to maintain accuracy.  
   - Processes each CCTV feed independently for **region-specific crowd analysis**.

2. 🎥 **OpenCV (cv2)**  
   - Handles **video frame capture**, visualization, and live display of detections.  
   - Draws **bounding boxes, labels, and real-time person counts** on each frame.  
   - Displays **alert color changes** (🟥 Red for high risk, 🟩 Green for normal).  

3. 💻 **Python + Threading**  
   - Enables **parallel email alerts and frame processing** without latency.  
   - Implements **timed re-alert control** using global state to prevent spam.  
   - Ensures smooth frame streaming while executing background alert threads.  

4. 📧 **SMTP (smtplib)**  
   - Sends **automated HTML-based email alerts** to authorities (e.g., Police, Control Room).  
   - Uses **secure Gmail SMTP (SSL port 465)** with app-password authentication.  
   - Customizable recipients, subjects, and region-based threshold notifications.  

---

## 🧩 System Architecture

```text
Camera Feed → YOLOv8 Model → Person Detection → Count Evaluation
                 ↓                          ↓
           Threshold Check         Real-Time Visualization
                 ↓                          ↓
           Alert Trigger → Threaded Email Notification (SMTP)
