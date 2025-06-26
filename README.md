# Squash Hawkeye 🎾

**AI-Powered Line-Calling System for Squash**

> **Academic Research Project** | University of East Anglia | Ubiquitous Computing Module

## 🚀 Project Impact
**Problem**: Amateur squash lacks affordable line-calling technology, while professional systems cost $60,000-$100,000 per court, leading to disputed calls that can dramatically shift match momentum.
**Solution**: Synchronized audio-visual detection system using accessible hardware (smartphone + laptop) that achieves **82% accuracy** in challenging edge cases for service line violations.

**📹 [Watch Technical Demo](https://youtu.be/d4KaSRGI-6w)** - 10-minute presentation covering architecture and results

## 🎯 Key Results
- **82% accuracy** in edge case line-calling scenarios (ball on/near service line)
- **Millisecond-precision** audio impact detection with adaptive thresholding
- **Dual-sensor validation** combining computer vision and audio processing
- **Cost-effective solution** using smartphone + laptop vs. $60K professional systems
- **Proof-of-concept** demonstrating feasibility for amateur squash officiating

## 🛠️ Technical Architecture
**Multi-Modal Sensing Pipeline**
- **Computer Vision**: OpenCV-based ball detection using HoughCircles transform
- **Audio Processing**: Java-based impact detection with dynamic amplitude thresholding  
- **Image Enhancement**: Brightness/contrast optimization for improved ball visibility
- **Spatial Analysis**: Precise ball-to-line distance calculation with official rules implementation
- **Synchronized Processing**: Audio timestamp correlation with video frame analysis

**Original Hardware Target**: Raspberry Pi 3 + Camera + Dual microphones (pivoted to offline processing due to performance constraints)

## 🔧 Core Technologies
- **Python + OpenCV**: Ball detection, line identification, spatial relationship analysis
- **Java Audio Processing**: Impact detection, timestamp extraction, adaptive filtering
- **Computer Vision Algorithms**: HoughCircles, Canny edge detection, HoughLinesP
- **Image Processing**: PIL enhancement, grayscale conversion, noise reduction
- **Multi-format Output**: Visual annotations, audio feedback, CSV logging

## 🎮 System Features
- **Real-time Audio Analysis**: 70% amplitude threshold with 200ms minimum gap filtering
- **Visual Ball Tracking**: 5-7 pixel radius detection optimized for squash ball characteristics  
- **Official Rules Implementation**: "Ball on line = OUT" with 1-pixel tolerance
- **Multi-output Feedback**: Annotated screenshots, spoken calls ("good serve"/"bad serve"), CSV logs
- **Edge Case Handling**: "NO BALL" fallback for poor visibility conditions

## 🚀 Quick Start
```bash
# Clone repository
git clone https://github.com/yourusername/squash-hawkeye.git
cd squash-hawkeye

# Install Python dependencies  
pip install opencv-python pillow numpy

# Install Java dependencies (for audio processing)
# Ensure Java 11+ is installed

# Process a test video
python cv_ball_detection.py test_video.mp4
java -cp . SquashHawkeye test_video.mp4
```

**Input Requirements**: 
- Video: 1080p @ 60fps (smartphone recording recommended)
- Audio: Embedded in video file
- Setup: Fixed camera position with clear service line view

## 📊 Performance Analysis
### Detection Accuracy
- **Edge Cases**: 82% accuracy on challenging ball-on-line scenarios
- **Clear Cases**: Near 100% accuracy for obvious IN/OUT calls
- **Audio Precision**: Millisecond-level impact timestamp detection
- **Visual Detection**: Robust performance under varied lighting conditions

### Technical Challenges Overcome
- **Hardware Limitations**: Raspberry Pi performance constraints led to strategic pivot
- **Multi-modal Synchronization**: Precise audio-visual timestamp correlation
- **Real-world Variability**: Adaptive thresholding for different court acoustics
- **Detection Robustness**: False positive prevention through multi-criteria validation

## 🏗️ System Pipeline

```
Audio Track → Impact Detection → Timestamp Extraction
     ↓
Video Frames → Computer Vision → Ball/Line Detection
     ↓
Spatial Analysis → Rule Implementation → IN/OUT Decision
     ↓
Multi-format Output → Visual + Audio + Logging
```

## 🎓 Academic Context

**Research Contribution**: Novel approach to affordable sports officiating through multi-modal sensing
**Collaboration**: Joint development with Jamie Green (50/50 contribution split)  
**Domain Impact**: Bridges gap between professional and amateur squash technology
**Technical Innovation**: Synchronized audio-visual processing for objective sports decisions

## 🔬 Technical Innovation

- **Adaptive Audio Processing**: Dynamic thresholding based on recording amplitude
- **Multi-criteria Ball Detection**: Combined geometric and spatial validation
- **Real-time Rule Implementation**: Direct translation of official squash regulations to code
- **Robust Edge Case Handling**: Specific focus on challenging boundary decisions

## 🏆 Skills Demonstrated

**Computer Vision**: OpenCV mastery, object detection, geometric analysis, image enhancement
**Audio Processing**: Digital signal processing, peak detection, noise filtering, multi-language integration
**Problem Solving**: Hardware constraint adaptation, real-world performance optimization
**Sports Technology**: Domain expertise application, official rules implementation
