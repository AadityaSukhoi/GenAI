# Face Generation using GAN (CelebA Dataset)

This project implements a **Generative Adversarial Network (GAN)** using PyTorch to generate human face images from random noise.

The model is trained on the **CelebA dataset** and learns to produce realistic face-like images through adversarial training.

---

## Overview

A GAN consists of two neural networks:

- **Generator (G)** → Creates fake images from noise  
- **Discriminator (D)** → Distinguishes real vs fake images  

Both networks compete, improving each other over time.

---

## Architecture

`Noise (z) → Generator → Fake Image → Discriminator → Real/Fake`

---

## Tech Stack

- **PyTorch**
- **Torchvision**
- **NumPy**
- **Matplotlib (optional for visualization)**
- **CUDA (GPU acceleration)**

---

## Dataset

- **CelebA (CelebFaces Attributes Dataset)**
- Contains over 200,000 celebrity face images

### Preprocessing:
- Resize to `64×64`
- Center crop
- Normalize to `[-1, 1]`

---

## Model Details

### Generator
- Input: Random noise vector (`z_dim = 100`)
- Fully connected layers
- Activation: ReLU + Tanh
- Output: `3 × 64 × 64` image

---

### Discriminator
- Input: Image (`64×64×3`)
- Fully connected layers
- Activation: LeakyReLU + Sigmoid
- Output: Probability (real/fake)

---

## Training Configuration

- **Loss Function**: Binary Cross Entropy (`BCELoss`)
- **Optimizer**: Adam
  - Learning Rate: `0.0002`
  - Betas: `(0.5, 0.999)`
- **Batch Size**: (set in notebook)
- **Device**: GPU (if available)

---

## Training Process

1. Sample random noise
2. Generate fake images
3. Train discriminator:
    - Real images → label 1
    - Fake images → label 0
4. Train generator:
    - Fool discriminator
5. Repeat for multiple epochs

--- 

## Output

- Generator learns to produce realistic human faces
- Output improves over epochs

---

## Features
- Custom dataset loader
- GPU acceleration support
- Modular Generator & Discriminator design
- End-to-end GAN pipeline

---

## Limitations
- Uses fully connected layers (not CNN-based)
- Image quality may be limited
- Training instability (common in GANs)

--- 

## Notes

- GAN training can be unstable — tuning is important
- GPU significantly improves training speed