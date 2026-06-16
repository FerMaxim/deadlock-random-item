# Deadlock Build Generator & Multiplayer Randomizer

A full-stack web application that uses Machine Learning (XGBoost) to predict and generate optimized 24-slot item builds and 36-point skill progressions for all 38 characters in the game Deadlock. Includes a real-time multiplayer WebSocket system for generating builds with friends in shared lobbies.

## 🚀 Architecture

* **Backend:** Django 4.2 + Daphne (ASGI)
* **Real-time Engine:** Django Channels + Redis (WebSocket synchronization)
* **Machine Learning:** XGBoost (Autoregressive predictive modeling)
* **Frontend:** Vanilla JavaScript + Vanilla CSS (Glassmorphism UI)
* **Containerization:** Docker + Docker Compose

---

## 📂 Project Structure

* **`website/`** - The main Django web application. Contains frontend templates, static assets, and WebSocket routing.
* **`main/simulator/`** - The core ML generation engine (`generate_build.py`).
* **`main/data/dictionary/`** - JSON configuration files for heroes, items, and abilities (parsed from Deadlock API).
* **`main/ml/models/`** - **[NOT IN GIT]** Contains the 2.2 GB of compiled XGBoost JSON models required for the simulator. You must supply these models manually!

---

## ⚠️ Important Note Regarding ML Models

Because GitHub has a strict file size limit and the XGBoost models weigh over **2.2 GB**, the `main/ml/models/` directory is intentionally ignored in Git (`.gitignore`).

To run this application, you **must** manually place the generated `xgb_items_hero_*.json` and `xgb_abilities_hero_*.json` files into the `main/ml/models/` folder. Without them, the build generator will crash.

---

## 💻 Local Development Setup (Without Docker)

1. Ensure you have Python 3.10+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run Django's development server (Redis is not strictly required for local testing, it will fallback to In-Memory Channel Layer):
   ```bash
   cd website
   python manage.py runserver
   ```
4. Access the site at `http://127.0.0.1:8000/`.

---

## 🐳 Production Deployment (With Docker Compose)

This project is fully containerized and production-ready.

**Prerequisites:**
* Docker and Docker Compose installed.
* The `main/ml/models/` folder fully populated with your `.json` models (Transfer them via FTP if deploying to a VPS).

**Deployment Steps:**
1. Clone this repository to your server.
2. Ensure your `.env` or configurations are correct (Redis is automatically orchestrated).
3. Build and start the containers:
   ```bash
   docker compose up -d --build
   ```

*Note on disk space:* The `.dockerignore` file prevents the heavy 2.2 GB ML models from being copied directly into the Docker Image during the build process, saving massive amounts of build context memory and disk space. Instead, Docker Compose mounts the directory at runtime via Volumes.
