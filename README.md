# 📑 KYC Form Digitizer — LayoutLMv3 Deep Learning

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://badges.aleen42.whalemining.com/composite/docker.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is a high-performance **AI Development** solution for automated data extraction from **KYC (Know Your Customer)** forms. It leverages state-of-the-art Deep Learning to transform unstructured document images into validated, structured data.

---

## 🧠 Model R&D & Methodology

The core engine is a **Fine-Tuned LayoutLMv3** architecture, specifically optimized for complex document understanding.

### 🛠️ Training Logic & IA Pipeline
* **Supervised Learning**: Fine-tuned on a proprietary dataset of **200 manually annotated forms**.
* **Multi-modal Input**: The model processes **Text (OCR)**, **Visual Features (RGB)**, and **Spatial Layout (Bounding Boxes)** simultaneously.
* **Spatial Normalization**: All coordinates are mapped to a $1000 \times 1000$ grid to ensure consistent spatial awareness during inference.
* **BIO Tagging Schema**: Implements the **BIO (Begin, Inside, Outside)** convention to classify tokens into three distinct entities: `HEADER`, `QUESTION`, and `ANSWER`.
* **Scientific Evaluation**: Model performance was validated using a **Confusion Matrix** on a dedicated test set (Parquet format), ensuring high reliability for industrial use.



---

## 🌟 Key Features

### 🧪 Ready-to-Test Dataset
The repository includes an **`images/`** directory containing **148 test samples** (from `form_0.png` to `form_147.png`).
* **Quick Demo**: Load these samples directly into the UI to observe extraction accuracy.
* **Compatibility**: Supports any digital form containing **non-handwritten (typed) text**.

### 🖥️ Professional Dashboard
* **Spatial Reconstruction**: Custom algorithm to logically pair "Question" labels with their corresponding "Answer" fields.
* **Human-in-the-Loop**: A responsive **Shiny for Python** interface allows users to verify and edit AI predictions in real-time.
* **Interactive UX**: High-resolution image exploration powered by `Panzoom.js` for precise visual auditing.

---

## 🚀 Quick Start (Docker)

The application is fully containerized to ensure seamless deployment, managing all system dependencies like Tesseract OCR and OpenCV.

### 1. Build the Image
```bash
docker build -t kyc-app .
2. Run with Model Volume
Since the model weights are heavy, they are mounted as a volume for optimal performance.

Linux / WSL / macOS:

Bash
docker run -p 8050:8050 -v $(pwd)/Model_with_nms_kyc:/app/Model_with_nms_kyc kyc-app
Windows (PowerShell):

Bash
docker run -p 8050:8050 -v "${PWD}/Model_with_nms_kyc:/app/Model_with_nms_kyc" kyc-app
Access the UI at: http://localhost:8050

🛠️ Technical Stack
AI Engine: PyTorch, Hugging Face Transformers, LayoutLMv3.

Data Science: Scikit-learn, Numpy, Seaborn, Pandas.

OCR: Tesseract OCR.

Web & Deployment: Shiny for Python, Docker, Debian Slim.

✉️ Contact & Developer Info
This system was developed as part of a specialized AI & Data Science R&D effort.

Developer: Mahmoud Tourki

Email: mahmud.tourki24@gmail.com

LinkedIn: MAHMOUD TOURKI