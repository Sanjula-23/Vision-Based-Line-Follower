# 🚀 Vision-Based Line Follower  

## 📌 Project Overview  
This project implements a **line-following algorithm using a webcam** and **OpenCV**. It detects a path, analyzes the centroid, and determines turn directions for robotic navigation.  

## 🛠️ Features  
✅ **Real-time Line Detection** using contours  
✅ **Turn Detection** (LEFT, RIGHT, FORWARD)  
✅ **Otsu’s Thresholding & Morphological Operations** for noise reduction  
✅ **Grid Overlay for Better Visualization**  

## 📂 File Structure  
📂 Vision-Based-Line-Follower
│── Vision Test.py (Main Python script for line following)
│── requirements.txt (Dependencies list)
│── README.md (Project documentation)


## 🚀 How to Run  
1️⃣ Install dependencies:  
```bash
pip install -r requirements.txt

2️⃣ Run the script:

bash
python Vision Test.py

🔍 How It Works
Captures live feed from a webcam
Processes the ROI (Region of Interest) for speed optimization
Applies thresholding & filtering to detect the line
Determines direction (LEFT, RIGHT, FORWARD) based on centroid position
Handles 90-degree turns and intersections
