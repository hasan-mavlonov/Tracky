# 🛰️ Tracky – Real-Time RFID Inventory & POS System for Clothing Stores

**Tracky** is a modern POS and inventory tracking system specifically built for clothing stores. Using low-cost RFID + barcode technology, it enables 24/7 monitoring of inventory to prevent product loss, miscounts, and theft — without the high costs traditionally associated with RFID infrastructure.

---

## 🚀 Product Overview

**What is Tracky?**  
Tracky is a hybrid POS and inventory management system that allows clothing stores to monitor products in real-time using RFID and barcodes.  

**What problem does it solve?**  
- Prevents inventory loss and product miscounts  
- Minimizes theft through 24/7 product detection  
- Simplifies product tracking across multiple stores  

**Why is it unique?**  
- ✅ **Omnidirectional RFID reader** with wide-range detection  
- 💸 **Extremely cheap RFID tags** (only $0.07 each)  
- 🖨️ **No special printers required** — standard thermal printers can print our RFID barcode tags  

---

## ⚙️ Features

### 📦 Inventory Tracking with RFID
Each item is tagged with a barcode-printed RFID label. Tags are tracked in real time to determine whether a product is inside or outside the store.

### 🧾 RFID + Barcode Label Printing
Tracky supports printing RFID barcode labels using regular thermal printers, eliminating the need for expensive UHF printers.

### 👤 Role-Based Access Control (RBAC)
Users can log in with specific roles (Owner, Cashier, SuperAdmin). Role permissions are enforced using JWT authentication.

### 🏪 Product & Shop Management
Create and manage:
- Products and their instances
- Shops and their inventories
- Assign items to shops, view per-location stock, and track sales

### 🔌 Real-Time RFID Integration (Windows Agent)
A lightweight native **Windows Agent** reads RFID tag data via USB reader using `SWHidApi.dll`, sending data to the Django backend via a local **Flask app**.

### 🧾 Multi-Tag Selling (Sales Module)
Scan multiple RFID tags, view a queue of items to be sold, confirm transaction in batch, and auto-update inventory.

---

## 🛠️ Tech Stack

| Component       | Stack / Tooling                         |
|----------------|------------------------------------------|
| Backend         | Django + Django REST Framework          |
| Frontend        | HTML + JavaScript (jwtFetch pattern)    |
| Local Service   | Flask (Python)                          |
| Native Agent    | Windows app using SWHidApi.dll (RFID)   |
| Database        | PostgreSQL                              |
| Hardware        | INveton RFID reader, USB barcode scanner, thermal printer |
| Hosting         | Render                                  |

---

## 🧪 Traction & MVP Status

| Metric | Value |
|--------|-------|
| Waitlist / LOIs       | 56 stores |
| Stores tested         | 1 store (MVP trial) |
| Total tracked sales   | 0 (pilot phase) |
| Feedback              | Collected verbally, not yet documented |
| MVP Complete          | ✅ Yes |

---

## 👥 Team

- **Hasan Mavlonov** – CEO & Founder  
- **Temurmalik Ilxomjonov** – Project Manager  

---

## 🧱 Business Model

- **Monthly Subscription** (per store)
- **Pay-per-Tag** model (based on tag usage)
- **Optional Hardware Bundles** (RFID Readers, Printers)

---

## 📈 Next Steps

- Raise **$10,000–$50,000** in pre-seed investment  
- Hire a **Frontend Developer** to build the POS UI  
- Start structured pilot testing with early adopters  
- Hire a **3D Designer** for interactive retail dashboards  

---

## 📦 Installation (Coming Soon)

This repo is not yet ready for public installation. In the near future, we will provide:
- Setup guides
- Docker configuration
- Dev environment setup

---

## 🔐 Security

Tracky uses:
- JWT-based authentication
- Role-based permission layers
- Server-client separation of concerns for hardware

---

## 📬 Contact

Interested in partnering, testing, or investing?  
📧 hmavlanov79@gmail.com  
🌐 tracky.one

---

## 📄 License

This project is currently **private** and under development. Licensing to be determined.

---

## 🧭 TL;DR

Tracky is a POS + inventory system for clothing stores using ultra-cheap RFID tech. Tracks every item in real time using omnidirectional readers, printed via thermal printers. MVP is ready, pilot store tested, and we're fundraising to scale and expand.

---

