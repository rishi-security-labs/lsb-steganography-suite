# 🕵️‍♂️ LSB Steganography Suite v3.0

<p align="center">
  <b>A powerful, feature-rich Python suite for hiding text and files inside images using Least Significant Bit (LSB) steganography, fortified with AES-256-GCM encryption.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Termux%20%7C%20Linux%20%7C%20Windows-2ea44f?style=for-the-badge&logo=linux&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/Security-AES--256--GCM-red?style=for-the-badge" alt="AES-256">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-project-structure">Structure</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-license">License</a>
</p>

---

## 📖 Overview

**LSB Steganography Suite** is an advanced command-line tool designed to securely hide sensitive information within standard image files. Unlike basic steganography tools, this suite provides military-grade security by combining **zlib compression** with **AES-256-GCM authenticated encryption**, ensuring that not only is your data hidden, but it is also unreadable without the password.

The tool features an interactive, color-coded terminal interface and includes advanced features like **EXIF metadata spoofing**, automated **payload capacity calculation**, and **diff-map generation** to analyze image tampering. It is highly optimized for Termux, making it a perfect companion for mobile security researchers.

> ⚠️ **Disclaimer:** This tool is developed for educational purposes, CTF challenges, and authorized security research. The author is not responsible for any misuse or illegal activities conducted with this tool.

---

## ✨ Key Features

### 🔐 Advanced Encoding & Security
*   **AES-256-GCM Encryption:** Secure your payload with a password. Authenticated encryption ensures data integrity and confidentiality.
*   **Zlib Compression:** Automatically compresses data before embedding, allowing you to hide larger files in smaller images.
*   **Integrity Verification:** Implements MD5 checksums within the payload header to detect data corruption or tampering.
*   **Multi-bit per Channel:** Supports 1, 2, or 4 bits per channel (BPC). 1-BPC offers maximum invisibility, while higher BPC allows for larger payloads at the cost of slight image degradation.

### 🖼️ Core Operations
*   **Hide Text:** Embed plain text messages directly into images.
*   **Hide Files:** Embed any file type (PDF, ZIP, DOCX, etc.) along with its original filename into the carrier image.
*   **Smart Extraction:** Automatically detects whether the extracted payload is plain text or a file, and restores it to your Downloads directory.

### 🕵️‍♂️ Analysis & Anti-Forensics
*   **Chi-Square Analysis:** Runs an LSB ratio analysis to hint at whether an image contains hidden data (detects stego anomalies).
*   **Metadata Spoofing:** Clone EXIF data from a generic, innocent image to your stego image to evade basic forensic analysis.
*   **Diff Map Generator:** Visually compare the original and stego images to highlight exactly which pixels were changed.

---

## 📁 Project Folder Structure

```text
lsb-steganography-suite/
│
├── stego.py                 # Main executable script
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── LICENSE                  # MIT License
├── .gitignore               # Git ignore rules
│
├── samples/                 # (Optional) Sample images for testing
│   ├── cover.jpg
│   └── secret.txt
│
└── outputs/                 # Default output folder
```

---

## ⚙️ Installation

### 📱 Termux (Android)
```bash
# 1. Update packages and grant storage access
pkg update -y && pkg upgrade -y
termux-setup-storage

# 2. Install Python and required system libraries
pkg install python -y
pkg install libjpeg-turbo libpng -y

# 3. Clone repository and install dependencies
git clone https://github.com/rishi-security-labs/lsb-steganography-suite.git
cd lsb-steganography-suite
pip install -r requirements.txt
```

### 🐧 Linux / 🪟 Windows
```bash
# Clone repository
git clone https://github.com/rishi-security-labs/lsb-steganography-suite.git
cd lsb-steganography-suite

# Install dependencies (use pip3 on Linux if necessary)
pip install -r requirements.txt
```

---

## 🚀 Usage

Run the main script to open the interactive menu:

```bash
python stego.py
```

### 🛠️ Menu Options

1.  **Hide text in image:** Enter the carrier image path, type your secret message, choose whether to compress/encrypt, and save the new PNG.
2.  **Hide file in image:** Enter the carrier image, provide the path to the secret file, set a password, and the tool will embed the file.
3.  **Decode / extract:** Point the tool to a stego image, enter the password (if any), and it will automatically extract the text or file to your Downloads folder.
4.  **Analyze image (chi-square):** Scans an image for LSB anomalies to determine if it likely contains hidden data.
5.  **Clone metadata (EXIF spoof):** Copies EXIF data from a normal photo to your stego photo to make it look authentic.
6.  **Compare images (diff map):** Shows a side-by-side pixel difference analysis, saving a visual map of the changed pixels.

---

## 🔧 Configuration & Environment

This tool requires **no environment variables** or API keys. All configuration is interactive via CLI prompts.

*   **File Output:** All generated files (stego images, extracted files, diff maps) are automatically saved to the user's download directory:
    *   **Termux:** `/storage/emulated/0/Download`
    *   **Linux/Windows:** `~/Downloads` or the current working directory.

### `requirements.txt`
```txt
Pillow>=9.0.0
cryptography>=38.0.0
piexif>=1.1.3
```

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```text
MIT License

Copyright (c) 2025 Rishi Security Labs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Made with 🖤 by <a href="https://github.com/rishi-security-labs">Rishi Security Labs</a>
</p>
