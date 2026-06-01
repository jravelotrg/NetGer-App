# 🛡️ NetGer App v1.2.0

**Firewall & Network Administration Tools**

---

## 📖 Deskripsi

**NetGer App** adalah aplikasi tools administrasi jaringan yang membantu Network Administrator dalam:

- 🔥 **Generate konfigurasi Firewall** (FortiGate & CheckPoint)
- 🌐 **NSLookup massal** dengan multi-threading
- 📊 **Export hasil ke Excel**
- ⚡ **Multi DNS Server support**
- 🔄 **Auto-clean domain format** (google[.]com → google.com)

---

## ✨ Fitur Utama

### 🔥 Firewall Command Generator
- Generate script konfigurasi FortiGate Address
- Generate script konfigurasi FortiGate Group
- Generate script konfigurasi CheckPoint
- Support multiple IP format
- Duplicate IP removal otomatis
- One-click copy to clipboard

### 🌐 NSLookup Pro Tool
- Multi DNS Server (Google, Cloudflare, Quad9, OpenDNS, Default System)
- Multi-threading support (1-20 threads)
- Configurable timeout (1-30 detik)
- Real-time logging dengan timestamp
- Progress bar visual
- Export hasil ke Excel (.xlsx) dengan 2 sheet:
  - **Detailed Results** (1 IP per baris)
  - **Domain Summary** (ringkasan per domain)
- Support multiple IP detection
- IP Tooltip untuk domain dengan banyak IP (>3 IP)
- **Auto-clean domain format** - Otomatis mengubah:
  - `google[.]com` → `google.com`
  - `facebook(.)com` → `facebook.com`
  - `malware{.}net` → `malware.net`

### 🎨 UI/UX
- Modern dark theme dengan gradient accent
- Responsive full-width desktop design
- Smooth animations (fadeIn, slideIn, pulse)
- Keyboard shortcuts (Ctrl+1, Ctrl+2)
- Toast notifications untuk feedback
- Copy to clipboard dengan visual feedback
- Footer dengan link LinkedIn

---

## 📌 Keyboard Shortcuts

| Shortcut | Fungsi |
|----------|--------|
| `Ctrl+1` | Buka Firewall Command Generator |
| `Ctrl+2` | Buka NSLookup Pro Tool |

---

## 📸 Screenshot

<img width="1897" height="961" alt="image" src="https://github.com/user-attachments/assets/73b88b4b-a934-42f8-ad24-c560e777f157" />
<img width="1894" height="955" alt="image" src="https://github.com/user-attachments/assets/06d4a836-16a6-40c4-9d88-8dabf730971a" />

---

## 🚀 Cara Install

### Metode 1: Menggunakan Installer (Rekomendasi)
1. Download file installer `NetGer_App_Setup_v1.2.0.exe`
2. Double-click untuk menjalankan installer
3. Ikuti wizard instalasi
4. Aplikasi siap digunakan

### Metode 2: Build dari Source
```bash
# Clone repository
git clone https://github.com/jravelotrg/NetGer-App.git

# Masuk ke folder
cd NetGer-App

# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
python app.py

# Buka browser di alamat
http://127.0.0.1:5000
