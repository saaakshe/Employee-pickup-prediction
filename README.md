# Employee Location Prediction Fullstack App

This project predicts employee pickup locations using PCA and KMeans clustering, with a fullstack architecture:

- **Backend:** Python (Flask), MySQL, Machine Learning (PCA, KMeans)
- **Frontend:** Flutter (Web & Mobile)
- **Containerization:** Docker & Docker Compose

---

## Features

- Predicts optimal pickup locations for employees using clustering.
- Uses PCA for dimensionality reduction and KMeans for clustering.
- Visualizes optimal K using the elbow method.
- Fullstack: REST API backend, Flutter frontend.
- Fully containerized for easy deployment.

---

## Project Structure

```
employee-prediction-fullstack-docker/
│
├── Backend/                # Flask backend with ML logic
│   ├── app.py
│   ├── requirements.txt
│   └── dockerfile
│
├── employee_prediction/    # Flutter frontend app
│   ├── lib/
│   ├── android/
│   ├── ios/
│   ├── web/
│   ├── pubspec.yaml
│   └── dockerfile
│
├── docker-compose.yml      # Orchestrates backend, frontend, and MySQL
└── .gitignore
```

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- (For local dev) Python 3.9+, Flutter SDK, MySQL

---

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/employee-prediction-fullstack-docker.git
cd employee-prediction-fullstack-docker
```

---

### 2. Environment Configuration

- Backend connects to MySQL using credentials in `docker-compose.yml`.
- Update credentials as needed.

---

### 3. Build & Run with Docker Compose

```sh
docker-compose up --build
```

- Backend: http://localhost:5001
- Frontend: http://localhost:8000

---

### 4. Backend Details

- **Location:** `Backend/`
- **Main file:** `app.py`
- **ML:** Uses PCA and KMeans to cluster employee pickup locations.
- **API:** Flask REST endpoints for predictions.
- **Dependencies:** See `Backend/requirements.txt`

---

### 5. Frontend Details

- **Location:** `employee_prediction/`
- **Framework:** Flutter (Web & Mobile)
- **Dependencies:** See `pubspec.yaml`
- **Build:** Handled via Dockerfile or Flutter CLI.

---

### 6. Database

- **Service:** MySQL (Dockerized)
- **Default credentials:** (see `docker-compose.yml`)
	- User: `jayesh`
	- Password: `12345678`
	- Database: `employeePrediction`
- **Data:** Table `employeedata` with columns for shift date, employee ID, latitude, longitude, etc.

---

### 7. .gitignore

- Ignores build artifacts, IDE files, environment files, and sensitive data for Python, Flutter, Docker, and OS.

---

## Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## License

Specify your license here.

---

## Acknowledgements

- Flask, SQLAlchemy, scikit-learn, Flutter, Docker

---
