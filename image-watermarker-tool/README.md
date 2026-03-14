# Day 85 - Image Watermarker

Desktop GUI application built with **Python + Tkinter + Pillow** that allows you to automatically add a **text** or **logo** watermark to your photos.

Perfect for batch-preparing images for social media (Instagram, etc.) with your branding.

## Features

- Upload main image (JPG, PNG, etc.)
- Two watermark modes:
  - **Text**: custom message, font size, color picker, opacity, 5 positions
  - **Logo**: upload PNG/JPG logo, scale %, opacity, 5 positions
- Real-time preview of the watermarked result
- Save as PNG (preserves transparency) or JPG
- Clean, modern interface with grid layout

## Technologies

- **Tkinter** – GUI framework
- **Pillow (PIL)** – image processing (watermarking, resizing, alpha blending)
- Python 3.x

## Requirements

```bash
pip install Pillow