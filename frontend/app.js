// Global State
let currentThreadId = null;
const API_URL = "http://127.0.0.1:8000";

// DOM Elements
const cvInput = document.getElementById("cvInput");
const jdInput = document.getElementById("jdInput");
const btnAnalyze = document.getElementById("btnAnalyze");
const envStatus = document.getElementById("envStatus");

// Tab Elements
const tabBtns = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");
const analysisContent = document.getElementById("analysisContent");
const clContent = document.getElementById("clContent");
const placeholderAnalysis = document.getElementById("placeholder-analysis");
const placeholderCl = document.getElementById("placeholder-cl");
const clActions = document.getElementById("clActions");
const btnCopyCl = document.getElementById("btnCopyCl");

// Graph Nodes
const nodeInput = document.getElementById("node-input");
const nodeAnalyzer = document.getElementById("node-analyzer");
const nodeGenerator = document.getElementById("node-generator");
const nodeHuman = document.getElementById("node-human");

// Feedback Elements
const feedbackPanel = document.getElementById("feedbackPanel");
const feedbackInput = document.getElementById("feedbackInput");
const btnSubmitFeedback = document.getElementById("btnSubmitFeedback");
const btnApprove = document.getElementById("btnApprove");
const revisionCountEl = document.getElementById("revisionCount");
const toast = document.getElementById("toast");

// ==========================================
// INITIAL SETUP & EVENT LISTENERS
// ==========================================

// Tab Switching Logic
tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        const targetTab = btn.getAttribute("data-tab");
        
        tabBtns.forEach(b => b.classList.remove("active"));
        tabContents.forEach(c => c.classList.remove("active"));
        
        btn.classList.add("active");
        document.getElementById(targetTab).classList.add("active");
    });
});

// Copy Cover Letter to Clipboard
btnCopyCl.addEventListener("click", () => {
    // Ambil raw text yang ada di clContent
    const textToCopy = clContent.innerText;
    navigator.clipboard.writeText(textToCopy).then(() => {
        showToast("Cover Letter berhasil disalin!", "success");
    }).catch(err => {
        showToast("Gagal menyalin teks: " + err, "error");
    });
});

// Cek koneksi backend saat startup
async function checkBackendConnection() {
    try {
        const res = await fetch(`${API_URL}/`);
        if (res.ok) {
            envStatus.innerHTML = '<span class="indicator-dot green"></span> Backend Terhubung';
        } else {
            throw new Error();
        }
    } catch (e) {
        envStatus.innerHTML = '<span class="indicator-dot red"></span> Backend Terputus';
        showToast("Gagal terhubung ke API backend server. Pastikan uvicorn berjalan.", "error");
    }
}

checkBackendConnection();

// ==========================================
// GRAPH CONTROLLER LOGIC
// ==========================================

// Reset Tampilan Grafik Node
function resetNodeStates() {
    [nodeInput, nodeAnalyzer, nodeGenerator, nodeHuman].forEach(node => {
        node.className = "node";
    });
}

// Mulai Alur Analisis Utama
btnAnalyze.addEventListener("click", async () => {
    const cv = cvInput.value.trim();
    const jd = jdInput.value.trim();
    
    if (!cv || !jd) {
        showToast("Mohon isi teks CV dan Deskripsi Lowongan terlebih dahulu!", "warning");
        return;
    }
    
    // Set UI State Loading
    btnAnalyze.disabled = true;
    btnAnalyze.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Memproses...';
    
    resetNodeStates();
    nodeInput.classList.add("completed");
    
    // Aktifkan Node Analyzer
    nodeAnalyzer.classList.add("active");
    
    try {
        const response = await fetch(`${API_URL}/api/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ cv, job_description: jd })
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Terjadi kesalahan di server.");
        }
        
        const data = await response.json();
        
        // Simpan thread ID untuk revisi
        currentThreadId = data.thread_id;
        
        // Render Hasil Analisis ATS
        analysisContent.innerHTML = marked.parse(data.analysis);
        analysisContent.classList.remove("hidden");
        placeholderAnalysis.classList.add("hidden");
        
        // Tandai Node Analyzer Selesai
        nodeAnalyzer.classList.remove("active");
        nodeAnalyzer.classList.add("completed");
        
        // Render Cover Letter
        clContent.innerHTML = marked.parse(data.cover_letter);
        clContent.classList.remove("hidden");
        placeholderCl.classList.add("hidden");
        clActions.classList.remove("hidden");
        
        // Tandai Node Generator Selesai
        nodeGenerator.classList.add("completed");
        
        // Pindah Tab Otomatis ke tab Analisis
        switchTab("tab-analysis");
        
        // Pengecekan Human-in-the-loop (Interrupt)
        if (data.status === "waiting_feedback") {
            // Tandai Node Human sedang menunggu review (Warna Kuning)
            nodeHuman.classList.add("waiting");
            
            // Tampilkan Panel Feedback
            feedbackPanel.classList.remove("hidden");
            revisionCountEl.textContent = data.revision_count;
            showToast("Analisis selesai. Menunggu ulasan Anda!", "info");
        }
        
    } catch (error) {
        showToast(error.message, "error");
        resetNodeStates();
    } finally {
        btnAnalyze.disabled = false;
        btnAnalyze.innerHTML = '<i class="fa-solid fa-magnifying-glass-chart"></i> Mulai Analisis & Pembuatan';
    }
});

// Kirim Feedback Revisi
btnSubmitFeedback.addEventListener("click", async () => {
    const feedback = feedbackInput.value.trim();
    if (!feedback) {
        showToast("Mohon masukkan instruksi revisi terlebih dahulu!", "warning");
        return;
    }
    
    if (!currentThreadId) {
        showToast("Sesi analisis tidak valid.", "error");
        return;
    }
    
    // Set UI State Loading
    btnSubmitFeedback.disabled = true;
    btnSubmitFeedback.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Mengirim...';
    
    // Set Visualizer Node State (Kembali mengedit)
    nodeHuman.className = "node completed";
    nodeGenerator.className = "node active";
    
    try {
        const response = await fetch(`${API_URL}/api/feedback`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                thread_id: currentThreadId,
                feedback: feedback
            })
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Gagal mengirim feedback.");
        }
        
        const data = await response.json();
        
        // Update Cover Letter
        clContent.innerHTML = marked.parse(data.cover_letter);
        switchTab("tab-cl");
        
        feedbackInput.value = ""; // Reset input
        revisionCountEl.textContent = data.revision_count;
        
        // Kembalikan ke state interrupt
        nodeGenerator.className = "node completed";
        nodeHuman.className = "node waiting";
        
        showToast("Cover Letter berhasil diperbarui berdasarkan masukan Anda!", "success");
        
    } catch (error) {
        showToast(error.message, "error");
        nodeGenerator.className = "node completed";
        nodeHuman.className = "node waiting";
    } finally {
        btnSubmitFeedback.disabled = false;
        btnSubmitFeedback.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Kirim Masukan';
    }
});

// Setujui & Selesai (Approve)
btnApprove.addEventListener("click", async () => {
    if (!currentThreadId) {
        showToast("Sesi analisis tidak valid.", "error");
        return;
    }
    
    btnApprove.disabled = true;
    btnApprove.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Memproses...';
    
    try {
        const response = await fetch(`${API_URL}/api/feedback`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                thread_id: currentThreadId,
                feedback: "approve"
            })
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Gagal menyetujui draf.");
        }
        
        const data = await response.json();
        
        // Sembunyikan panel feedback
        feedbackPanel.classList.add("hidden");
        
        // Tandai semua node selesai
        nodeHuman.className = "node completed";
        
        showToast("Cover Letter disetujui! Proses selesai.", "success");
        
    } catch (error) {
        showToast(error.message, "error");
    } finally {
        btnApprove.disabled = false;
        btnApprove.innerHTML = '<i class="fa-solid fa-circle-check"></i> Setujui & Selesai';
    }
});


// ==========================================
// HELPER FUNCTIONS
// ==========================================

function switchTab(tabId) {
    tabBtns.forEach(btn => {
        if (btn.getAttribute("data-tab") === tabId) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });
    
    tabContents.forEach(c => {
        if (c.id === tabId) {
            c.classList.add("active");
        } else {
            c.classList.remove("active");
        }
    });
}

function showToast(message, type = "info") {
    toast.textContent = message;
    toast.className = "toast"; // Reset
    
    // Warnai toast berdasarkan jenis pesan
    if (type === "error") {
        toast.style.borderColor = "#ef4444";
        toast.innerHTML = `<i class="fa-solid fa-circle-exclamation" style="color: #ef4444;"></i> ${message}`;
    } else if (type === "success") {
        toast.style.borderColor = "var(--success)";
        toast.innerHTML = `<i class="fa-solid fa-circle-check" style="color: var(--success);"></i> ${message}`;
    } else if (type === "warning") {
        toast.style.borderColor = "var(--warning)";
        toast.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: var(--warning);"></i> ${message}`;
    } else {
        toast.style.borderColor = "var(--primary)";
        toast.innerHTML = `<i class="fa-solid fa-circle-info" style="color: var(--primary);"></i> ${message}`;
    }
    
    toast.classList.remove("hidden");
    
    setTimeout(() => {
        toast.classList.add("hidden");
    }, 4000);
}
