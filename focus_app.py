import streamlit as st
import cv2
import numpy as np
import time
import os

# Streamlit Page Configuration
st.set_page_config(page_title="Deep Work Focus App", layout="wide")

# Default values
session_time = 25 * 60  # 25 minutes
break_time = 5 * 60  # 5 minutes
distraction_count = 0
xp = 0
focus_score = 100
distraction_timer = 0  # Track distraction time

# Function to start camera tracking
def track_focus():
    global distraction_count, xp, focus_score, distraction_timer
    cap = cv2.VideoCapture(0)  # Open webcam

    if not cap.isOpened():
        st.error("❌ Camera not accessible! Please check permissions.")
        return
    
    placeholder = st.empty()  # Placeholder for messages
    cam_placeholder = st.image([])  # Placeholder for camera preview

    start_time = time.time()
    session_active = True
    distraction_start = None  # Track when distraction starts

    while session_active:
        ret, frame = cap.read()
        if not ret:
            st.error("❌ Failed to capture video!")
            break

        # Resize and convert to RGB for Streamlit display
        small_frame = cv2.resize(frame, (200, 150))  # Smaller preview
        small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        cam_placeholder.image(small_frame, caption="Your Focus Cam", use_column_width=False)

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        detected_faces = faces.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(detected_faces) == 0:  # No face detected = Distraction
            if distraction_start is None:
                distraction_start = time.time()  # Mark when distraction started

            distraction_count += 1
            focus_score -= 2  # Reduce focus score

            elapsed_distraction = time.time() - distraction_start

            if elapsed_distraction >= 5:  # If distracted for more than 5 seconds
                placeholder.error("🚨 **You've been distracted for too long! Refocus now!** 🚨")
            else:
                placeholder.warning("⚠️ You got distracted! Get back to work!")

            os.system("echo \a")  # System beep as alert
            time.sleep(2)  # Wait before re-checking
        else:
            placeholder.success("✅ You are focused! Keep going!")
            distraction_start = None  # Reset distraction timer

        elapsed_time = time.time() - start_time
        if elapsed_time >= session_time:
            session_active = False

    cap.release()
    placeholder.success("🎉 Session Complete! Take a Break!")
    return distraction_count, focus_score

# UI Layout
st.title("🎯 Foreal Focus Xone")
st.markdown("**Stay focused with AI-powered distraction detection!**")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Pomodoro Timer")
    work_time = st.slider("Set Work Session Duration (minutes)", 5, 60, 25)
    session_time = work_time * 60

    if st.button("Start Focus Session", use_container_width=True):
        distraction_count, focus_score = track_focus()

with col2:
    st.subheader("📊 Focus Analytics")
    st.metric(label="📌 Distraction Count", value=distraction_count)
    st.metric(label="⚡ Focus Score", value=focus_score)
    st.metric(label="🎖 XP Earned", value=focus_score // 10)  # XP based on focus

st.info("🔹 Keep your face visible to avoid distractions being counted!")
