# Panduan & Outline Presentasi Video UAS NLP (30-50 Menit)

Rencana presentasi ini dibagi menjadi dua bagian utama sesuai dengan ketentuan soal UAS:
1. **Bagian 1: Penjelasan Teori (15-25 Menit)** - Memaparkan teori dasar LangChain, LangGraph, dan LangSmith.
2. **Bagian 2: Penjelasan Project & Praktik/Demo (15-25 Menit)** - Menunjukkan kode, menjalankan aplikasi, dan memperlihatkan hasil tracing.

---

## 🎥 BAGIAN 1: PRESENTASI TEORI (Durasi: 15-25 Menit)

Gunakan PowerPoint atau Google Slides. Berikut adalah panduan tiap slide dan apa yang harus Anda katakan:

### Slide 1: Pembukaan & Identitas Proyek
* **Judul**: EduGenius: Smart Resume & Cover Letter Analyzer menggunakan Multi-Agent LangGraph.
* **Konten**: Nama Anda, NIM, Kelas, dan Nama Dosen Pengampu.
* **Narasi**: 
  > *"Selamat pagi/siang Bapak/Ibu Dosen dan teman-teman semua. Pada hari ini saya akan mempresentasikan proyek Ujian Akhir Semester saya untuk mata kuliah Natural Language Processing (NLP). Proyek yang saya bangun berjudul EduGenius, yaitu asisten analisis CV dan pembuatan Cover Letter berbasis agen pintar dengan intervensi manusia (human-in-the-loop) menggunakan framework LangChain, LangGraph, dan sistem monitoring LangSmith."*

### Slide 2: Latar Belakang & Masalah (Problem Statement)
* **Konten**:
  * Sulitnya menyelaraskan CV dengan persyaratan lowongan kerja secara manual.
  * Menulis Cover Letter yang unik dan disesuaikan (tailored) memakan banyak waktu.
  * Solusi AI biasa seringkali bersifat sekali jalan (linear) tanpa ada opsi revisi interaktif dari pengguna sebelum hasil akhir disimpan.
* **Narasi**:
  > *"Biasanya, pencari kerja mengirimkan CV yang sama ke banyak lowongan tanpa mempedulikan kata kunci penting yang diminta oleh ATS (Applicant Tracking System). Ketika mereka menggunakan AI generatif biasa, alurnya sangat linear: input CV, output surat lamaran, selesai. Padahal, pengguna sering ingin merevisi bagian tertentu. Di sinilah proyek ini hadir dengan memberikan solusi alur kerja multi-agent yang bisa berputar (iteratif) dan dikontrol langsung oleh pengguna melalui fitur Human-in-the-Loop."*

### Slide 3: Teori LangChain (Core Framework)
* **Konten**:
  * Apa itu LangChain? (Framework untuk membangun aplikasi berbasis LLM).
  * Komponen yang digunakan di proyek ini:
    * **Model Wrapper**: Memanggil Gemini 1.5 Flash secara aman.
    * **Prompt Templates**: Mengatur instruksi sistem untuk peran *CV Analyzer* dan *Cover Letter Generator*.
    * **Chains (LCEL)**: Menghubungkan prompt template dengan model LLM menggunakan operator pipe (`|`).
* **Narasi**:
  > *"Pertama, mari kita bahas LangChain. LangChain adalah pustaka utama yang kami gunakan sebagai jembatan ke LLM. Kami menggunakan model Gemini 1.5 Flash. Di dalam proyek ini, LangChain mempermudah kami mendefinisikan prompt template terstruktur untuk dua tugas utama: menganalisis CV dan membuat surat lamaran kerja. Kami merangkainya menggunakan LCEL (LangChain Expression Language) agar kode program menjadi bersih dan efisien."*

### Slide 4: Teori LangGraph (Stateful Workflow & Human-in-the-Loop)
* **Konten**:
  * Apa itu LangGraph? (Pustaka untuk membangun aplikasi LLM yang memiliki status/state dan bersifat sirkular/looping).
  * Mengapa butuh LangGraph? (Memungkinkan agen untuk berputar melakukan revisi dan mendukung interupsi).
  * Konsep Utama:
    * **State**: Tempat menyimpan memori selama proses berjalan (CV, hasil analisis, draf surat, feedback).
    * **Nodes**: Aksi atau fungsi yang dijalankan (Analyze Node, Generate Node).
    * **Edges & Conditional Edges**: Pengarah alur berdasarkan logika/feedback.
    * **Interrupts & Checkpointer**: Menghentikan alur kerja sebelum node tertentu (Human Review) dan menyimpan statusnya di memori agar bisa dilanjutkan nanti.
* **Narasi**:
  > *"Kedua adalah LangGraph. Pustaka ini sangat penting karena alur penulisan dokumen membutuhkan revisi. Berbeda dengan LangChain biasa yang berjalan searah, LangGraph memungkinkan kita membuat alur kerja sirkular. Kami mendefinisikan State sebagai memori bersama. Alur akan berhenti (interrupt) tepat sebelum langkah ulasan manusia. Sistem akan menyimpan state ke dalam Checkpointer. Setelah manusia memberikan umpan balik (feedback), alur dilanjutkan secara dinamis."*

### Slide 5: Teori LangSmith (Observability & Tracing)
* **Konten**:
  * Apa itu LangSmith? (Platform pengujian, evaluasi, dan pemantauan aplikasi LLM).
  * Manfaat di proyek ini:
    * Melacak setiap langkah pemanggilan API LLM (tracing).
    * Melihat durasi waktu (latency) dan jumlah token (cost tracking) per node.
    * Mempermudah debugging jika prompt tidak memberikan hasil yang diinginkan.
* **Narasi**:
  > *"Ketiga adalah LangSmith. Saat mengembangkan aplikasi LLM, sangat sulit untuk mendebug apa yang dikirim ke LLM dan apa hasilnya secara detail di balik layar. LangSmith membantu memvisualisasikan seluruh rantai panggilan API tersebut. Kita bisa melihat latensi waktu, berapa token yang habis, dan bagaimana perubahan state terjadi secara visual di dashboard LangSmith."*

---

## 💻 BAGIAN 2: BEDAH KODE DAN DEMO IMPLEMENTASI (Durasi: 15-25 Menit)

Pada bagian ini, Anda akan merekam layar komputer Anda untuk memperlihatkan kode program dan menjalankan aplikasinya.

### 📝 Langkah 1: Bedah Struktur Kode (5-7 Menit)
Tunjukkan editor kode Anda (seperti VS Code atau IDE ini) dan jelaskan file satu per satu:
1. **`backend/agents/state.py`**: Jelaskan bahwa file ini mendefinisikan tipe data state yang mengalir di sepanjang graf (input CV, Job Desc, analisis, cover letter, feedback, dan revision count).
2. **`backend/agents/graph.py`**: Jelaskan node-node yang dibuat (`analyze_cv_node`, `generate_cover_letter_node`), logika conditional edge (`decide_next_step`), dan cara meng-compile graph menggunakan checkpointer memori lokal (`MemorySaver()`) serta konfigurasi interrupt `interrupt_before=["human_review"]`.
3. **`backend/app.py`**: Tunjukkan server FastAPI. Jelaskan endpoint `/api/analyze` yang memulai graph, endpoint `/api/feedback` yang memperbarui state dengan feedback pengguna dan melanjutkan graph, serta static files server yang melayani frontend.
4. **`frontend/`**: Perlihatkan file `index.html` (struktur UI), `styles.css` (tampilan premium dark mode), dan `app.js` (menangani fetch API ke backend, memperbarui grafik node visualizer secara interaktif, dan rendering Markdown).

### 🚀 Langkah 2: Demo Aplikasi Berjalan (8-10 Menit)
1. **Jalankan Backend**: Buka terminal dan jalankan server dengan perintah `python app.py` (tunjukkan terminal Anda).
2. **Buka Aplikasi**: Buka browser ke alamat `http://127.0.0.1:8000/`.
3. **Uji Kasus Pertama (Analisis Awal)**:
   * Paste contoh CV samaran (misal: Programmer Web Pemula, menguasai HTML, CSS, JavaScript).
   * Paste contoh Deskripsi Pekerjaan (misal: Lowongan Frontend Developer, mencari yang paham React, Tailwind, Git, dan memiliki skill komunikasi baik).
   * Klik tombol **"Mulai Analisis"**.
   * *Tunjukkan visualizer grafik*: Jelaskan bahwa node Input dan Analyzer menyala hijau, lalu Generator menyala hijau, dan sekarang berhenti di node **Human Feedback** (warna kuning/orange berkedip).
   * Tunjukkan tab **"Hasil Analisis ATS"** yang menampilkan persentase kecocokan (misal 50%) dan mendaftar skill yang hilang (seperti React dan Tailwind).
   * Tunjukkan tab **"Draf Cover Letter"** berisi draf surat lamaran kerja yang sudah disesuaikan.
4. **Uji Kasus Kedua (Proses Revisi / Human-in-the-loop)**:
   * Pada panel umpan balik di bawah, ketik feedback revisi: *"Tolong tambahkan bahwa saya bersedia belajar React dan Tailwind dengan cepat karena saya memiliki dasar JavaScript yang kuat."*
   * Klik **"Kirim Masukan"**.
   * *Jelaskan apa yang terjadi*: Alur graph berjalan kembali ke Node Generator untuk menulis ulang Cover Letter berdasarkan feedback Anda.
   * Tunjukkan draf Cover Letter yang baru, yang sekarang sudah berisi kalimat kesediaan belajar React dan Tailwind. Jumlah revisi bertambah menjadi 1.
5. **Uji Kasus Ketiga (Persetujuan / Approve)**:
   * Jika draf sudah dirasa cocok, klik tombol **"Setujui & Selesai"**.
   * Tunjukkan bahwa panel feedback menghilang, seluruh node di visualizer menjadi hijau (selesai), dan tampilkan pesan sukses.

### 📊 Langkah 3: Demo Monitoring LangSmith (3-5 Menit)
1. Buka browser Anda dan masuk ke akun [LangSmith](https://smith.langchain.com/).
2. Tunjukkan proyek `resume-cover-letter-analyzer`.
3. Klik salah satu run history terbaru hasil demo tadi.
4. Perlihatkan kepada dosen bagaimana grafik trace visual menampilkan alur dari setiap prompt template, waktu eksekusi (latency), dan token yang terpakai untuk memanggil model Gemini.
5. **Narasi**: 
   > *"Di sini bisa kita lihat di LangSmith, setiap panggilan ke Gemini 1.5 Flash terekam dengan rapi. Kita bisa melacak isi prompt lengkap, input variabel yang dimasukkan, dan output teks yang dihasilkan. Ini membuktikan bahwa integrasi LangChain dan monitoring sistem berjalan sempurna."*

### Slide Terakhir: Kesimpulan & Penutup
* Kembalikan layar ke slide PowerPoint penutup.
* Ucapkan terima kasih dan buka sesi tanya jawab virtual.
* **Narasi**:
  > *"Demikian presentasi dan demonstrasi proyek UAS NLP saya mengenai Resume & Cover Letter Analyzer berbasis LangChain dan LangGraph. Sistem berhasil melakukan analisis ATS, menghasilkan draf surat lamaran, menerima revisi dari pengguna, dan terpantau dengan baik di LangSmith. Terima kasih atas perhatiannya, saya siap menerima masukan atau pertanyaan."*
