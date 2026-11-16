let daLuuLogsJson = '';
const TOOL_COLORS = [
    { id: "random_line", ten: "Ngẫu nhiên dòng", hex: "rainbow" },
    { id: "random_msg", ten: "Ngẫu nhiên tin", hex: "dice" },
    { id: "#DB342E", ten: "Đỏ rực", hex: "#DB342E" },
    { id: "#15A85F", ten: "Xanh lá", hex: "#15A85F" },
    { id: "#F27806", ten: "Cam tươi", hex: "#F27806" },
    { id: "#F7B503", ten: "Vàng chanh", hex: "#F7B503" },
    { id: "#FFFFFF", ten: "Trắng tinh", hex: "#FFFFFF" },
    { id: "#000000", ten: "Đen huyền", hex: "#000000" }
];

const ICONS = {
    "shield-check": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>`,
    "user": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
    "lock": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>`,
    "eye": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`,
    "eye-off": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>`,
    "arrow-right": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" x2="19" y1="12" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>`,
    "zap": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`,
    "menu": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>`,
    "plus": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="5" y2="19"/><line x1="5" x2="19" y1="12" y2="12"/></svg>`,
    "plus-circle": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="16"/><line x1="8" x2="16" y1="12" y2="12"/></svg>`,
    "check": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
    "check-circle-2": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>`,
    "qr-code": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="5" height="5" x="3" y="3" rx="1"/><rect width="5" height="5" x="16" y="3" rx="1"/><rect width="5" height="5" x="3" y="16" rx="1"/><path d="M21 16h-3a2 2 0 0 0-2 2v3"/><path d="M21 21v.01"/><path d="M12 7v3a2 2 0 0 1-2 2H7"/><path d="M3 12h.01"/><path d="M12 3h.01"/><path d="M12 16v.01"/><path d="M16 12h1"/><path d="M21 12v.01"/><path d="M12 21v-1"/></svg>`,
    "edit-3": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>`,
    "rotate-cw": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>`,
    "refresh-cw": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>`,
    "play": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"/></svg>`,
    "square": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/></svg>`,
    "layers": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>`,
    "layout-grid": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>`,
    "users": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
    "user-check": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><polyline points="16 11 18 13 22 9"/></svg>`,
    "sliders": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="4" y1="21" y2="14"/><line x1="4" x2="4" y1="10" y2="3"/><line x1="12" x2="12" y1="21" y2="12"/><line x1="12" x2="12" y1="8" y2="3"/><line x1="20" x2="20" y1="21" y2="16"/><line x1="20" x2="20" y1="12" y2="3"/><line x1="1" x2="7" y1="14" y2="14"/><line x1="9" x2="15" y1="8" y2="8"/><line x1="17" x2="23" y1="16" y2="16"/></svg>`,
    "file-text": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/></svg>`,
    "info": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>`,
    "alert-triangle": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>`,
    "x": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>`,
    "arrow-left": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" x2="5" y1="12" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>`,
    "arrow-up-right": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" x2="17" y1="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>`,
    "log-out": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>`,
    "headset": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-5a9 9 0 0 1 18 0v5a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/></svg>`,
    "copy": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>`,
    "copy-check": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 15 2 2 4-4"/><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>`,
    "send": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" x2="11" y1="2" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>`,
    "message-circle": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/></svg>`,
    "gamepad-2": `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" x2="10" y1="12" y2="12"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="15" x2="15.01" y1="13" y2="13"/><line x1="18" x2="18.01" y1="11" y2="11"/><rect width="20" height="12" x="2" y="6" rx="6"/></svg>`
};

function capNhatIcons() {
    try {
        if (typeof lucide !== "undefined" && lucide && typeof lucide.createIcons === "function") {
            lucide.createIcons();
        }
    } catch(e) {}
    document.querySelectorAll("[data-lucide]").forEach(el => {
        const name = el.getAttribute("data-lucide");
        if (name && ICONS[name] && !el.querySelector("svg")) {
            const w = el.style.width || "18px";
            const h = el.style.height || "18px";
            el.innerHTML = ICONS[name];
            const svg = el.querySelector("svg");
            if (svg) {
                svg.style.width = w;
                svg.style.height = h;
                svg.style.display = "inline-block";
                svg.style.verticalAlign = "middle";
            }
        }
    });
}

let maToken = localStorage.getItem("zalo_web_token") || null;
let tenNguoiDung = localStorage.getItem("zalo_web_user") || "";
let cheDoAuth = "login";
let chuKyPolling = null;
let currentEditingTabId = null;
let currentTabConfig = null;
let cheDoNhapAcc = "manual";
let qrSessions = {};
let qrPollingTimer = null;
let currentQRIndex = 0;

window.onload = function() {
    capNhatIcons();
    khoiTao3DParticles();
    if (maToken) {
        kiemTraPhienTuDong();
    } else {
        hienThiAuth();
    }
};

async function kiemTraPhienTuDong() {
    try {
        const res = await fetch("/api/me", {
            headers: { "Authorization": "Bearer " + maToken }
        });
        const data = await res.json();
        if (data.success && data.user) {
            tenNguoiDung = data.user.username || tenNguoiDung;
            localStorage.setItem("zalo_web_user", tenNguoiDung);
            hienThiAppChinh();
            return;
        }
    } catch(e) {}
    hienThiAppChinh();
}

function khoiTao3DParticles() {
    const canvas = document.getElementById("canvas3dBg");
    if (!canvas || typeof THREE === "undefined") return;
    if (window.innerWidth < 768) {
        canvas.style.display = "none";
        return;
    }
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 110;
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: false, powerPreference: "low-power" });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(1);
    const pCount = 75;
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(pCount * 3);
    const cols = new Float32Array(pCount * 3);
    const c1 = new THREE.Color(0x00F0FF);
    const c2 = new THREE.Color(0x0084FF);
    for (let i = 0; i < pCount; i++) {
        pos[i * 3] = (Math.random() - 0.5) * 320;
        pos[i * 3 + 1] = (Math.random() - 0.5) * 280;
        pos[i * 3 + 2] = (Math.random() - 0.5) * 220;
        const picked = i % 2 === 0 ? c1 : c2;
        cols[i * 3] = picked.r;
        cols[i * 3 + 1] = picked.g;
        cols[i * 3 + 2] = picked.b;
    }
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(cols, 3));
    const mat = new THREE.PointsMaterial({
        size: 2.2,
        vertexColors: true,
        transparent: true,
        opacity: 0.55
    });
    const pts = new THREE.Points(geo, mat);
    scene.add(pts);
    let isHidden = false;
    document.addEventListener("visibilitychange", () => {
        isHidden = document.hidden;
    });
    function render() {
        requestAnimationFrame(render);
        if (isHidden) return;
        pts.rotation.y += 0.0004;
        pts.rotation.x += 0.0002;
        renderer.render(scene, camera);
    }
    render();
    window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

function hienThiThongBaoGlass(tieuDe, noiDung, loai = "info") {
    const modal = document.getElementById("glassModalAlert");
    if (!modal) {
        alert(noiDung);
        return;
    }
    const titleEl = document.getElementById("glassModalTitle");
    const msgEl = document.getElementById("glassModalMessage");
    const iconEl = document.getElementById("glassModalIcon");
    if (titleEl) titleEl.textContent = tieuDe || "Thông Báo Hệ Thống";
    if (msgEl) msgEl.textContent = noiDung || "";
    if (iconEl) {
        iconEl.className = "glass-modal-icon " + loai;
        let iconName = "info";
        if (loai === "error") iconName = "alert-triangle";
        else if (loai === "success") iconName = "check-circle-2";
        iconEl.innerHTML = `<i data-lucide="${iconName}" style="width: 28px; height: 28px;"></i>`;
    }
    modal.classList.add("show");
    modal.style.setProperty("display", "flex", "important");
    capNhatIcons();
}

function dongGlassModal() {
    const modal = document.getElementById("glassModalAlert");
    if (modal) {
        modal.classList.remove("show");
        modal.style.setProperty("display", "none", "important");
    }
}

function anHienMatKhau() {
    const input = document.getElementById("authPassword");
    const icon = document.getElementById("authEyeIcon");
    if (!input || !icon) return;
    if (input.type === "password") {
        input.type = "text";
        icon.setAttribute("data-lucide", "eye-off");
    } else {
        input.type = "password";
        icon.setAttribute("data-lucide", "eye");
    }
    capNhatIcons();
}

function chuyenCheDoAuth(mode) {
    cheDoAuth = mode;
    const tabLogin = document.getElementById("tabBtnLogin");
    const tabReg = document.getElementById("tabBtnRegister");
    const title = document.getElementById("authTitle");
    const btnText = document.getElementById("btnAuthText");
    const notice = document.getElementById("authNotice");
    if (mode === "login") {
        if (tabLogin) tabLogin.classList.add("active");
        if (tabReg) tabReg.classList.remove("active");
        if (title) title.textContent = "Đăng Nhập Quản Trị";
        if (btnText) btnText.textContent = "ĐĂNG NHẬP";
        if (notice) notice.innerHTML = 'Chưa có tài khoản? <a href="javascript:void(0)" onclick="chuyenCheDoAuth(\'register\')">Đăng ký mới ngay</a>';
    } else {
        if (tabReg) tabReg.classList.add("active");
        if (tabLogin) tabLogin.classList.remove("active");
        if (title) title.textContent = "Tạo Tài Khoản Mới";
        if (btnText) btnText.textContent = "ĐĂNG KÝ NGAY";
        if (notice) notice.innerHTML = 'Đã có tài khoản? <a href="javascript:void(0)" onclick="chuyenCheDoAuth(\'login\')">Đăng nhập ngay</a>';
    }
    capNhatIcons();
}

function hienThiAuth() {
    const backdrop = document.getElementById("authBackdrop");
    const main = document.getElementById("mainDashboard");
    if (backdrop) {
        backdrop.classList.remove("hidden");
        backdrop.style.setProperty("display", "flex", "important");
    }
    if (main) main.style.display = "none";
    chuyenCheDoAuth("login");
    capNhatIcons();
}

function hienThiAppChinh() {
    const backdrop = document.getElementById("authBackdrop");
    const main = document.getElementById("mainDashboard");
    if (backdrop) {
        backdrop.classList.add("hidden");
        backdrop.style.setProperty("display", "none", "important");
    }
    if (main) main.style.display = "block";
    const userSpan = document.getElementById("welcomeUsername");
    if (userSpan && tenNguoiDung) {
        userSpan.textContent = tenNguoiDung;
    }
    chuyenTrang('quan-ly-tab');
    taiDanhSachTabs();
    capNhatIcons();
}

async function xuLyXacThuc(e) {
    e.preventDefault();
    const u = document.getElementById("authUsername").value.trim();
    const p = document.getElementById("authPassword").value.trim();
    if (!u || !p) {
        hienThiThongBaoGlass("Thiếu Thông Tin", "Vui lòng nhập đầy đủ tên tài khoản và mật khẩu!", "error");
        return;
    }
    const endpoint = cheDoAuth === "login" ? "/api/login" : "/api/register";
    try {
        const res = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: u, password: p })
        });
        const data = await res.json();
        if (res.ok && data.success) {
            maToken = data.token;
            tenNguoiDung = data.username;
            localStorage.setItem("zalo_web_token", maToken);
            localStorage.setItem("zalo_web_user", tenNguoiDung);
            hienThiAppChinh();
            hienThiThongBaoGlass("Thành Công", data.message || (cheDoAuth === "login" ? "Đăng nhập thành công!" : "Đăng ký thành công!"), "success");
        } else {
            const loi = data.message || data.detail || (cheDoAuth === "login" ? "Tài khoản hoặc mật khẩu không chính xác!" : "Đăng ký tài khoản thất bại!");
            hienThiThongBaoGlass("Xác Thực Thất Bại", loi, "error");
        }
    } catch(err) {
        hienThiThongBaoGlass("Lỗi Kết Nối", "Không thể kết nối máy chủ: " + err, "error");
    }
}

async function xuLyDangXuat() {
    try {
        if (maToken) {
            await fetch("/api/logout", {
                method: "POST",
                headers: { "Authorization": "Bearer " + maToken }
            });
        }
    } catch(e) {}
    localStorage.removeItem("zalo_web_token");
    localStorage.removeItem("zalo_web_user");
    maToken = null;
    tenNguoiDung = "";
    dongMenu3Gach();
    hienThiAuth();
}

function moMenu3Gach() {
    const menu = document.getElementById("drawerMenu");
    const overlay = document.getElementById("drawerOverlay");
    if (menu) menu.classList.add("open");
    if (overlay) overlay.classList.add("open");
}

function dongMenu3Gach() {
    const menu = document.getElementById("drawerMenu");
    const overlay = document.getElementById("drawerOverlay");
    if (menu) menu.classList.remove("open");
    if (overlay) overlay.classList.remove("open");
}

function chuyenTrang(trang) {
    dongMenu3Gach();
    const vQuanLy = document.getElementById("viewQuanLyTab");
    const vTaoTab = document.getElementById("viewTaoTab");
    const vLienHe = document.getElementById("viewLienHe");
    const vChiTiet = document.getElementById("viewChiTietTab");
    if (vQuanLy) vQuanLy.style.display = "none";
    if (vTaoTab) vTaoTab.style.display = "none";
    if (vLienHe) vLienHe.style.display = "none";
    if (vChiTiet) vChiTiet.style.display = "none";
    document.querySelectorAll(".drawer-nav-item").forEach(el => el.classList.remove("active"));
    if (trang === "quan-ly-tab") {
        if (vQuanLy) vQuanLy.style.display = "block";
        document.getElementById("menuItemQuanLyTab")?.classList.add("active");
        taiDanhSachTabs();
    } else if (trang === "tao-tab") {
        if (vTaoTab) vTaoTab.style.display = "block";
        document.getElementById("menuItemTaoTab")?.classList.add("active");
        const inName = document.getElementById("inputTenTabMoi");
        if (inName) { inName.value = ""; inName.focus(); }
    } else if (trang === "lien-he") {
        if (vLienHe) vLienHe.style.display = "block";
        document.getElementById("menuItemLienHe")?.classList.add("active");
    } else if (trang === "chi-tiet-tab") {
        if (vChiTiet) vChiTiet.style.display = "block";
    }
    capNhatIcons();
}

function saoChepDiscord(text) {
    navigator.clipboard.writeText(text).then(() => {
        hienThiThongBaoGlass("Đã Sao Chép", "Đã sao chép Discord ID: " + text, "success");
    }).catch(() => {
        hienThiThongBaoGlass("Discord ID", text, "info");
    });
}

function luuBackupTabsCucBo(tabs) {
    if (!tabs || !Array.isArray(tabs)) return;
    try {
        localStorage.setItem("zalo_permanent_tabs_backup", JSON.stringify(tabs));
    } catch(e) {}
}

function layBackupTabsCucBo() {
    try {
        const raw = localStorage.getItem("zalo_permanent_tabs_backup");
        if (raw) return JSON.parse(raw);
    } catch(e) {}
    return [];
}

async function taiDanhSachTabs() {
    if (!maToken) return;
    try {
        const res = await fetch("/api/tabs", {
            headers: { "Authorization": "Bearer " + maToken }
        });
        const data = await res.json();
        if (data.success) {
            let tabs = data.tabs || [];
            if (tabs.length === 0) {
                const localTabs = layBackupTabsCucBo();
                if (localTabs.length > 0) {
                    await fetch("/api/tabs/sync", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": "Bearer " + maToken
                        },
                        body: JSON.stringify({ tabs: localTabs })
                    });
                    const resSync = await fetch("/api/tabs", {
                        headers: { "Authorization": "Bearer " + maToken }
                    });
                    const dataSync = await resSync.json();
                    if (dataSync.success && dataSync.tabs) {
                        tabs = dataSync.tabs;
                    }
                }
            }
            luuBackupTabsCucBo(tabs);
            renderDanhSachTabsNgang(tabs);
        }
    } catch(e) {
        const localTabs = layBackupTabsCucBo();
        if (localTabs.length > 0) {
            renderDanhSachTabsNgang(localTabs);
        }
    }
}

function renderDanhSachTabsNgang(tabs) {
    const container = document.getElementById("vungDanhSachTabsNgang");
    if (!container) return;
    if (!tabs || tabs.length === 0) {
        container.innerHTML = `
        <div class="card-3d" style="text-align: center; padding: 48px 20px;">
            <div class="auth-icon-badge" style="margin: 0 auto 16px; background: rgba(255,255,255,0.06); box-shadow: none;">
                <i data-lucide="layers" style="width: 26px; height: 26px; color: var(--text-muted);"></i>
            </div>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 6px;">Chưa có tab treo nào</h3>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 20px;">Tạo tab mới ngay để thiết lập treo tin tự động đa tài khoản 24/7!</p>
            <button class="btn-glow btn-primary" onclick="chuyenTrang('tao-tab')">
                <i data-lucide="plus" style="width: 16px; height: 16px;"></i> Tạo Tab Đầu Tiên
            </button>
        </div>
        `;
        capNhatIcons();
        return;
    }

    let html = "";
    tabs.forEach(tab => {
        const isRunning = tab.is_running;
        const statusClass = isRunning ? "running" : "stopped";
        const statusText = isRunning ? "ĐANG CHẠY" : "ĐÃ DỪNG";
        const iconName = isRunning ? "play" : "square";
        const runtime = tab.runtime_formatted || "00:00:00";
        const sent = tab.total_sent || 0;
        const failed = tab.total_failed || 0;
        const accCount = tab.acc_count || (tab.config?.accounts?.length || 1);
        const groupName = tab.target_group_name || tab.config?.group_name || tab.config?.group_id || "Chưa chọn";

        html += `
        <div class="tab-horizontal-card ${statusClass}">
            <div class="tab-info-left">
                <div class="tab-status-icon">
                    <i data-lucide="${iconName}" style="width: 20px; height: 20px;"></i>
                </div>
                <div class="tab-details">
                    <div class="tab-name-title">${escapeHtml(tab.name)}</div>
                    <div class="tab-meta-pills">
                        <span class="tab-meta-pill" style="color: ${isRunning ? 'var(--neon-emerald)' : 'var(--neon-red)'}; border-color: ${isRunning ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'};">
                            ● ${statusText}
                        </span>
                        <span class="tab-meta-pill">⏱ ${runtime}</span>
                        <span class="tab-meta-pill">👥 ${accCount} Acc</span>
                        <span class="tab-meta-pill">🎯 ${escapeHtml(groupName)}</span>
                        <span class="tab-meta-pill">🚀 Đã gửi: ${sent} | ❌ ${failed}</span>
                    </div>
                </div>
            </div>
            <div class="tab-actions-right">
                <button class="btn-glow btn-primary" onclick="moChiTietTab('${tab.id}')">
                    <i data-lucide="sliders" style="width: 15px; height: 15px;"></i> Cấu hình
                </button>
                ${isRunning ? `
                <button class="btn-glow btn-danger" onclick="dungNhanhTab('${tab.id}')">
                    <i data-lucide="square" style="width: 15px; height: 15px;"></i> Dừng
                </button>
                ` : `
                <button class="btn-glow btn-outline" style="color: #f87171; border-color: rgba(239, 68, 68, 0.35);" onclick="xoaTab('${tab.id}')">
                    <i data-lucide="x" style="width: 15px; height: 15px;"></i> Xóa
                </button>
                `}
            </div>
        </div>
        `;
    });

    container.innerHTML = html;
    capNhatIcons();
}

async function xuLyTaoTabMoi(e) {
    e.preventDefault();
    const input = document.getElementById("inputTenTabMoi");
    const name = input ? input.value.trim() : "";
    if (!name) {
        hienThiThongBaoGlass("Thiếu Tên Tab", "Vui lòng nhập tên cho tab mới!", "error");
        return;
    }
    try {
        const res = await fetch("/api/tabs/create", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + maToken
            },
            body: JSON.stringify({ name: name })
        });
        const data = await res.json();
        if (data.success) {
            hienThiThongBaoGlass("Tạo Thành Công", `Tab [${name}] đã được tạo thành công!`, "success");
            chuyenTrang('quan-ly-tab');
            taiDanhSachTabs();
        } else {
            hienThiThongBaoGlass("Lỗi Tạo Tab", data.message || "Không thể tạo tab mới", "error");
        }
    } catch(err) {
        hienThiThongBaoGlass("Lỗi Tạo Tab", "Không thể kết nối máy chủ: " + err, "error");
    }
}

async function dungNhanhTab(tabId) {
    try {
        await fetch(`/api/tabs/${tabId}/stop`, {
            method: "POST",
            headers: { "Authorization": "Bearer " + maToken }
        });
        taiDanhSachTabs();
    } catch(e) {}
}

async function xoaTab(tabId) {
    if (!confirm("Sếp có chắc chắn muốn xóa tab này không?")) return;
    try {
        const res = await fetch(`/api/tabs/${tabId}`, {
            method: "DELETE",
            headers: { "Authorization": "Bearer " + maToken }
        });
        const data = await res.json();
        if (data.success) {
            taiDanhSachTabs();
        } else {
            hienThiThongBaoGlass("Lỗi Xóa Tab", data.message || "Không thể xóa tab này", "error");
        }
    } catch(e) {}
}

async function moChiTietTab(tabId) {
    currentEditingTabId = tabId;
    try {
        const res = await fetch(`/api/tabs/${tabId}`, {
            headers: { "Authorization": "Bearer " + maToken }
        });
        const data = await res.json();
        if (data.success && data.tab) {
            currentTabConfig = data.tab.config || {};
            document.getElementById("lblDangXemTabName").textContent = data.tab.name;
            chuyenTrang('chi-tiet-tab');
            renderBangMauTab();
            napDuLieuVaoTabForm(data.tab, data.status);
        }
    } catch(e) {
        hienThiThongBaoGlass("Lỗi Mở Tab", "Không thể tải chi tiết tab: " + e, "error");
    }
}

function napDuLieuVaoTabForm(tab, status) {
    const cfg = tab.config || {};
    const accs = cfg.accounts && cfg.accounts.length > 0 ? cfg.accounts : [{ imei: "", cookie: "" }];
    document.getElementById("inputTabSoLuongAcc").value = accs.length;
    renderTabFormAccs(accs);
    renderTabFormAccsQR(accs);
    const selectNhom = document.getElementById("selectTabNhomZalo");
    if (cfg.group_id) {
        selectNhom.innerHTML = `<option value="${cfg.group_id}">${cfg.group_name || ('Nhóm ' + cfg.group_id)}</option>`;
    } else {
        selectNhom.innerHTML = `<option value="">-- Bấm "Lấy danh sách nhóm từ Acc #1" trước --</option>`;
    }
    document.getElementById("inputTabManualGroupId").value = cfg.group_id || "";
    document.getElementById("textareaTabNoiDungNgon").value = cfg.message_text || "";
    document.getElementById("inputTabDelay").value = cfg.delay || 5;
    document.getElementById("inputTabFontSize").value = cfg.font_size || 500;
    const mode = cfg.color_mode || "random_line";
    const hex = cfg.chosen_color || "#DB342E";
    chonMauTab(mode, hex);
    capNhatStatusTabUI(status);
}

function thayDoiSoLuongAcc() {
    renderTabFormAccs();
    renderTabFormAccsQR();
}

function chuyenCheDoNhapAcc(mode) {
    cheDoNhapAcc = mode;
    const btnManual = document.getElementById("btnModeManual");
    const btnQR = document.getElementById("btnModeQR");
    const wrapManual = document.getElementById("vungTabDanhSachAccsManual");
    const wrapQR = document.getElementById("vungTabDanhSachAccsQR");
    if (btnManual && btnQR && wrapManual && wrapQR) {
        if (mode === "manual") {
            btnManual.classList.add("active");
            btnQR.classList.remove("active");
            wrapManual.style.display = "block";
            wrapQR.style.display = "none";
        } else {
            btnQR.classList.add("active");
            btnManual.classList.remove("active");
            wrapManual.style.display = "none";
            wrapQR.style.display = "block";
            renderTabFormAccsQR();
        }
    }
    capNhatIcons();
}

function renderTabFormAccs(presetAccs) {
    const count = parseInt(document.getElementById("inputTabSoLuongAcc").value) || 1;
    const container = document.getElementById("vungTabDanhSachAccs");
    let html = "";
    for (let i = 0; i < count; i++) {
        const accData = (presetAccs && presetAccs[i]) ? presetAccs[i] : null;
        const imeiVal = accData ? (accData.imei || "") : (document.getElementById(`tab_acc_imei_${i}`)?.value || "");
        const cookieVal = accData ? (accData.cookie || "") : (document.getElementById(`tab_acc_cookie_${i}`)?.value || "");
        const groupIdVal = accData ? (accData.group_id || "") : (document.getElementById(`tab_acc_group_id_${i}`)?.value || "");
        const groupNameVal = accData ? (accData.group_name || "") : (document.getElementById(`tab_acc_group_name_${i}`)?.value || "");
        html += `
        <div class="acc-config-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #60a5fa; display: flex; align-items: center; gap: 6px;">
                    <i data-lucide="user-check" style="width: 16px; height: 16px;"></i>
                    Tài khoản #${i + 1}
                </div>
                ${i === 0 ? `
                <button type="button" class="btn-glow btn-outline" style="padding: 3px 8px; font-size: 0.72rem; color: var(--neon-cyan); border-color: rgba(0, 240, 255, 0.35);" onclick="dongBoNhomChoTatCaAcc()" title="Sao chép nhóm của Acc #1 cho tất cả các Acc còn lại">
                    ⚡ Dùng nhóm này cho tất cả Acc
                </button>
                ` : ''}
            </div>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <div class="form-row" style="margin-bottom: 0;">
                    <label>IMEI Acc #${i + 1}:</label>
                    <input type="text" id="tab_acc_imei_${i}" value="${escapeHtml(imeiVal)}" placeholder="IMEI Acc #${i + 1}..." required>
                </div>
                <div class="form-row" style="margin-bottom: 0;">
                    <label>Cookie Acc #${i + 1} (JSON hoặc chuỗi token zpw_sek):</label>
                    <textarea id="tab_acc_cookie_${i}" style="min-height: 52px; font-size: 0.8rem;" placeholder='Dán Cookie hoặc token zpw_sek...' required>${escapeHtml(cookieVal)}</textarea>
                </div>
                <div class="acc-group-box">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 0.75rem; font-weight: 600; color: var(--neon-cyan);">Nhóm riêng Acc #${i + 1}:</span>
                        <button type="button" class="btn-glow btn-outline" style="padding: 2px 6px; font-size: 0.7rem;" onclick="tabLayDanhSachNhomTheoAcc(${i})">
                            <i data-lucide="rotate-cw" style="width: 11px; height: 11px;"></i> Lấy nhóm Acc này
                        </button>
                    </div>
                    <select id="tab_acc_select_group_${i}" onchange="doiNhomAcc(${i}, this.value)" style="margin-bottom: 6px; font-size: 0.82rem; padding: 8px 12px;">
                        ${groupIdVal ? `<option value="${groupIdVal}">${groupNameVal || ('Nhóm ' + groupIdVal)}</option>` : '<option value="">-- Mặc định dùng nhóm chung ở Bước 2 --</option>'}
                    </select>
                    <input type="text" id="tab_acc_group_id_${i}" value="${escapeHtml(groupIdVal)}" placeholder="Hoặc tự gõ ID nhóm riêng cho Acc #${i + 1}..." oninput="nhapTayNhomAcc(${i}, this.value)" style="font-size: 0.82rem; padding: 8px 12px;">
                    <input type="hidden" id="tab_acc_group_name_${i}" value="${escapeHtml(groupNameVal)}">
                </div>
            </div>
        </div>
        `;
    }
    container.innerHTML = html;
    capNhatIcons();
}

function renderTabFormAccsQR(presetAccs) {
    const count = parseInt(document.getElementById("inputTabSoLuongAcc").value) || 1;
    const container = document.getElementById("vungTabDanhSachAccsQRList");
    if (!container) return;
    if (presetAccs && Array.isArray(presetAccs)) {
        presetAccs.forEach((a, idx) => {
            if (a && a.cookie) {
                qrSessions[idx] = {
                    status: "confirmed",
                    credentials: {
                        imei: a.imei || "",
                        cookie: a.cookie || "",
                        name: "Acc #" + (idx + 1)
                    }
                };
            }
        });
    }

    let html = "";
    for (let i = 0; i < count; i++) {
        const cookieInput = document.getElementById("tab_acc_cookie_" + i);
        const cookieVal = cookieInput ? cookieInput.value.trim() : "";
        const sess = qrSessions[i];
        const isLogged = (sess && sess.status === "confirmed") || (cookieVal.length > 10);
        const name = (sess && sess.credentials && sess.credentials.name) ? sess.credentials.name : (isLogged ? "Đã có Cookie" : "Chưa đăng nhập");
        const badgeClass = isLogged ? "badge-logged" : "badge-unlogged";
        const badgeText = isLogged ? ("✅ Đã đăng nhập: " + escapeHtml(name)) : "⚪ Chưa quét mã QR";

        html += `
        <div class="qr-acc-card">
            <div class="qr-acc-header-info">
                <div class="qr-acc-title">
                    <i data-lucide="user" style="width: 16px; height: 16px; color: var(--neon-cyan);"></i>
                    <span>Acc ${i + 1} :</span>
                </div>
                <div class="qr-acc-badge ${badgeClass}" id="qrBadge_${i}">
                    ${badgeText}
                </div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                <button type="button" class="btn-glow ${isLogged ? 'btn-outline' : 'btn-primary'} btn-xem-ma" onclick="moModalXemMaQR(${i})">
                    <i data-lucide="qr-code" style="width: 15px; height: 15px;"></i>
                    ${isLogged ? 'Đổi mã' : 'Xem mã'}
                </button>
                ${isLogged ? `
                <button type="button" class="btn-glow btn-outline" style="padding: 6px 12px; font-size: 0.78rem; display: flex; align-items: center; gap: 4px;" onclick="tabLayDanhSachNhomTheoAcc(${i})">
                    <i data-lucide="rotate-cw" style="width: 13px; height: 13px;"></i> Lấy nhóm
                </button>
                ` : ''}
            </div>
        </div>
        `;
    }
    container.innerHTML = html;
    capNhatIcons();
}

async function moModalXemMaQR(accIndex) {
    currentQRIndex = accIndex;
    const modal = document.getElementById("modalQRContainer");
    if (!modal) return;
    modal.classList.add("show");
    modal.style.setProperty("display", "flex", "important");
    document.getElementById("modalQRTitle").innerHTML = '<i data-lucide="qr-code" style="color: var(--neon-cyan);"></i> Mã QR Đăng Nhập - Acc #' + (accIndex + 1);
    document.getElementById("qrLoadingSpinner").style.setProperty("display", "flex", "important");
    document.getElementById("qrImageWrapper").style.setProperty("display", "none", "important");
    document.getElementById("lblTrangThaiQR").innerText = "⏳ Đang kết nối máy chủ Zalo tạo mã QR...";
    document.getElementById("lblTrangThaiQR").style.color = "var(--neon-cyan)";
    capNhatIcons();

    if (qrPollingTimer) {
        clearInterval(qrPollingTimer);
        qrPollingTimer = null;
    }

    try {
        const res = await fetch("/api/qr/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ acc_index: accIndex })
        });
        const data = await res.json();
        if (!res.ok || data.status !== "ok") {
            throw new Error(data.detail || "Không thể tạo mã QR Zalo");
        }

        const sessionInfo = data.data;
        qrSessions[accIndex] = {
            session_id: sessionInfo.session_id,
            image: sessionInfo.image,
            code: sessionInfo.code,
            status: "waiting-scan"
        };

        const imgEl = document.getElementById("imgMaQRZalo");
        if (imgEl) imgEl.src = sessionInfo.image;
        document.getElementById("qrLoadingSpinner").style.setProperty("display", "none", "important");
        document.getElementById("qrImageWrapper").style.setProperty("display", "block", "important");
        document.getElementById("lblTrangThaiQR").innerText = "📱 Mở Zalo trên điện thoại quét mã này";
        batDauPollQR(sessionInfo.session_id, accIndex);
    } catch (err) {
        document.getElementById("qrLoadingSpinner").style.setProperty("display", "none", "important");
        document.getElementById("lblTrangThaiQR").innerText = "❌ Lỗi: " + err.message;
        document.getElementById("lblTrangThaiQR").style.color = "#f87171";
    }
}

function batDauPollQR(sessionId, accIndex) {
    if (qrPollingTimer) {
        clearInterval(qrPollingTimer);
        qrPollingTimer = null;
    }
    let elapsed = 0;
    qrPollingTimer = setInterval(async () => {
        elapsed += 1.5;
        const remaining = Math.max(0, Math.floor(120 - elapsed));
        const demNguocEl = document.getElementById("lblDemNguocQR");
        if (demNguocEl) {
            demNguocEl.innerText = "Mã tự động làm mới sau " + remaining + "s";
        }
        if (remaining <= 0) {
            clearInterval(qrPollingTimer);
            qrPollingTimer = null;
            document.getElementById("lblTrangThaiQR").innerText = "⚠️ Mã QR đã hết hạn!";
            document.getElementById("lblTrangThaiQR").style.color = "#fbbf24";
            return;
        }

        try {
            const res = await fetch("/api/qr/status/" + sessionId);
            const data = await res.json();
            if (data.status === "ok" && data.data) {
                const s = data.data;
                if (s.status === "scanned") {
                    document.getElementById("lblTrangThaiQR").innerText = "⏳ Đã quét! Vui lòng bấm 'Đăng nhập' trên điện thoại...";
                    document.getElementById("lblTrangThaiQR").style.color = "#38bdf8";
                } else if (s.status === "confirmed") {
                    clearInterval(qrPollingTimer);
                    qrPollingTimer = null;
                    const creds = s.credentials || {};
                    qrSessions[accIndex] = {
                        status: "confirmed",
                        credentials: creds
                    };
                    const imeiInput = document.getElementById("tab_acc_imei_" + accIndex);
                    const cookieInput = document.getElementById("tab_acc_cookie_" + accIndex);
                    if (imeiInput && creds.imei) imeiInput.value = creds.imei;
                    if (cookieInput && creds.cookie) cookieInput.value = creds.cookie;

                    const userName = creds.name || "Zalo User";
                    document.getElementById("lblTrangThaiQR").innerText = "🎉 Đăng nhập thành công: " + userName + "!";
                    document.getElementById("lblTrangThaiQR").style.color = "#34d399";

                    renderTabFormAccsQR();
                    setTimeout(() => {
                        dongModalXemMaQR();
                        hienThiThongBaoGlass("Đăng Nhập Thành Công", "Acc #" + (accIndex + 1) + " (" + userName + ") đã kết nối!", "success");
                        if (accIndex === 0) {
                            setTimeout(() => tabLayDanhSachNhomTheoAcc(0), 400);
                        }
                    }, 1400);
                } else if (s.status === "expired") {
                    clearInterval(qrPollingTimer);
                    qrPollingTimer = null;
                    document.getElementById("lblTrangThaiQR").innerText = "⚠️ Mã QR đã hết hạn hoặc bị hủy!";
                    document.getElementById("lblTrangThaiQR").style.color = "#fbbf24";
                }
            }
        } catch (e) {}
    }, 1500);
}

function lamMoiMaQRHienTai() {
    moModalXemMaQR(currentQRIndex);
}

function dongModalXemMaQR() {
    if (qrPollingTimer) {
        clearInterval(qrPollingTimer);
        qrPollingTimer = null;
    }
    const modal = document.getElementById("modalQRContainer");
    if (modal) {
        modal.classList.remove("show");
        modal.style.setProperty("display", "none", "important");
    }
}

async function tabLayDanhSachNhomTheoAcc(idx) {
    let imei = document.getElementById(`tab_acc_imei_${idx}`)?.value.trim() || "";
    let cookie = document.getElementById(`tab_acc_cookie_${idx}`)?.value.trim() || "";
    if ((!imei || !cookie) && qrSessions[idx] && qrSessions[idx].credentials) {
        if (!imei && qrSessions[idx].credentials.imei) imei = qrSessions[idx].credentials.imei;
        if (!cookie && qrSessions[idx].credentials.cookie) cookie = qrSessions[idx].credentials.cookie;
    }
    if (!imei || !cookie) {
        hienThiThongBaoGlass("Thiếu Thông Tin Acc", `Vui lòng quét mã QR hoặc nhập IMEI/Cookie cho Tài khoản #${idx + 1} trước!`, "error");
        return;
    }
    hienThiThongBaoGlass("Đang Lấy Nhóm", `Đang kết nối API Zalo để quét danh sách nhóm của Acc #${idx + 1}...`, "info");
    try {
        const res = await fetch("/api/get-groups", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + maToken
            },
            body: JSON.stringify({ imei: imei, cookie: cookie })
        });
        const data = await res.json();
        if (data.success && data.groups && data.groups.length > 0) {
            let opts = `<option value="">-- Chọn nhóm từ Acc #${idx + 1} (${data.groups.length} nhóm) --</option>`;
            data.groups.forEach(g => {
                opts += `<option value="${g.id}">${escapeHtml(g.name)} (${g.id})</option>`;
            });
            const selAcc = document.getElementById(`tab_acc_select_group_${idx}`);
            if (selAcc) selAcc.innerHTML = opts;
            if (idx === 0) {
                const selChung = document.getElementById("selectTabNhomZalo");
                if (selChung) selChung.innerHTML = opts;
            }
            hienThiThongBaoGlass("Lấy Nhóm Thành Công", `Tìm thấy ${data.groups.length} nhóm Zalo từ Acc #${idx + 1}!`, "success");
        } else {
            hienThiThongBaoGlass("Không Tìm Thấy Nhóm", data.message || "Không tìm thấy nhóm nào hoặc Cookie hết hạn", "error");
        }
    } catch(err) {
        hienThiThongBaoGlass("Lỗi Kết Nối", "Không thể lấy danh sách nhóm: " + err, "error");
    }
}

function doiNhomAcc(idx, val) {
    const gidInp = document.getElementById(`tab_acc_group_id_${idx}`);
    if (gidInp) gidInp.value = val;
    const sel = document.getElementById(`tab_acc_select_group_${idx}`);
    const gName = sel?.options[sel.selectedIndex]?.text || ("Nhóm " + val);
    const nameInp = document.getElementById(`tab_acc_group_name_${idx}`);
    if (nameInp) nameInp.value = gName;
}

function nhapTayNhomAcc(idx, val) {
    const nameInp = document.getElementById(`tab_acc_group_name_${idx}`);
    if (nameInp) nameInp.value = val ? ("Nhóm " + val) : "";
}

function dongBoNhomChoTatCaAcc() {
    const gid0 = document.getElementById("tab_acc_group_id_0")?.value.trim() || document.getElementById("inputTabManualGroupId")?.value.trim();
    const gname0 = document.getElementById("tab_acc_group_name_0")?.value.trim() || "Nhóm " + gid0;
    if (!gid0) {
        hienThiThongBaoGlass("Chưa Chọn Nhóm", "Vui lòng chọn hoặc nhập ID nhóm ở Acc #1 hoặc Bước 2 trước!", "error");
        return;
    }
    const count = parseInt(document.getElementById("inputTabSoLuongAcc").value) || 1;
    for (let i = 0; i < count; i++) {
        const inp = document.getElementById(`tab_acc_group_id_${i}`);
        if (inp) inp.value = gid0;
        const nameInp = document.getElementById(`tab_acc_group_name_${i}`);
        if (nameInp) nameInp.value = gname0;
    }
    document.getElementById("inputTabManualGroupId").value = gid0;
    hienThiThongBaoGlass("Đồng Bộ Thành Công", `Đã đồng bộ nhóm [${gname0}] cho tất cả ${count} tài khoản!`, "success");
}

function doiNhomChung(val) {
    const manualChung = document.getElementById("inputTabManualGroupId");
    if (manualChung) manualChung.value = val;
    const gid0 = document.getElementById("tab_acc_group_id_0");
    if (gid0 && !gid0.value.trim()) {
        gid0.value = val;
        const selectChung = document.getElementById("selectTabNhomZalo");
        const gName = selectChung?.options[selectChung.selectedIndex]?.text || ("Nhóm " + val);
        const name0 = document.getElementById("tab_acc_group_name_0");
        if (name0) name0.value = gName;
    }
}

function nhapTayNhomChung(val) {
    const gid0 = document.getElementById("tab_acc_group_id_0");
    if (gid0 && !gid0.value.trim()) {
        gid0.value = val;
    }
}

function tabDocFileNgon(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(evt) {
        document.getElementById("textareaTabNoiDungNgon").value = evt.target.result;
        hienThiThongBaoGlass("Tải File Ngôn Thành Công", `Đã tải file: ${file.name}\nTổng cộng ${evt.target.result.split('\n').length} dòng ngôn sẵn sàng gửi!`, "success");
    };
    reader.readAsText(file, "UTF-8");
}

function renderBangMauTab() {
    const grid = document.getElementById("vungTabBangMau");
    if (!grid) return;
    let html = "";
    TOOL_COLORS.forEach((c, idx) => {
        let dot = c.hex === "rainbow"
            ? "background: linear-gradient(135deg, red, orange, yellow, green, blue, purple);"
            : (c.hex === "dice" ? "background: linear-gradient(135deg, #0084ff, #a855f7);" : `background-color: ${c.hex};`);
        html += `
        <div class="palette-item" id="tabPal_${idx}" onclick="tabChonMauClick('${c.id}', '${c.ten}', ${idx})">
            <div class="palette-circle" style="${dot}"></div>
            <span class="palette-label">${c.ten}</span>
        </div>
        `;
    });
    grid.innerHTML = html;
}

function tabChonMauClick(colorId, colorName, idx) {
    document.querySelectorAll(".palette-item").forEach(el => el.classList.remove("active"));
    const item = document.getElementById(`tabPal_${idx}`);
    if (item) item.classList.add("active");
    if (colorId === "random_line") {
        document.getElementById("tabColorMode").value = "random_line";
        document.getElementById("tabColorHex").value = "#DB342E";
        document.getElementById("lblTabMauDangChon").textContent = "Mỗi dòng 1 màu ngẫu nhiên (Rainbow)";
    } else if (colorId === "random_msg") {
        document.getElementById("tabColorMode").value = "random_msg";
        document.getElementById("tabColorHex").value = "#DB342E";
        document.getElementById("lblTabMauDangChon").textContent = "Cả tin 1 màu ngẫu nhiên mỗi lần gửi";
    } else {
        document.getElementById("tabColorMode").value = "fixed";
        document.getElementById("tabColorHex").value = colorId;
        document.getElementById("tabColorPicker").value = colorId;
        document.getElementById("lblTabMauDangChon").textContent = colorName + " (" + colorId + ")";
    }
}

function tabChonMauPicker(hex) {
    document.querySelectorAll(".palette-item").forEach(el => el.classList.remove("active"));
    document.getElementById("tabColorMode").value = "fixed";
    document.getElementById("tabColorHex").value = hex;
    document.getElementById("lblTabMauDangChon").textContent = "Tùy chỉnh (" + hex + ")";
}

function chonMauTab(mode, hex) {
    if (mode === "random_line") {
        tabChonMauClick("random_line", "Ngẫu nhiên dòng", 0);
    } else if (mode === "random_msg") {
        tabChonMauClick("random_msg", "Ngẫu nhiên tin", 1);
    } else {
        let foundIdx = TOOL_COLORS.findIndex(c => c.hex.toLowerCase() === hex.toLowerCase());
        if (foundIdx >= 0) {
            tabChonMauClick(TOOL_COLORS[foundIdx].id, TOOL_COLORS[foundIdx].ten, foundIdx);
        } else {
            tabChonMauPicker(hex);
        }
    }
}

async function tabBatDauTreo() {
    if (!currentEditingTabId) return;
    const count = parseInt(document.getElementById("inputTabSoLuongAcc").value) || 1;
    const accounts = [];
    for (let i = 0; i < count; i++) {
        let imei = document.getElementById(`tab_acc_imei_${i}`)?.value.trim() || "";
        let cookie = document.getElementById(`tab_acc_cookie_${i}`)?.value.trim() || "";
        if ((!imei || !cookie) && qrSessions[i] && qrSessions[i].credentials) {
            if (!imei && qrSessions[i].credentials.imei) imei = qrSessions[i].credentials.imei;
            if (!cookie && qrSessions[i].credentials.cookie) cookie = qrSessions[i].credentials.cookie;
        }
        const gid = document.getElementById(`tab_acc_group_id_${i}`)?.value.trim() || "";
        const gname = document.getElementById(`tab_acc_group_name_${i}`)?.value.trim() || "";
        if (!imei || !cookie) {
            hienThiThongBaoGlass("Thiếu Thông Tin Acc", `Tài khoản #${i + 1} chưa có IMEI hoặc Cookie (hãy quét mã QR hoặc nhập tay)!`, "error");
            return;
        }
        accounts.push({
            imei: imei,
            cookie: cookie,
            group_id: gid,
            group_name: gname
        });
    }

    const groupIdChung = document.getElementById("inputTabManualGroupId")?.value.trim() || document.getElementById("selectTabNhomZalo")?.value.trim();
    const selectChung = document.getElementById("selectTabNhomZalo");
    const groupNameChung = selectChung?.options[selectChung.selectedIndex]?.text || ("Nhóm " + groupIdChung);
    const messageText = document.getElementById("textareaTabNoiDungNgon")?.value.trim();
    const delay = parseInt(document.getElementById("inputTabDelay")?.value) || 5;
    const fontSize = parseInt(document.getElementById("inputTabFontSize")?.value) || 500;
    const colorMode = document.getElementById("tabColorMode")?.value || "random_line";
    const chosenColor = document.getElementById("tabColorHex")?.value || "#DB342E";

    if (!messageText) {
        hienThiThongBaoGlass("Thiếu File Ngôn", "Vui lòng nhập hoặc tải file ngôn vào ô 'Nội dung File Ngôn'!", "error");
        return;
    }

    const payload = {
        accounts: accounts,
        group_id: groupIdChung,
        group_name: groupNameChung,
        message_text: messageText,
        delay: delay,
        font_size: fontSize,
        color_mode: colorMode,
        chosen_color: chosenColor,
        ttl: 0
    };

    try {
        const res = await fetch(`/api/tabs/${currentEditingTabId}/start`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + maToken
            },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            hienThiThongBaoGlass("Bắt Đầu Thành Công", data.message || "Tab đã bắt đầu chạy!", "success");
            capNhatStatusTabUI({ is_running: true });
            batDauPolling();
        } else {
            hienThiThongBaoGlass("Lỗi Chạy Tab", data.message || "Không thể bắt đầu treo tab này", "error");
        }
    } catch(err) {
        hienThiThongBaoGlass("Lỗi Kết Nối", "Không thể gửi lệnh chạy: " + err, "error");
    }
}

async function tabDungTreo() {
    if (!currentEditingTabId) return;
    try {
        const res = await fetch(`/api/tabs/${currentEditingTabId}/stop`, {
            method: "POST",
            headers: { "Authorization": "Bearer " + maToken }
        });
        const data = await res.json();
        if (data.success) {
            hienThiThongBaoGlass("Đã Dừng", "Đã dừng tiến trình treo của tab này!", "info");
            capNhatStatusTabUI({ is_running: false });
        }
    } catch(err) {}
}

function capNhatStatusTabUI(status) {
    const isRunning = status && status.is_running;
    const btnStart = document.getElementById("btnTabStart");
    const btnStop = document.getElementById("btnTabStop");
    const badge = document.getElementById("badgeTabDangChay");
    if (isRunning) {
        if (badge) {
            badge.textContent = "ĐANG CHẠY";
            badge.style.background = "linear-gradient(135deg, #10b981 0%, #059669 100%)";
            badge.style.color = "#fff";
        }
        if (btnStart) {
            btnStart.disabled = true;
            btnStart.style.opacity = "0.5";
            btnStart.style.cursor = "not-allowed";
        }
        if (btnStop) {
            btnStop.disabled = false;
            btnStop.style.opacity = "1";
            btnStop.style.cursor = "pointer";
        }
    } else {
        if (badge) {
            badge.textContent = "ĐÃ DỪNG";
            badge.style.background = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)";
            badge.style.color = "#fff";
        }
        if (btnStart) {
            btnStart.disabled = false;
            btnStart.style.opacity = "1";
            btnStart.style.cursor = "pointer";
        }
        if (btnStop) {
            btnStop.disabled = true;
            btnStop.style.opacity = "0.5";
            btnStop.style.cursor = "not-allowed";
        }
    }
    if (status) {
        document.getElementById("lblTabTimerDisplay").textContent = status.runtime_formatted || "00:00:00";
        document.getElementById("lblTabSentDisplay").textContent = status.total_sent || 0;
        document.getElementById("lblTabFailedDisplay").textContent = status.total_failed || 0;
        document.getElementById("lblTabAccCountDisplay").textContent = status.acc_count || 0;
        if (status.logs && Array.isArray(status.logs)) {
            const logsStr = JSON.stringify(status.logs);
            if (logsStr !== daLuuLogsJson) {
                daLuuLogsJson = logsStr;
                const box = document.getElementById("tabTerminalLogs");
                if (box) {
                    let logHtml = "";
                    status.logs.forEach(l => {
                        let col = "#e2e8f0";
                        if (l.type === "success") col = "#34d399";
                        else if (l.type === "error") col = "#f87171";
                        else if (l.type === "warning") col = "#fbbf24";
                        logHtml += `<div class="log-row"><span class="log-time">[${l.time}]</span> <span style="color: ${col};">${escapeHtml(l.text)}</span></div>`;
                    });
                    box.innerHTML = logHtml;
                    box.scrollTop = box.scrollHeight;
                }
            }
        }
    }
}

function batDauPolling() {
    if (chuKyPolling) clearInterval(chuKyPolling);
    chuKyPolling = setInterval(tickRealtime, 1500);
}

async function tickRealtime() {
    const vChiTiet = document.getElementById("viewChiTietTab");
    if (!vChiTiet || vChiTiet.style.display === "none" || !currentEditingTabId || !maToken) {
        if (chuKyPolling) {
            clearInterval(chuKyPolling);
            chuKyPolling = null;
        }
        return;
    }
    try {
        const res = await fetch(`/api/tabs/${currentEditingTabId}`, {
            headers: { "Authorization": "Bearer " + maToken }
        });
        const data = await res.json();
        if (data.success && data.status) {
            capNhatStatusTabUI(data.status);
            if (!data.status.is_running && chuKyPolling) {
                clearInterval(chuKyPolling);
                chuKyPolling = null;
            }
        }
    } catch(e) {}
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}