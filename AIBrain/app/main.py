import cv2
import numpy as np
import time
import heartpy as hp
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from collections import deque

MEASUREMENT_DURATION = 30.0      

SAMPLE_RATE = 30.0               

MIN_GOOD_PEAKS = 15              

MIN_SIGNAL_STD = 5.0             

INSTRUCTIONS = """
HEART RATE MEASUREMENT INSTRUCTIONS
1. Turn ON your phone's FLASH (very important!)
2. Place your fingertip GENTLY but FULLY over the camera lens
Cover the entire lens, no light should leak around finger
3. Apply LIGHT to MODERATE pressure not too hard, not too loose
4. Keep your hand and finger COMPLETELY STILL
5. Do NOT move, talk, or press harder during measurement
6. Stay relaxed and breathe normally
7. Measurement will take exactly 30 seconds
"""

print(INSTRUCTIONS)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot open camera")
    print("Tip: If using phone camera, use DroidCam / IP Webcam and update the URL")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

green_buffer = deque(maxlen=int(MEASUREMENT_DURATION * SAMPLE_RATE * 1.5))
timestamps = deque(maxlen=len(green_buffer))

start_time = time.time()
frame_count = 0

print("\nStarting measurement in 3 seconds... Get ready!")
time.sleep(3)

print("Measuring... Keep finger still!")

plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
line_raw, = ax1.plot([], [], 'b-', label='Raw Green Signal')
line_filt, = ax2.plot([], [], 'r-', label='Filtered Signal')
ax1.set_title('Raw PPG Signal (Green Channel)')
ax2.set_title('Filtered PPG Signal')
ax1.set_ylabel('Intensity')
ax2.set_ylabel('Intensity')
ax2.set_xlabel('Time (s)')
ax1.legend()
ax2.legend()
plt.tight_layout()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame")
        break

    current_time = time.time() - start_time

    if current_time >= MEASUREMENT_DURATION:
        break

    frame_count += 1

    h, w = frame.shape[:2]
    roi = frame[int(h*0.35):int(h*0.65), int(w*0.35):int(w*0.65)]

    green_mean = np.mean(roi[:, :, 1])  

    green_buffer.append(green_mean)
    timestamps.append(current_time)

    cv2.rectangle(frame, (int(w*0.35), int(h*0.35)), (int(w*0.65), int(h*0.65)), (0, 255, 0), 2)
    cv2.putText(frame, f"Time: {current_time:.1f}s / {MEASUREMENT_DURATION}s", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow("Finger on Camera", frame)

    if frame_count % (SAMPLE_RATE * 2) == 0 and len(green_buffer) > 60:
        times_np = np.array(timestamps) - timestamps[0]
        signal_np = np.array(green_buffer)

        signal_norm = (signal_np - np.mean(signal_np)) / (np.std(signal_np) + 1e-8)

        try:
            wd, m = hp.process(signal_norm, sample_rate=SAMPLE_RATE, highpass=True, lowpass=True)
            filtered = wd['filtered']
        except:
            filtered = signal_norm  

        ax1.clear()
        ax1.plot(times_np, signal_norm, 'b-', label='Raw Green')
        ax1.legend()
        ax1.set_title('Raw PPG Signal (Green Channel)')

        ax2.clear()
        ax2.plot(times_np, filtered, 'r-', label='Filtered')
        ax2.legend()
        ax2.set_title('Filtered PPG Signal')

        plt.draw()
        plt.pause(0.01)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Measurement cancelled by user")
        break

cap.release()
cv2.destroyAllWindows()

print("\nProcessing final signal...")

if len(green_buffer) < 60:
    print("Error: Not enough data collected")
else:
    signal = np.array(green_buffer)
    times_np = np.array(timestamps)

    signal_norm = (signal - np.mean(signal)) / (np.std(signal) + 1e-8)

    try:
        working_data, measures = hp.process(
            signal_norm,
            sample_rate=SAMPLE_RATE,
            highpass=True,
            lowpass=True,
            highpass_order=2,
            lowpass_order=2,
            breathing_method=None
        )

        bpm = measures['bpm']
        peaks = working_data['peaklist']
        peak_count = len(peaks)

        signal_std = np.std(signal_norm)
        quality_ok = (peak_count >= MIN_GOOD_PEAKS) and (signal_std >= MIN_SIGNAL_STD)

        print("\n" + "="*50)
        print("FINAL RESULT")
        print("="*50)

        if quality_ok:
            print(f"Estimated Heart Rate: {bpm:.1f} BPM")
            print(f"Number of detected beats: {peak_count}")
            print(f"Signal quality: GOOD")
            print(f"Measurement duration: {times_np[-1]:.1f} seconds")
        else:
            print("Signal quality: POOR")
            print("Please try again with:")
            print(" - Better finger contact (full coverage)")
            print(" - Steady pressure and no movement")
            print(" - Flash turned ON")
            print(f"(Detected {peak_count} beats | Signal variation: {signal_std:.1f})")

        if 'rmssd' in measures:
            print(f"RMSSD (HRV): {measures['rmssd']:.1f} ms")

    except Exception as e:
        print("Error processing signal:", str(e))
        print("Try again with steadier finger placement.")

print("\nMeasurement complete.")