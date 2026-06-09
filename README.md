# 🛡️ Firewall & Network Tools Pro

**Firewall & Network Tools Pro** adalah aplikasi web berbasis Flask yang menyediakan tiga alat penting untuk administrator jaringan:  
- **Generator Konfigurasi Firewall** (FortiGate & CheckPoint)  
- **NSLookup Pro Tool** (DNS lookup dengan multi-threading)  
- **Reverse DNS Lookup** (PTR record + Forward ke public IP)

Aplikasi ini mendukung input teks massal, pemrosesan paralel (threading), dan ekspor hasil ke file Excel.

---

## ✨ Fitur Utama

### 🔥 Firewall Command Generator
- Input daftar IP (satu per baris) dengan format bebas (contoh: `192.168.1.1/32`, `10.0.0.0/24`)
- Normalisasi otomatis format IP yang kotor (seperti `192[.]168[.]1[.]1` menjadi `192.168.1.1`)
- Generate konfigurasi:
  - **FortiGate Address** (setiap IP sebagai objek address)
  - **FortiGate Address Group** (grup berisi semua IP)
  - **CheckPoint Host Objects** (perintah `add host`)

### 🌐 NSLookup Pro Tool
- Input daftar domain (satu per baris)
- Pilih DNS server: **Default System DNS** atau **Public DNS (Multi-Server)** yang mencoba Cloudflare, Google, OpenDNS, Quad9, Comodo secara bergantian
- Pemrosesan multi-threading (1–20 thread) untuk kecepatan maksimal
- Hasil meliputi: IP address, tipe jawaban (authoritative/non-authoritative), waktu respons
- Ekspor ke Excel (2 sheet: detail per IP + ringkasan domain)

### 🔄 Reverse DNS Lookup Tool
- Input teks bebas (satu baris per entri). Setiap baris dapat berisi IP atau teks lain (contoh: `/Common/10.49.58.105:80`)
- Ekstraksi otomatis alamat IPv4 pertama dari setiap baris
- Reverse lookup (PTR) menggunakan resolver sistem untuk mendapatkan nama domain
- Forward lookup ke public IP menggunakan multi-DNS (Cloudflare, Google, OpenDNS, Quad9, Comodo) hingga menemukan IP publik
- Ekspor hasil ke Excel (4 kolom: Data Asli, IP Terekstrak, Domain Reverse, IP Publik Forward)

---

## 🛠️ Teknologi yang Digunakan

- **Backend**: Python 3.8+, Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **DNS Resolution**: `socket`, `subprocess` (nslookup)
- **Excel Generation**: pandas, openpyxl
- **Concurrency**: ThreadPoolExecutor

---

## 📦 Instalasi dan Menjalankan

### Prasyarat
- Python 3.8 atau lebih baru
- Pip (package manager Python)

### Langkah-langkah

1. **Clone repository**
   ```bash
   git clone https://github.com/username/firewall-network-tools.git
   cd firewall-network-tools

