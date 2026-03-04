# 🔐 CertiSecure – Secure Certificate Generation & Verification Platform

CertiSecure is a platform designed to help hackathons, events, and organizations generate **secure digital certificates** and allow **instant verification using QR codes and unique IDs**.

The system automates certificate generation, bulk participant uploads, and verification workflows.

---

# 🚀 What It Does

CertiSecure allows organizers to:

• Upload participant data using Excel  
• Automatically generate certificates  
• Add secure verification IDs  
• Provide a public certificate verification page  
• Allow users to download and verify certificates  

---

# 🏗 Architecture

Frontend (React + GSAP)

↓

Backend API (FastAPI)

↓

Certificate Engine

↓

Database (PostgreSQL)

↓

PDF Generator + QR Verification

---

# 🛠 Tech Stack

### Frontend
• React  
• GSAP Animations  
• TailwindCSS  
• Zustand State Management  

### Backend
• FastAPI  
• PostgreSQL  
• Redis  

### Infrastructure
• Docker  
• Cloud Deployment  

---

# 📂 Project Structure

```
Certisecure/
│
├ frontend/        # React UI
├ backend/         # FastAPI backend
├ docs/            # Project documentation
└ infrastructure/  # Deployment configuration
```

---

# ⭐ Key Features

### 🎓 Certificate Generation
Automatic PDF certificate creation for participants.

### 📊 Bulk Participant Upload
Upload Excel sheet to generate certificates for hundreds of users.

### 🔍 Certificate Verification
Public verification page to validate certificates using:

• Certificate ID  
• QR Code  

### 👨‍💼 Admin Dashboard
Admins can:

• Upload participant lists  
• Generate certificates  
• Track issued certificates  

---

# ⚡ Quick Start (Development)

### Clone Repository

```
git clone <repo-url>
cd certisecure
```

### Backend Setup

```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```
cd frontend
npm install
npm run dev
```

---

# 🌐 Access

Frontend  
```
http://localhost:3000
```

Backend API Docs  
```
http://localhost:8000/docs
```

---

# 📄 Future Improvements

• Blockchain certificate verification  
• Email certificate delivery  
• Organization dashboard  
• Public certificate directory  

---

# 🤝 Contributors

CertiSecure Team
