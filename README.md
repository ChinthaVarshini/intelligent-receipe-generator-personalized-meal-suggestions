# 🍽️ Intelligent Recipe Generator — Personalized Meal Suggestions

> An AI-powered system that recognizes ingredients from images and text, then generates personalized recipe recommendations using Computer Vision, OCR, and Natural Language Processing.

---

## 📌 Project Overview

The **Intelligent Recipe Generator** is a multimodal AI application that eliminates the hassle of manual recipe searching. A user simply provides an image or text input containing ingredients, and the system automatically identifies them and suggests personalized recipes in seconds.

This project combines **Computer Vision (CNN)**, **Optical Character Recognition (OCR)**, and **Natural Language Processing (NLP)** to create a seamless end-to-end AI pipeline — turning unstructured visual/text data into structured, actionable recipe recommendations.

---

## 🎯 Key Results

| Metric | Result |
|--------|--------|
| Ingredient Recognition Accuracy | **~85%** |
| Reduction in Manual Search Time | **~60%** |
| Input Formats Supported | Images, Text, Mixed |
| Output | Personalized recipe suggestions in seconds |

---

## 🧠 How It Works

```
User Input (Image / Text)
        │
        ▼
┌─────────────────────┐
│  Image Processing   │  ← CNN-based visual feature extraction
│  (Computer Vision)  │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   OCR Extraction    │  ← Text extraction from images/labels
│   (Tesseract/CV)    │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  NLP Processing     │  ← Ingredient identification & normalization
│                     │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Recipe Matching &  │  ← Personalized recommendation engine
│  Generation Engine  │
└─────────────────────┘
        │
        ▼
  📋 Personalized Recipe Output
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.x |
| Computer Vision | OpenCV, CNN (Convolutional Neural Network) |
| OCR | Tesseract OCR / EasyOCR |
| NLP | NLTK / spaCy |
| Deep Learning | TensorFlow / Keras |
| Data Processing | Pandas, NumPy |
| Image Processing | Pillow (PIL) |

---

## ✨ Features

- 🖼️ **Image-based ingredient recognition** — upload a photo of your fridge or ingredients
- 📝 **Text-based input** — type ingredients manually
- 🔀 **Multimodal processing** — handles both image and text inputs simultaneously
- 🍳 **Personalized suggestions** — recipes tailored to available ingredients
- ⚡ **Fast processing** — results generated in seconds
- 📊 **High accuracy** — ~85% ingredient recognition accuracy using CNN + OCR

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.8+
pip
```

### Installation

```bash
# Clone the repository
git clone https://github.com/ChinthaVarshini/intelligent-receipe-generator-personalized-meal-suggestions.git

# Navigate to project directory
cd intelligent-receipe-generator-personalized-meal-suggestions

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

---

## 📁 Project Structure

```
intelligent-recipe-generator/
│
├── models/                  # Trained CNN models
├── data/                    # Dataset and training data
├── preprocessing/           # Image and text preprocessing scripts
├── ocr/                     # OCR extraction modules
├── nlp/                     # NLP processing pipeline
├── recommendation/          # Recipe matching engine
├── app.py                   # Main application entry point
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## 🔬 Model Architecture

The ingredient recognition system uses a **CNN-based architecture** trained on a custom dataset:

- **Input**: Raw images of ingredients / food items
- **Feature Extraction**: Convolutional layers for visual pattern recognition
- **OCR Pipeline**: Extracts text from packaged food labels and handwritten notes
- **NLP Layer**: Normalizes and identifies ingredient names from extracted text
- **Output**: Structured list of recognized ingredients → recipe recommendations

---

## 📊 Performance

- Trained and evaluated on a custom curated dataset
- Achieved **~85% accuracy** on ingredient recognition tasks
- Reduced manual recipe search time by approximately **60%**
- Handles multiple input formats with consistent performance

---

## 👩‍💻 Contributors

| Name | Role |
|------|------|
| **Varshini Chintha** | AI/ML Development — CNN model training, OCR integration, NLP pipeline |

---

## 🏆 Highlights

- ✅ Built as part of **Infosys Springboard AI/ML Internship (Nov 2025 – Jan 2026)**
- ✅ Real-world multimodal AI pipeline combining CV + OCR + NLP
- ✅ End-to-end solution from raw input to structured output
- ✅ Demonstrates practical application of deep learning for everyday problems

---

## 📄 License

This project is for educational and portfolio purposes.

---

## 📬 Contact

**Varshini Chintha**
- 📧 chinthavarshini4@gmail.com
- 💼 [LinkedIn](https://linkedin.com/in/varshini-chintha-108424314)
- 🐙 [GitHub](https://github.com/ChinthaVarshini)

---

*Built with ❤️ using Python, Computer Vision, OCR, and NLP*
