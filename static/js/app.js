/**
 * Calculus Bridge - Interactive Gamified Learning Engine
 * Features:
 * - Sound Synthesis Engine (Web Audio API)
 * - Animated Reactive Mascot ("Archie the Axolotl")
 * - Adaptive Diagnostic Evaluation Engine
 * - Skill Tree Progression & Unlocking (Duolingo style)
 * - Immediate Feedback & Step-by-Step Learning Drawer
 * - LocalStorage State Persistence
 */

// ==========================================
// 1. SOUND SYNTHESIS ENGINE (Web Audio API)
// ==========================================
class SoundEngine {
    constructor() {
        this.ctx = null;
        this.enabled = true;
    }

    init() {
        if (!this.ctx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) {
                this.ctx = new AudioCtx();
            }
        }
    }

    toggle(enable) {
        this.enabled = enable !== undefined ? enable : !this.enabled;
        return this.enabled;
    }

    playTone(freq, type = 'sine', duration = 0.15, startTime = 0, gainLevel = 0.1) {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;

        try {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = type;
            osc.frequency.setValueAtTime(freq, this.ctx.currentTime + startTime);

            gain.gain.setValueAtTime(gainLevel, this.ctx.currentTime + startTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + startTime + duration);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(this.ctx.currentTime + startTime);
            osc.stop(this.ctx.currentTime + startTime + duration);
        } catch (e) {
            console.warn("Audio play prevented:", e);
        }
    }

    playSuccess() {
        // Harmonious arpeggio: C5 -> E5 -> G5 -> C6
        const notes = [523.25, 659.25, 783.99, 1046.50];
        notes.forEach((freq, idx) => {
            this.playTone(freq, 'triangle', 0.2, idx * 0.08, 0.15);
        });
    }

    playError() {
        // Gentle, soft low boop (not annoying)
        this.playTone(220, 'sine', 0.18, 0, 0.15);
        this.playTone(185, 'sine', 0.25, 0.12, 0.15);
    }

    playClick() {
        this.playTone(600, 'triangle', 0.04, 0, 0.08);
    }

    playFanfare() {
        // Celebratory victory chords
        const seq = [
            { f: 523.25, t: 0, d: 0.12 },
            { f: 659.25, t: 0.1, d: 0.12 },
            { f: 783.99, t: 0.2, d: 0.14 },
            { f: 1046.50, t: 0.32, d: 0.35 }
        ];
        seq.forEach(s => this.playTone(s.f, 'sine', s.d, s.t, 0.18));
    }
}

const sounds = new SoundEngine();

// ==========================================
// 2. MASCOT CONTROLLER ("Archie the Axolotl")
// ==========================================
class MascotController {
    constructor() {
        this.mascotEl = document.getElementById('mascot-avatar');
        this.speechEl = document.getElementById('mascot-speech');
        this.expression = 'idle';

        this.quotes = [
            "Halo! Aku Archie, pemandumu menaklukkan kalkulus!",
            "Tahukah kamu? Notasi dy/dx dibuat oleh Leibniz, sedangkan Newton memakai notasi titik ẏ!",
            "Limit itu seperti mendekati gebetan: sedekat mungkin, tapi ga harus saling bersentuhan!",
            "Turunan adalah laju perubahan sesaat—seperti speedometer mobilmu!",
            "Integral adalah akumulasi area di bawah kurva: menjumlahkan hal-hal kecil menjadi besar!",
            "Tenang! Kalau kamu salah, itu tandanya otakmu sedang membentuk sinapsis matematika baru!"
        ];
    }

    setMood(mood, text = null) {
        this.expression = mood;
        if (!this.mascotEl) return;

        // Reset classes
        this.mascotEl.classList.remove('mascot-celebrate', 'mascot-thinking', 'mascot-comfort', 'mascot-wave');

        if (mood === 'celebrate') {
            this.mascotEl.classList.add('mascot-celebrate');
        } else if (mood === 'thinking') {
            this.mascotEl.classList.add('mascot-thinking');
        } else if (mood === 'comfort') {
            this.mascotEl.classList.add('mascot-comfort');
        } else if (mood === 'wave') {
            this.mascotEl.classList.add('mascot-wave');
        }

        if (text && this.speechEl) {
            this.say(text);
        }
    }

    say(text) {
        if (!this.speechEl) return;
        this.speechEl.innerHTML = text;
        this.speechEl.classList.remove('speech-pop');
        // trigger reflow
        void this.speechEl.offsetWidth;
        this.speechEl.classList.add('speech-pop');
    }

    randomQuote() {
        const rand = this.quotes[Math.floor(Math.random() * this.quotes.length)];
        this.setMood('wave', rand);
        sounds.playClick();
    }
}

// ==========================================
// 3. PERSISTENT GAME STATE
// ==========================================
const DEFAULT_STATE = {
    faculty: 'fasilkom', // 'ft', 'fasilkom', 'fmipa'
    xp: 60,
    streak: 3,
    hearts: 5,
    maxHearts: 5,
    gems: 120,
    completedNodes: ['node-precalc'],
    activeNode: 'node-limit',
    diagnosticCompleted: false,
    diagnosticLevel: 'Belum Dievaluasi',
    soundEnabled: true
};

class GameStateManager {
    constructor() {
        this.state = this.loadState();
        sounds.toggle(this.state.soundEnabled);
    }

    loadState() {
        try {
            const saved = localStorage.getItem('calculus_bridge_state_v1');
            if (saved) return Object.assign({}, DEFAULT_STATE, JSON.parse(saved));
        } catch (e) {
            console.warn("Storage read error:", e);
        }
        return Object.assign({}, DEFAULT_STATE);
    }

    saveState() {
        try {
            localStorage.setItem('calculus_bridge_state_v1', JSON.stringify(this.state));
        } catch (e) {
            console.warn("Storage write error:", e);
        }
        this.updateHUD();
    }

    addXP(points) {
        this.state.xp += points;
        this.saveState();
        this.showFloatingXP(points);
    }

    deductHeart() {
        if (this.state.hearts > 0) {
            this.state.hearts -= 1;
            this.saveState();
            sounds.playError();
            this.animateHeartLoss();
        }
    }

    setFaculty(fac) {
        this.state.faculty = fac;
        this.saveState();
    }

    completeNode(nodeId, nextNodeId = null) {
        if (!this.state.completedNodes.includes(nodeId)) {
            this.state.completedNodes.push(nodeId);
        }
        if (nextNodeId) {
            this.state.activeNode = nextNodeId;
        }
        this.saveState();
    }

    updateHUD() {
        const xpEl = document.getElementById('hud-xp');
        const streakEl = document.getElementById('hud-streak');
        const heartsEl = document.getElementById('hud-hearts');
        const gemsEl = document.getElementById('hud-gems');
        const facultyBadgeEl = document.getElementById('hud-faculty-badge');
        const soundBtn = document.getElementById('sound-toggle-btn');

        if (xpEl) xpEl.textContent = `${this.state.xp} XP`;
        if (streakEl) streakEl.textContent = `${this.state.streak}`;
        if (heartsEl) heartsEl.textContent = `${this.state.hearts}/${this.state.maxHearts}`;
        if (gemsEl) gemsEl.textContent = `${this.state.gems}`;

        if (facultyBadgeEl) {
            const labels = {
                'ft': '⚙️ Fak. Teknik',
                'fasilkom': '💻 Fasilkom',
                'fmipa': '🔬 FMIPA'
            };
            facultyBadgeEl.textContent = labels[this.state.faculty] || 'Fasilkom';
        }

        if (soundBtn) {
            soundBtn.textContent = this.state.soundEnabled ? '🔊 Suara' : '🔇 Mute';
            soundBtn.classList.toggle('muted', !this.state.soundEnabled);
        }
    }

    showFloatingXP(amount) {
        const hudXp = document.getElementById('hud-xp');
        if (!hudXp) return;
        const floatSpan = document.createElement('span');
        floatSpan.className = 'floating-xp-anim';
        floatSpan.textContent = `+${amount} XP!`;
        document.body.appendChild(floatSpan);

        const rect = hudXp.getBoundingClientRect();
        floatSpan.style.left = `${rect.left + 10}px`;
        floatSpan.style.top = `${rect.top - 20}px`;

        setTimeout(() => floatSpan.remove(), 1200);
    }

    animateHeartLoss() {
        const heartEl = document.getElementById('hud-hearts-container');
        if (heartEl) {
            heartEl.classList.add('heart-shake');
            setTimeout(() => heartEl.classList.remove('heart-shake'), 600);
        }
    }
}

const gameState = new GameStateManager();
const mascot = new MascotController();

// ==========================================
// 4. DIAGNOSTIC EVALUATION SYSTEM
// ==========================================
const DIAGNOSTIC_QUESTIONS = {
    fasilkom: [
        {
            level: 'Dasar (Basic)',
            difficulty: 'basic',
            prompt: "Sederhanakan ekspresi aljabar berikut untuk x ≠ 3:\n$$\\frac{x^2 - 9}{x - 3}$$",
            options: [
                { text: "x - 3", isCorrect: false },
                { text: "x + 3", isCorrect: true },
                { text: "3x", isCorrect: false },
                { text: "x^2 + 3", isCorrect: false }
            ],
            explanation: "Pembilang merupakan selisih dua kuadrat: x² - 9 = (x - 3)(x + 3). Setelah membagi dengan penyebut (x - 3), tersisa (x + 3)."
        },
        {
            level: 'Menengah (Medium)',
            difficulty: 'medium',
            prompt: "Tentukan nilai dari limit fungsi rasional berikut:\n$$\\lim_{x \\to 2} \\frac{x^2 + x - 6}{x - 2}$$",
            options: [
                { text: "0", isCorrect: false },
                { text: "5", isCorrect: true },
                { text: "4", isCorrect: false },
                { text: "Tidak terdefinisi (∞)", isCorrect: false }
            ],
            explanation: "Substitusi langsung menghasilkan bentuk tak tentu 0/0. Faktorkan pembilang: x² + x - 6 = (x + 3)(x - 2). Coret faktor (x - 2) lalu substitusi x = 2: 2 + 3 = 5."
        },
        {
            level: 'Tinggi (High)',
            difficulty: 'high',
            prompt: "Dalam optimasi Machine Learning (Gradient Descent), kita butuh turunan fungsi error. Tentukan f'(x) untuk:\n$$f(x) = (3x^2 + 1)^3$$",
            options: [
                { text: "9(3x² + 1)²", isCorrect: false },
                { text: "18x (3x² + 1)²", isCorrect: true },
                { text: "6x (3x² + 1)²", isCorrect: false },
                { text: "3(6x)²", isCorrect: false }
            ],
            explanation: "Gunakan Aturan Rantai (Chain Rule): Misal u = 3x² + 1 maka u' = 6x. Turunan dari u³ adalah 3u² · u' = 3(3x² + 1)² · 6x = 18x(3x² + 1)²."
        }
    ],
    ft: [
        {
            level: 'Dasar (Basic)',
            difficulty: 'basic',
            prompt: "Sebuah partikel bergerak dengan persamaan s(t) = 4t² - 2t. Berapakah nilai s(3) - s(1)?",
            options: [
                { text: "28", isCorrect: true },
                { text: "24", isCorrect: false },
                { text: "30", isCorrect: false },
                { text: "16", isCorrect: false }
            ],
            explanation: "s(3) = 4(9) - 2(3) = 36 - 6 = 30. s(1) = 4(1) - 2(1) = 2. Selisih = 30 - 2 = 28."
        },
        {
            level: 'Menengah (Medium)',
            difficulty: 'medium',
            prompt: "Tentukan gradien garis singgung kurva y = 2x² - 5x pada titik x = 3.",
            options: [
                { text: "7", isCorrect: true },
                { text: "12", isCorrect: false },
                { text: "3", isCorrect: false },
                { text: "-5", isCorrect: false }
            ],
            explanation: "Gradien m = dy/dx = 4x - 5. Pada x = 3: m = 4(3) - 5 = 12 - 5 = 7."
        },
        {
            level: 'Tinggi (High)',
            difficulty: 'high',
            prompt: "Sebuah tangki air berbentuk kerucut terbalik. Jika volume V = (1/3)π r² h dan r = (1/2)h, tentukan laju dV/dh saat h = 4 meter.",
            options: [
                { text: "4π m²/s", isCorrect: true },
                { text: "2π m²/s", isCorrect: false },
                { text: "8π m²/s", isCorrect: false },
                { text: "16π m²/s", isCorrect: false }
            ],
            explanation: "V = (1/3)π ((1/2)h)² h = (1/12)π h³. Maka dV/dh = (3/12)π h² = (1/4)π (4)² = 4π."
        }
    ],
    fmipa: [
        {
            level: 'Dasar (Basic)',
            difficulty: 'basic',
            prompt: "Faktorkan dan tentukan akar-akar real dari persamaan kuadrat:\n$$2x^2 - 7x + 3 = 0$$",
            options: [
                { text: "x = 3 dan x = 1/2", isCorrect: true },
                { text: "x = -3 dan x = -1/2", isCorrect: false },
                { text: "x = 2 dan x = 3/2", isCorrect: false },
                { text: "x = 7 dan x = 3", isCorrect: false }
            ],
            explanation: "Faktorkan: (2x - 1)(x - 3) = 0. Menghasilkan x = 1/2 atau x = 3."
        },
        {
            level: 'Menengah (Medium)',
            difficulty: 'medium',
            prompt: "Hitung limit trigonometri fundamental berikut:\n$$\\lim_{x \\to 0} \\frac{\\sin(5x)}{x}$$",
            options: [
                { text: "0", isCorrect: false },
                { text: "1", isCorrect: false },
                { text: "5", isCorrect: true },
                { text: "Tak terdefinisi", isCorrect: false }
            ],
            explanation: "Berdasarkan teorema limit trigonometri lim_{u→0} sin(u)/u = 1. Dengan u = 5x, lim_{x→0} 5 · (sin(5x)/(5x)) = 5(1) = 5."
        },
        {
            level: 'Tinggi (High)',
            difficulty: 'high',
            prompt: "Berdasarkan definisi turunan limit f'(x) = lim_{h→0} [f(x+h) - f(x)] / h, tentukan turunan dari f(x) = 1/x.",
            options: [
                { text: "-1 / x²", isCorrect: true },
                { text: "1 / x²", isCorrect: false },
                { text: "-1 / x", isCorrect: false },
                { text: "ln|x|", isCorrect: false }
            ],
            explanation: "[1/(x+h) - 1/x]/h = [(x - (x+h)) / (x(x+h))]/h = -h / (h · x(x+h)) = -1 / (x(x+h)). Saat h→0, hasilnya -1/x²."
        }
    ]
};

class DiagnosticRunner {
    constructor() {
        this.currentStep = 0;
        this.answers = [];
        this.questions = [];
        this.selectedOptionIndex = null;
        this.modal = document.getElementById('diagnostic-modal');
    }

    start() {
        const fac = gameState.state.faculty || 'fasilkom';
        this.questions = DIAGNOSTIC_QUESTIONS[fac] || DIAGNOSTIC_QUESTIONS['fasilkom'];
        this.currentStep = 0;
        this.answers = [];
        this.selectedOptionIndex = null;

        if (this.modal) {
            this.modal.classList.add('active');
            sounds.playClick();
            mascot.setMood('thinking', "Ayo kita ukur kemampuan dasarmu! Santai saja, tes ini adaptif.");
            this.renderQuestion();
        }
    }

    renderQuestion() {
        const q = this.questions[this.currentStep];
        const container = document.getElementById('diag-quiz-content');
        if (!container) return;

        this.selectedOptionIndex = null;

        const progressPercent = ((this.currentStep) / this.questions.length) * 100;

        container.innerHTML = `
            <div class="diag-header-bar">
                <span class="badge badge-difficulty ${q.difficulty}">${q.level}</span>
                <span class="diag-step-counter">Soal ${this.currentStep + 1} dari ${this.questions.length}</span>
            </div>
            <div class="diag-progress-track">
                <div class="diag-progress-fill" style="width: ${progressPercent}%;"></div>
            </div>
            <div class="diag-prompt-box">
                <p class="diag-prompt-text">${this.formatMath(q.prompt)}</p>
            </div>
            <div class="diag-options-grid" id="diag-options">
                ${q.options.map((opt, idx) => `
                    <button class="diag-opt-btn" onclick="diagnosticRunner.selectOption(${idx})">
                        <span class="opt-letter">${String.fromCharCode(65 + idx)}</span>
                        <span class="opt-text">${this.formatMath(opt.text)}</span>
                    </button>
                `).join('')}
            </div>
            <div class="diag-action-bar">
                <button class="btn btn-primary btn-3d" id="diag-check-btn" disabled onclick="diagnosticRunner.submitAnswer()">
                    Jawab & Lanjutkan ➔
                </button>
            </div>
        `;
    }

    formatMath(text) {
        // Simple clean replacement for inline math preview
        return text.replace(/\$\$(.*?)\$\$/g, '<strong>$1</strong>');
    }

    selectOption(index) {
        this.selectedOptionIndex = index;
        sounds.playClick();

        const btns = document.querySelectorAll('.diag-opt-btn');
        btns.forEach((btn, idx) => {
            btn.classList.toggle('selected', idx === index);
        });

        const checkBtn = document.getElementById('diag-check-btn');
        if (checkBtn) checkBtn.removeAttribute('disabled');
    }

    submitAnswer() {
        if (this.selectedOptionIndex === null) return;

        const q = this.questions[this.currentStep];
        const isCorrect = q.options[this.selectedOptionIndex].isCorrect;

        this.answers.push({
            difficulty: q.difficulty,
            isCorrect: isCorrect,
            explanation: q.explanation
        });

        if (isCorrect) {
            sounds.playSuccess();
        } else {
            sounds.playError();
        }

        this.currentStep++;

        if (this.currentStep < this.questions.length) {
            this.renderQuestion();
        } else {
            this.showResults();
        }
    }

    showResults() {
        const basicOk = this.answers[0]?.isCorrect ?? false;
        const mediumOk = this.answers[1]?.isCorrect ?? false;
        const highOk = this.answers[2]?.isCorrect ?? false;

        let recommendation = '';
        let badgeColor = '';
        let targetNode = 'node-precalc';
        let mascotMessage = '';

        if (!basicOk) {
            // Fundamental weak
            recommendation = `
                <div class="diag-result-card warning">
                    <div class="result-icon">🛡️</div>
                    <div class="result-body">
                        <h4>Fondasi Fundamental Perlu Diperkuat</h4>
                        <p>Kamu melakukan kesalahan pada soal tingkat <strong>Dasar</strong>. Tenang! Sistem kami telah memprogram jalur khusus <strong>Precalculus Bridge</strong> agar kamu tidak ketinggalan saat masuk materi turunan lanjut.</p>
                        <span class="rec-path-pill">Rute Wajib: Precalculus Bridge (Aljabar & Fungsi)</span>
                    </div>
                </div>
            `;
            targetNode = 'node-precalc';
            mascotMessage = "Jangan khawatir! Kita mulai dari fondasi Precalculus dulu ya, biar makin mantap!";
            mascot.setMood('comfort');
            sounds.playFanfare();
        } else if (basicOk && !highOk) {
            // Fundamental good, high level failed
            recommendation = `
                <div class="diag-result-card ready">
                    <div class="result-icon">🚀</div>
                    <div class="result-body">
                        <h4>Fondasi Aljabar Sangat Aman!</h4>
                        <p>Dasar aljabarmu sudah kokoh! Kamu siap melompat langsung ke <strong>Kalkulus 1 (Konsep Limit & Dasar Turunan)</strong> tanpa harus mengulang materi prasyarat.</p>
                        <span class="rec-path-pill">Rute Terbuka: Calculus 1: Limit & Derivative</span>
                    </div>
                </div>
            `;
            targetNode = 'node-limit';
            mascotMessage = "Hebat! Fondasi dasarmu sangat siap. Langsung gas ke materi Limit & Turunan!";
            mascot.setMood('celebrate');
            sounds.playFanfare();
            triggerConfetti();
        } else {
            // All correct
            recommendation = `
                <div class="diag-result-card mastery">
                    <div class="result-icon">👑</div>
                    <div class="result-body">
                        <h4>Tingkat Penguasaan Tinggi (Advanced Candidate)!</h4>
                        <p>Skormu sempurna di seluruh tingkatan! Seluruh rute fundamental telah terbuka, dan kamu bisa langsung menantang modul <strong>Aplikasi Turunan & Masalah Optimasi</strong>.</p>
                        <span class="rec-path-pill">Rute Akselerasi: Advanced Optimization & Boss Quest</span>
                    </div>
                </div>
            `;
            targetNode = 'node-chain';
            mascotMessage = "Luar biasa! Kamu punya bakat kalkulus yang tajam! Siap jadi juara kelas!";
            mascot.setMood('celebrate');
            sounds.playFanfare();
            triggerConfetti();
        }

        gameState.state.diagnosticCompleted = true;
        gameState.state.activeNode = targetNode;
        gameState.addXP(40);
        gameState.saveState();

        // Progressive backend synchronization
        try {
            fetch('/api/diagnostic/submit/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    faculty: gameState.state.faculty,
                    answers: this.answers.map(a => ({ difficulty: a.difficulty, is_correct: a.isCorrect }))
                })
            }).catch(e => console.debug("Offline/Local mode:", e));
        } catch (e) {
            console.debug("Backend sync skipped:", e);
        }

        const container = document.getElementById('diag-quiz-content');
        if (container) {
            container.innerHTML = `
                <div class="diag-summary-container">
                    <div class="diag-trophy-header">
                        <span class="trophy-sparkle">✨</span>
                        <h3>Evaluasi Diagnostik Selesai!</h3>
                        <p class="subtitle">Hasil analisis algoritma adaptif Calculus Bridge untuk jalurmu:</p>
                    </div>

                    ${recommendation}

                    <div class="diag-breakdown-table">
                        <h5>Rincian Evaluasi Soal:</h5>
                        ${this.answers.map((ans, idx) => `
                            <div class="breakdown-row ${ans.isCorrect ? 'row-correct' : 'row-incorrect'}">
                                <span class="breakdown-status">${ans.isCorrect ? '✅ Benar' : '❌ Salah'}</span>
                                <span class="breakdown-name">Soal ${idx + 1} (${this.questions[idx].level})</span>
                                <p class="breakdown-expl">${ans.explanation}</p>
                            </div>
                        `).join('')}
                    </div>

                    <div class="diag-final-action">
                        <button class="btn btn-primary btn-3d btn-lg" onclick="diagnosticRunner.closeAndFocusTree('${targetNode}')">
                            Masuk ke Peta Belajar Sekarang 🚀
                        </button>
                    </div>
                </div>
            `;
        }

        mascot.say(mascotMessage);
    }

    closeAndFocusTree(targetNodeId) {
        if (this.modal) {
            this.modal.classList.remove('active');
        }
        sounds.playClick();

        // Scroll smoothly to skill tree
        const treeSection = document.getElementById('skill-tree-section');
        if (treeSection) {
            treeSection.scrollIntoView({ behavior: 'smooth' });
        }

        // Highlight recommended node
        setTimeout(() => {
            const nodeEl = document.getElementById(targetNodeId);
            if (nodeEl) {
                nodeEl.classList.add('node-pulse-highlight');
                setTimeout(() => nodeEl.classList.remove('node-pulse-highlight'), 2000);
            }
        }, 600);
    }

    close() {
        if (this.modal) {
            this.modal.classList.remove('active');
        }
    }
}

const diagnosticRunner = new DiagnosticRunner();

// ==========================================
// 5. SKILL TREE & LEARNING DRAWER ENGINE
// ==========================================
const LEVEL_DATA = {
    'node-precalc': {
        title: "Tahap 1: Precalculus Bridge",
        badge: "Fondasi Aljabar",
        subtitle: "Menyegarkan pemfaktoran, pecahan aljabar, dan fungsi sebelum masuk kalkulus.",
        summary: `
            <div class="lesson-summary-box">
                <h4>Mengapa Precalculus Penting?</h4>
                <p>90% kesalahan mahasiswa baru dalam kalkulus bukan pada rumus turunannya, melainkan pada <strong>kegagalan memanipulasi aljabar dasar</strong> dan pemfaktoran.</p>
                <div class="formula-card">
                    <h5>Rumus Cepat Selisih Kuadrat & Kubik:</h5>
                    <div class="formula-line">a² - b² = (a - b)(a + b)</div>
                    <div class="formula-line">a³ - b³ = (a - b)(a² + ab + b²)</div>
                </div>
                <div class="video-mock-card">
                    <div class="video-mock-play">▶</div>
                    <div class="video-mock-info">
                        <strong>Video Modul: Rahasia Aljabar Mahasiswa Baru UI</strong>
                        <span>Durasi: 08:45 • Pembicara: Dosen Pengampu Kalkulus</span>
                    </div>
                </div>
            </div>
        `,
        quiz: [
            {
                q: "Berapakah hasil pemfaktoran dari ekspresi x² - 16?",
                options: [
                    { t: "(x - 4)(x + 4)", ok: true },
                    { t: "(x - 8)(x + 2)", ok: false },
                    { t: "(x - 4)²", ok: false },
                    { t: "x(x - 16)", ok: false }
                ],
                explanation: "Sesuai rumus selisih kuadrat a² - b² = (a - b)(a + b) dengan a=x dan b=4."
            },
            {
                q: "Jika f(x) = 2x + 1, berapakah nilai dari f(x + h) - f(x)?",
                options: [
                    { t: "2h", ok: true },
                    { t: "2x + 2h", ok: false },
                    { t: "h", ok: false },
                    { t: "2h + 1", ok: false }
                ],
                explanation: "f(x + h) = 2(x + h) + 1 = 2x + 2h + 1. Dikurangi f(x) = 2x + 1 menghasilkan 2h."
            }
        ]
    },
    'node-limit': {
        title: "Tahap 2: Limit & Kekontinuan",
        badge: "Konsep Intuitif",
        subtitle: "Memahami batas pendekatan nilai fungsi saat mendekati titik kritis.",
        summary: `
            <div class="lesson-summary-box">
                <h4>Intuisi Limit: "Mendekati tapi Tak Harus Menyentuh"</h4>
                <p>Limit f(x) saat x mendekati c adalah nilai L yang dituju oleh f(x) saat x bergerak sangat dekat ke c dari sisi kiri maupun kanan.</p>
                <div class="formula-card">
                    <h5>Sifat Limit Utama:</h5>
                    <div class="formula-line">lim [f(x) ± g(x)] = lim f(x) ± lim g(x)</div>
                    <div class="formula-line">lim [sin(x) / x] saat x → 0 = 1</div>
                </div>
                <div class="interactive-slope-preview">
                    <p>💡 <em>Tips Trik Ujian:</em> Jika ketemu bentuk 0/0, coba 3 strategi berurutan: <strong>Faktorkan</strong>, <strong>Kalikan Sekawan</strong>, atau <strong>Aturan L'Hopital</strong>.</p>
                </div>
            </div>
        `,
        quiz: [
            {
                q: "Berapakah nilai dari lim_{x → 3} (x² - 9) / (x - 3)?",
                options: [
                    { t: "6", ok: true },
                    { t: "0", ok: false },
                    { t: "3", ok: false },
                    { t: "Tidak terdefinisi", ok: false }
                ],
                explanation: "Faktorkan (x - 3)(x + 3) / (x - 3) = x + 3. Substitusi x = 3 menghasilkan 6."
            },
            {
                q: "Kapan suatu fungsi f(x) dikatakan kontinu di titik x = c?",
                options: [
                    { t: "f(c) terdefinisi, lim_{x→c} f(x) ada, dan nilainya sama", ok: true },
                    { t: "Cukup jika grafiknya lurus", ok: false },
                    { t: "Hanya jika f(c) > 0", ok: false },
                    { t: "Jika turunan keduanya nol", ok: false }
                ],
                explanation: "Definisi syarat kontinuitas adalah: (1) f(c) ada, (2) limit di c ada, dan (3) nilai limit sama dengan f(c)."
            }
        ]
    },
    'node-deriv': {
        title: "Tahap 3: Dasar Turunan & Garis Singgung",
        badge: "Kalkulus 1",
        subtitle: "Memahami laju perubahan sesaat, kemiringan tangen, dan aturan pangkat.",
        summary: `
            <div class="lesson-summary-box">
                <h4>Definisi Turunan sebagai Limit Garis Sekan</h4>
                <p>Kemiringan garis singgung di titik x diperoleh dengan membawa dua titik pada kurva sedekat mungkin (h → 0).</p>
                <div class="formula-card">
                    <h5>Aturan Pangkat (Power Rule):</h5>
                    <div class="formula-line">d/dx [xⁿ] = n · xⁿ⁻¹</div>
                    <div class="formula-line">d/dx [c · f(x)] = c · f'(x)</div>
                </div>
            </div>
        `,
        quiz: [
            {
                q: "Tentukan turunan dari f(x) = 5x⁴ - 3x² + 7.",
                options: [
                    { t: "20x³ - 6x", ok: true },
                    { t: "20x⁴ - 6x²", ok: false },
                    { t: "5x³ - 3x", ok: false },
                    { t: "20x³ - 6x + 7", ok: false }
                ],
                explanation: "d/dx(5x⁴) = 20x³, d/dx(-3x²) = -6x, dan turunan konstanta 7 adalah 0."
            }
        ]
    },
    'node-chain': {
        title: "Tahap 4: Aturan Rantai & Implisit",
        badge: "Advanced Chain Rule",
        subtitle: "Menurunkan fungsi bersarang/komposisi yang sering keluar di ujian.",
        summary: `
            <div class="lesson-summary-box">
                <h4>Aturan Rantai: Kupas Kulit Buah</h4>
                <p>Turunkan fungsi terluar terlebih dahulu dengan membiarkan fungsi dalam tetap, lalu kalikan dengan turunan fungsi dalamnya.</p>
                <div class="formula-card">
                    <div class="formula-line">d/dx [f(g(x))] = f'(g(x)) · g'(x)</div>
                </div>
            </div>
        `,
        quiz: [
            {
                q: "Jika y = sin(3x²), maka dy/dx adalah...",
                options: [
                    { t: "6x · cos(3x²)", ok: true },
                    { t: "cos(3x²)", ok: false },
                    { t: "6x · sin(3x²)", ok: false },
                    { t: "3x² · cos(6x)", ok: false }
                ],
                explanation: "Turunan terluar sin(u) adalah cos(u). Turunan u = 3x² adalah 6x. Hasilnya 6x · cos(3x²)."
            }
        ]
    },
    'node-app': {
        title: "Tahap 5: Aplikasi Turunan & Optimasi",
        badge: "Real-world Engineering",
        subtitle: "Mencari nilai maksimum, minimum, laju terkait, dan desain efisien.",
        summary: `
            <div class="lesson-summary-box">
                <h4>Titik Stasioner & Uji Turunan</h4>
                <p>Titik kritis terjadi ketika f'(x) = 0 atau tidak ada. Uji turunan kedua menentukan kecekungan kurva (f''(x) > 0 minimum lokal, f''(x) < 0 maksimum lokal).</p>
            </div>
        `,
        quiz: [
            {
                q: "Tentukan nilai x yang meminimumkan biaya C(x) = 2x² - 8x + 50.",
                options: [
                    { t: "x = 2", ok: true },
                    { t: "x = 4", ok: false },
                    { t: "x = -2", ok: false },
                    { t: "x = 0", ok: false }
                ],
                explanation: "C'(x) = 4x - 8 = 0 ⟹ 4x = 8 ⟹ x = 2. C''(2) = 4 > 0 (konfirmasi minimum)."
            }
        ]
    }
};

class LevelDrawerManager {
    constructor() {
        this.drawerEl = document.getElementById('level-drawer');
        this.currentNodeId = null;
        this.currentQuizIdx = 0;
        this.selectedAnswerIdx = null;
    }

    openNode(nodeId) {
        const data = LEVEL_DATA[nodeId];
        if (!data) return;

        this.currentNodeId = nodeId;
        this.currentQuizIdx = 0;
        this.selectedAnswerIdx = null;

        sounds.playClick();
        mascot.setMood('wave', `Selamat datang di <strong>${data.title}</strong>! Pelajari materi dulu sebelum kuis.`);

        // Populate drawer header & content
        document.getElementById('drawer-level-badge').textContent = data.badge;
        document.getElementById('drawer-level-title').textContent = data.title;
        document.getElementById('drawer-level-subtitle').textContent = data.subtitle;

        // Populate summary tab
        document.getElementById('drawer-summary-content').innerHTML = data.summary;

        // Switch to Summary Tab first
        this.switchTab('summary');

        // Open drawer
        if (this.drawerEl) {
            this.drawerEl.classList.add('active');
        }
    }

    switchTab(tabName) {
        sounds.playClick();
        const tabBtns = document.querySelectorAll('.drawer-tab-btn');
        tabBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        const tabSummary = document.getElementById('tab-content-summary');
        const tabQuiz = document.getElementById('tab-content-quiz');

        if (tabName === 'summary') {
            if (tabSummary) tabSummary.style.display = 'block';
            if (tabQuiz) tabQuiz.style.display = 'none';
        } else {
            if (tabSummary) tabSummary.style.display = 'none';
            if (tabQuiz) tabQuiz.style.display = 'block';
            this.renderQuizQuestion();
        }
    }

    renderQuizQuestion() {
        const data = LEVEL_DATA[this.currentNodeId];
        if (!data || !data.quiz) return;

        const quizBox = document.getElementById('drawer-quiz-content');
        const feedbackBar = document.getElementById('quiz-feedback-bar');
        if (feedbackBar) feedbackBar.className = 'quiz-feedback-bar'; // hide

        const q = data.quiz[this.currentQuizIdx];
        if (!q) {
            this.showQuizComplete();
            return;
        }

        this.selectedAnswerIdx = null;

        quizBox.innerHTML = `
            <div class="quiz-question-card">
                <div class="quiz-q-num">Pertanyaan ${this.currentQuizIdx + 1} dari ${data.quiz.length}</div>
                <h4 class="quiz-q-prompt">${q.q}</h4>
                <div class="quiz-options-list">
                    ${q.options.map((opt, idx) => `
                        <button class="quiz-opt-item" onclick="levelDrawer.selectQuizAnswer(${idx})">
                            <span class="opt-indicator">${String.fromCharCode(65 + idx)}</span>
                            <span class="opt-label">${opt.t}</span>
                        </button>
                    `).join('')}
                </div>
                <div class="quiz-control-row">
                    <button class="btn btn-primary btn-3d" id="btn-check-quiz" disabled onclick="levelDrawer.verifyQuizAnswer()">
                        Periksa Jawaban
                    </button>
                </div>
            </div>
        `;
    }

    selectQuizAnswer(idx) {
        sounds.playClick();
        this.selectedAnswerIdx = idx;

        const items = document.querySelectorAll('.quiz-opt-item');
        items.forEach((item, i) => {
            item.classList.toggle('selected', i === idx);
        });

        const checkBtn = document.getElementById('btn-check-quiz');
        if (checkBtn) checkBtn.removeAttribute('disabled');
    }

    verifyQuizAnswer() {
        if (this.selectedAnswerIdx === null) return;

        const data = LEVEL_DATA[this.currentNodeId];
        const q = data.quiz[this.currentQuizIdx];
        const opt = q.options[this.selectedAnswerIdx];
        const isCorrect = opt.ok;

        const feedbackBar = document.getElementById('quiz-feedback-bar');
        const feedbackText = document.getElementById('feedback-text');
        const feedbackExpl = document.getElementById('feedback-explanation');
        const feedbackBtn = document.getElementById('btn-feedback-action');

        if (isCorrect) {
            sounds.playSuccess();
            gameState.addXP(20);
            mascot.setMood('celebrate', "Benar sekali! Keren banget penalaranmu! 🎉");

            feedbackBar.className = 'quiz-feedback-bar active success';
            feedbackText.innerHTML = "🎉 Jawabanmu Tepat! <strong>+20 XP</strong>";
            feedbackExpl.innerHTML = `<strong>Langkah Penyelesaian:</strong> ${q.explanation}`;
            feedbackBtn.textContent = "Lanjut Soal Berikutnya ➔";
            feedbackBtn.onclick = () => {
                this.currentQuizIdx++;
                this.renderQuizQuestion();
            };
        } else {
            sounds.playError();
            gameState.deductHeart();
            mascot.setMood('comfort', "Jangan sedih, perhatikan pembahasannya di bawah ya!");

            feedbackBar.className = 'quiz-feedback-bar active error';
            feedbackText.innerHTML = "❌ Jawaban Belum Tepat (-1 Nyawa)";
            feedbackExpl.innerHTML = `<strong>Langkah Pembahasan:</strong> ${q.explanation}`;
            feedbackBtn.textContent = "Coba Pahami & Lanjut ➔";
            feedbackBtn.onclick = () => {
                this.currentQuizIdx++;
                this.renderQuizQuestion();
            };
        }
    }

    showQuizComplete() {
        const quizBox = document.getElementById('drawer-quiz-content');
        const feedbackBar = document.getElementById('quiz-feedback-bar');
        if (feedbackBar) feedbackBar.className = 'quiz-feedback-bar';

        sounds.playFanfare();
        triggerConfetti();

        // Unlock next node in tree
        const nodeSequence = ['node-precalc', 'node-limit', 'node-deriv', 'node-chain', 'node-app'];
        const curIdx = nodeSequence.indexOf(this.currentNodeId);
        const nextNodeId = curIdx >= 0 && curIdx < nodeSequence.length - 1 ? nodeSequence[curIdx + 1] : null;

        gameState.completeNode(this.currentNodeId, nextNodeId);
        updateTreeUI();

        mascot.setMood('celebrate', "Hore! Kamu berhasil menyelesaikan kuis level ini! Level berikutnya sudah terbuka!");

        quizBox.innerHTML = `
            <div class="level-complete-card">
                <div class="trophy-bounce">🏆</div>
                <h3>Level Selesai!</h3>
                <p>Kamu telah menguasai kompetensi dasar untuk level ini dan mendapatkan <strong>+50 Bonus XP</strong>!</p>
                <div class="level-complete-actions">
                    <button class="btn btn-primary btn-3d" onclick="levelDrawer.close()">
                        Kembali ke Peta Belajar 🗺️
                    </button>
                </div>
            </div>
        `;
    }

    close() {
        if (this.drawerEl) {
            this.drawerEl.classList.remove('active');
        }
        sounds.playClick();
    }
}

const levelDrawer = new LevelDrawerManager();

// ==========================================
// 6. TREE UI & DOM EVENT BINDINGS
// ==========================================
function updateTreeUI() {
    const nodes = document.querySelectorAll('.tree-node-item');
    nodes.forEach(node => {
        const id = node.id;
        const isCompleted = gameState.state.completedNodes.includes(id);
        const isActive = gameState.state.activeNode === id;

        node.classList.remove('node-completed', 'node-active', 'node-locked');

        if (isCompleted) {
            node.classList.add('node-completed');
            const icon = node.querySelector('.node-icon');
            if (icon) icon.textContent = '✓';
        } else if (isActive) {
            node.classList.add('node-active');
        } else {
            node.classList.add('node-locked');
        }
    });

    gameState.updateHUD();
}

function handleNodeClick(nodeId) {
    const isCompleted = gameState.state.completedNodes.includes(nodeId);
    const isActive = gameState.state.activeNode === nodeId;

    if (isCompleted || isActive) {
        levelDrawer.openNode(nodeId);
    } else {
        sounds.playError();
        mascot.setMood('comfort', "Level ini masih terkunci! Selesaikan level sebelumnya untuk membukanya.");
        const nodeEl = document.getElementById(nodeId);
        if (nodeEl) {
            nodeEl.classList.add('shake-anim');
            setTimeout(() => nodeEl.classList.remove('shake-anim'), 500);
        }
    }
}

function selectFacultyPath(facultyKey) {
    sounds.playClick();
    gameState.setFaculty(facultyKey);

    const cards = document.querySelectorAll('.faculty-card');
    cards.forEach(c => {
        c.classList.toggle('active', c.dataset.faculty === facultyKey);
    });

    const messages = {
        'ft': "Fakultas Teknik dipilih! Fokusmu: Laju Terkait, Optimasi Struktur, & Vektor praktis.",
        'fasilkom': "Fasilkom dipilih! Fokusmu: Gradien Komputasi AI, Logika Matematika, & Kompleksitas Algoritma.",
        'fmipa': "FMIPA dipilih! Fokusmu: Ketatnya Limit Epsilon-Delta, Teorema Nilai Rata-rata, & Bukti Analitis."
    };

    mascot.setMood('wave', messages[facultyKey] || "Jalur fakultas berhasil diperbarui!");
}

function toggleSound() {
    const enabled = sounds.toggle();
    gameState.state.soundEnabled = enabled;
    gameState.saveState();
    if (enabled) sounds.playClick();
}

// ==========================================
// 7. CONFETTI PARTICLE SYSTEM
// ==========================================
function triggerConfetti() {
    const canvas = document.getElementById('confetti-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    const colors = ['#58cc02', '#22c55e', '#6366f1', '#f59e0b', '#ec4899', '#38bdf8'];

    for (let i = 0; i < 90; i++) {
        particles.push({
            x: canvas.width / 2,
            y: canvas.height / 2 + 50,
            r: Math.random() * 6 + 4,
            d: Math.random() * 90,
            color: colors[Math.floor(Math.random() * colors.length)],
            vx: (Math.random() - 0.5) * 14,
            vy: (Math.random() - 0.9) * 16,
            tilt: Math.random() * 10 - 10,
            tiltAngleIncremental: (Math.random() * 0.07) + 0.05,
            tiltAngle: 0
        });
    }

    let animationId;
    let frames = 0;

    function render() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        frames++;

        particles.forEach(p => {
            p.tiltAngle += p.tiltAngleIncremental;
            p.y += (Math.cos(p.d) + 3 + p.r / 2) / 2;
            p.x += Math.sin(p.d);
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.35; // gravity

            ctx.beginPath();
            ctx.lineWidth = p.r / 2;
            ctx.strokeStyle = p.color;
            ctx.moveTo(p.x + p.tilt + (p.r / 4), p.y);
            ctx.lineTo(p.x + p.tilt, p.y + p.tilt + (p.r / 4));
            ctx.stroke();
        });

        if (frames < 120) {
            animationId = requestAnimationFrame(render);
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            cancelAnimationFrame(animationId);
        }
    }

    render();
}

// Window resize handler for confetti canvas
window.addEventListener('resize', () => {
    const canvas = document.getElementById('confetti-canvas');
    if (canvas) {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
});

// Initial boot
document.addEventListener('DOMContentLoaded', () => {
    gameState.updateHUD();
    updateTreeUI();

    // Select existing faculty card in UI
    const activeFac = gameState.state.faculty;
    const cards = document.querySelectorAll('.faculty-card');
    cards.forEach(c => {
        c.classList.toggle('active', c.dataset.faculty === activeFac);
    });

    // Make mascot reactive to clicks
    const mascotClickArea = document.getElementById('mascot-click-trigger');
    if (mascotClickArea) {
        mascotClickArea.addEventListener('click', () => {
            mascot.randomQuote();
        });
    }
});

