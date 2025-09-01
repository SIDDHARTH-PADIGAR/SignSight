# ISL Trainer: Real-Time Sign Language Learning Tool

## Why

Millions of children and adults with hearing or speech impairments lack access to effective sign language education. Most available tools are either too generic, not interactive, or lack the kind of real-time feedback that encourages consistent learning and improvement. We aim to solve that gap with a personalized, responsive training module for American Sign Language (ASL).

## What

**ISL Trainer** is a desktop application that uses a machine learning model to predict hand gestures in real-time and provide instant feedback. Users are shown a target letter, perform the corresponding sign, and the system validates it live using the camera feed. It is designed to feel like a real tutor — slow-paced, supportive, and built for learning, not just testing.

Key Features:

* Real-time gesture recognition using camera input
* Simple, intuitive interface for children and first-time learners
* Score tracking, attempt counting, and performance logging
* SQLite database integration for local session tracking
* Built-in trainer flow that respects pacing and avoids frustration

---

## How It Works — System Flow

<img width="1122" height="960" alt="_- visual selection (1)" src="https://github.com/user-attachments/assets/5b82435b-db89-4bb0-8e7f-cbede0d33a3f" />

1. **User Launches the App**

   * The desktop GUI opens using a custom-styled **Tkinter** interface.
   * A random target letter from the ASL alphabet is displayed on screen.
   * Fonts are customized using a `.ttf` to ensure a modern, child-friendly feel.

2. **Camera Feed Initialization**

   * **OpenCV** initializes the webcam and continuously captures real-time video frames.
   * Each frame is processed to extract the region of interest (typically the user’s hand).

3. **Frame Preprocessing**

   * Captured frames are cropped, resized, and normalized as per model input requirements.
   * Background noise is minimized using basic preprocessing (e.g., grayscale, thresholding if needed).

4. **Prediction**

   * The cleaned frame is passed into a pre-trained **TensorFlow/Keras ML model**.
   * The model outputs a prediction: the most likely ASL letter the user is showing.

5. **Matching & Feedback**

   * The prediction is compared with the target letter.
   * If correct:

     * A "Correct" prompt is shown.
     * **Score and attempt count** are updated in the UI and database.
     * The next letter is queued after a short delay.
   * If incorrect:

     * The system waits for a few more predictions before prompting retry.
     * Only attempt count is incremented, not score.

6. **Data Logging**

   * All interaction metadata (target, prediction, correctness, timestamp) is logged locally using **SQLite**.
   * Enables session tracking and performance analysis over time.

7. **Loop Continues**

   * The process repeats until all target letters in a session are completed or the user exits.
   * The UI remains responsive and non-intrusive to support flow-based learning.

## Who

This project is primarily aimed at:

* Children and early learners new to sign language
* Schools and institutions catering to special needs education
* NGOs and training centers focusing on accessible communication
* Parents or caregivers who want to support consistent learning at home

The trainer is designed with inclusivity and approachability in mind. It is offline-first, lightweight, and respectful of the learner’s pace.
