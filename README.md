# Smart Gym Attendance System
### Face Recognition-Based Attendance — System Analysis Documentation

> Proyek ini adalah dokumentasi lengkap analisis sistem untuk solusi absensi gym berbasis face recognition. Dibuat sebagai portofolio System Analyst, mencakup seluruh siklus dokumentasi dari requirements hingga test case.

---

## Latar Belakang

Gym terdekat dari lokasi saya masih menggunakan sistem absensi manual yang menyebabkan antrian di pintu masuk dan menyulitkan admin dalam mengelola data kehadiran ratusan member. Proyek ini hadir sebagai solusi: sistem absensi otomatis menggunakan face recognition yang memungkinkan member check-in hanya dengan berdiri di depan kamera, sementara admin mendapatkan dashboard real-time untuk memantau kehadiran dan membership.

---

## Demo Face Recognition

> Kode face recognition engine sudah diimplementasikan secara terpisah menggunakan Python + OpenCV.

```bash
# Clone repo
git clone https://github.com/username/smart-gym-attendance.git
cd smart-gym-attendance

# Install dependencies
pip install -r requirements.txt

# Jalankan face scanner
python face_scanner.py
```

---

## Dokumentasi Sistem

Seluruh artefak analisis sistem tersedia di folder `/docs`:

| Dokumen | Deskripsi | File |
|---|---|---|
| SRS v1.1 | Software Requirements Specification lengkap | `docs/SRS_SmartGym_v1.1.docx` |
| Use Case Diagram | Diagram aktor dan use case sistem | `docs/UseCase_SmartGym.drawio` |
| ERD | Entity Relationship Diagram 4 entitas | `docs/ERD_SmartGym.drawio` |
| Flowchart Check-in | Alur proses check-in happy path & alternatif | `docs/Flowchart_CheckIn_SmartGym.drawio` |
| Test Case Document | 23 test case dari FR-01 sampai FR-08 | `docs/TestCase_SmartGym_v1.0.docx` |
| Traceability Matrix | RTM 100% coverage FR → US → AC → TC → NFR | `docs/RTM_SmartGym_v1.0.docx` |

---

## Scope Sistem

**Dalam scope:**
- Absensi otomatis menggunakan face recognition via kamera/tablet
- Pendaftaran wajah member oleh admin
- Dashboard admin (manajemen member, laporan, absensi manual)
- Dashboard owner (read-only, statistik operasional)
- Pencatatan kehadiran otomatis ke database
- Reminder membership via WhatsApp (H-7, H-3, H-1)

**Di luar scope:**
- Pembayaran membership
- Cloud deployment

---

## Arsitektur Singkat

```
Tablet/Kamera
     │
     ▼
Face Recognition Module  ──►  Database (SQLite/PostgreSQL)
     │                              │
     ▼                              ▼
Attendance System              Admin Dashboard
     │                         Owner Dashboard
     ▼
WhatsApp Reminder (Cron Job)
```

---

## Entity Relationship

```
MEMBER ──(1 to many)──► ATTENDANCE
MEMBER ──(1 to many)──► REMINDER_LOG
ADMIN  ──(1 to many)──► ATTENDANCE (absensi manual)
```

**Entitas utama:**

| Entitas | Atribut kunci |
|---|---|
| MEMBER | member_id, member_name, face_embedded, member_expiry_date, status |
| ADMIN | admin_id, username, password_hash, role (admin/owner) |
| ATTENDANCE | attendance_id, member_id FK, admin_id FK, check_in_time, method (auto/manual) |
| REMINDER_LOG | reminder_id, member_id FK, reminder_type (H7/H3/H1), status (sent/failed) |

---

## Functional Requirements

| ID | Requirement | Aktor |
|---|---|---|
| FR-01 | Pendaftaran wajah member | Admin |
| FR-02 | Verifikasi wajah saat check-in | Member |
| FR-03 | Pencatatan kehadiran otomatis | Sistem |
| FR-04 | Manajemen data member (CRUD) | Admin |
| FR-05 | Laporan kehadiran dengan ekspor | Admin, Owner |
| FR-06 | Reminder otomatis via WhatsApp | Sistem |
| FR-07 | Absensi manual fallback | Admin |
| FR-08 | Dashboard owner (read-only) | Owner |

---

## Non-Functional Requirements

| ID | Kategori | Target |
|---|---|---|
| NFR-01 | Kinerja | Verifikasi wajah ≤ 3 detik |
| NFR-02 | Akurasi | Face recognition ≥ 90% pada pencahayaan normal |
| NFR-03 | Keamanan | Data wajah terenkripsi, akses terotorisasi |
| NFR-04 | Usability | Admin baru onboarding ≤ 15 menit |
| NFR-05 | Availability | Uptime ≥ 99% selama jam operasional (06.00–22.00) |

---

## Coverage Dokumentasi

| Artefak | Jumlah | Coverage |
|---|---|---|
| Functional Requirement (FR) | 8 | 100% |
| User Story (US) | 6 | 100% |
| Acceptance Criteria (AC) | 8 | 100% |
| Test Case (TC) | 23 | 100% |
| Non-Functional Requirement (NFR) | 5 | 100% |

> Seluruh FR memiliki jalur traceability lengkap: **FR → User Story → Acceptance Criteria → Test Case**. Divalidasi melalui Requirements Traceability Matrix (RTM).

---

## Tech Stack (Rencana Implementasi)

| Komponen | Teknologi |
|---|---|
| Face Recognition | Python, OpenCV, face_recognition library |
| Backend | Python (Flask / FastAPI) |
| Database | PostgreSQL |
| Frontend Dashboard | React.js |
| WhatsApp Reminder | Twilio API / WhatsApp Business API |
| Platform | Raspberry Pi / Mini PC (on-premise) |

---

## Struktur Folder

```
smart-gym-attendance/
├── docs/
│   ├── SRS_SmartGym_v1.1.docx
│   ├── UseCase_SmartGym.drawio
│   ├── ERD_SmartGym.drawio
│   ├── Flowchart_CheckIn_SmartGym.drawio
│   ├── TestCase_SmartGym_v1.0.docx
│   └── RTM_SmartGym_v1.0.docx
├── src/
│   ├── face_scanner.py
│   └── ...
├── requirements.txt
└── README.md
```

---

## Role di Proyek Ini

Proyek ini dikerjakan secara mandiri sebagai latihan dokumentasi System Analyst, mencakup:

- Identifikasi stakeholder dan kebutuhan bisnis
- Penulisan Software Requirements Specification (SRS)
- Pembuatan Use Case Diagram dan ERD
- Desain alur sistem (flowchart)
- Wireframing dashboard admin dan owner
- Penyusunan test case dari acceptance criteria
- Pembuatan Requirements Traceability Matrix

---

## Tentang

**Mahasiswa Sistem Informasi — Fasilkom UI**
Semester 2 | Peminatan: Manajemen Tata Kelola

Tertarik di bidang: System Analysis · IT Audit · IT Governance

---

*Dokumentasi ini dibuat sebagai bagian dari portofolio personal. Gym yang menjadi studi kasus adalah gym nyata di sekitar tempat tinggal penulis.*
