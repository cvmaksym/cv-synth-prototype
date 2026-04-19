# Gesture-Controlled MIDI Synth & Waveform Shaper

A functional prototype of a touchless MIDI synthesizer powered by Computer Vision. This project allows users to interact with a digital synthesizer in 3-dimensional space, using hand gestures to trigger notes and manipulate sound parameters in real-time.

## 📺 Project Demo
Watch the system in action (includes audio):

https://github.com/user-attachments/assets/595ef16c-22d1-462e-8472-c7c881824357

> [!NOTE]
> If the video player above does not load, you can [download the demo file directly here](https://github.com/cvmaksym/cv-synth-prototype/raw/main/demo.mp4).

## 🌟 Key Features

* **Real-time Waveform Shaping:** The core innovation — an algorithm that analyzes hand contours to dynamically change the oscillator's shape (Sine, Saw, Triangle) on the fly.
* **Touchless Parameter Control:** Full control over ADSR envelope (Attack, Decay, Sustain, Release), Pitch, and Legato by tracking hand coordinates.
* **Gesture-Based UI:** A custom-built interface featuring "hover-and-hold" mechanics, allowing for full system navigation without physical contact.
* **High Performance:** Optimized Python pipeline to ensure low-latency interaction between video processing and MIDI output.

## 🛠 Tech Stack

* **Language:** Python
* **Computer Vision:** OpenCV, NumPy (Contour detection, Bounding box analysis)
* **Audio/MIDI:** MIDI protocol integration (Mido)
* **Architecture:** Modular design with separate processors for hand tracking, GUI rendering, and audio synthesis.

## ⚙️ Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
