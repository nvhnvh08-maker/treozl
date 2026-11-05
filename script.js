/**
 * ==============================================================
 * ZALO TREO TEXT PRO - MULTI-TAB JAVASCRIPT
 * Tách riêng file logic sạch sẽ, chuẩn lập trình viên thực tế
 * ==============================================================
 */

// Danh sách mã màu tool gốc dangkhiem_1.py:
// COLOR_LIST = ["#DB342E","#15A85F","#F27806","#F7B503","#FFFFFF","#000000"]
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

let maToken = localStorage.getItem("zalo_web_token") || null;
let tenNguoiDung = localStorage.getItem("zalo_web_user") || "";
let cheDoAuth = "login";
let chuKyPolling = null;

// Quản lý tab hiện tại đang mở cấu hình
let currentEditingTabId = null;
let currentTabConfig = null;

window.onload = function() {
    lucide.createIcons();
    khoiTao3DParticles();

    if (maToken) {
        hienThiAppChinh();
    } else {
        hienThiAuth();
    }
};

// ==========================================
// 1. KHỞI TẠO NỀN 3D PARTICLES BẰNG THREE.JS
// ==========================================
function khoiTao3DParticles() {
    const canvas = document.getElementById("canvas3dBg");
    if (!canvas || typeof THREE === "undefined") return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 120;

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const pCount = 650;
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(pCount * 3);
    const cols = new Float32Array(pCount * 3);

    const c1 = new THREE.Color(0x0084FF);
    const c2 = new THREE.Color(0x00F0FF);
    const c3 = new THREE.Color(0xA855F7);

    for (let i = 0; i < pCount; i++) {
        pos[i * 3] = (Math.random() - 0.5) * 350;
        pos[i * 3 + 1] = (Math.random() - 0.5) * 350;
        pos[i * 3 + 2] = (Math.random() - 0.5) * 250;

        const r = Math.random();
        const picked = r < 0.4 ? c1 : (r < 0.75 ? c2 : c3);
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
        opacity: 0.65,
        blending: THREE.AdditiveBlending
    });

    const pts = new THREE.Points(geo, mat);
    scene.add(pts);

    let mX = 0, mY = 0;
    window.addEventListener("mousemove", (e) => {
        mX = (e.clientX - window.innerWidth / 2) * 0.0005;
        mY = (e.clientY - window.innerHeight / 2) * 0.0005;
    });

    function render() {
        requestAnimationFrame(render);
        pts.rotation.y += 0.0007;
        pts.rotation.x += 0.0003;
        camera.position.x += (mX * 50 - camera.position.x) * 0.05;
        camera.position.y += (-mY * 50 - camera.position.y) * 0.05;
        camera.lookAt(scene.position);
        renderer.render(scene, camera);
    }
    render();

    window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// ==========================================
// 2. AUTHENTICATION (SQLITE DATABASE)
// ==========================================
function chuyenCheDoAuth(mode) {
    cheDoAuth = mode;
    const tabLogin = document.getElementById("tabBtnLogin");
    const tabReg = document.getElementById("tabBtnRegister");
    const title = document.getElementById("authTitle");
    const btn = document.getElementById("btnAuthSubmit");
    const notice = document.getElementById("authNotice");

    if (mode === "login") {
        tabLogin.classList.add("active");
        tabReg.classList.remove("active");
        title.textContent = "Đăng Nhập Quản Trị";
        btn.innerHTML = `<i data-lucide="log-in" style="width: 18px; height: 18px;"></i> ĐĂNG NHẬP`;
        notice.innerHTML = `💡 Sếp chưa có tài khoản? Nhấn "Đăng Ký Mới" ở trên để tạo acc ngay!`;
    } else {
        tabReg.classList.add("active");
        tabLogin.classList.remove("active");
        title.textContent = "Tạo Tài Khoản Mới";
        btn.innerHTML = `<i data-lucide="user-plus" style="width: 18px; height: 18px;"></i> ĐĂNG KÝ NGAY`;
        notice.innerHTML = `💡 Đăng ký xong hệ thống sẽ tự động đăng nhập và đưa sếp vào ngay!`;
    }
    lucide.createIcons();
}

function hienThiAuth() {
    document.getElementById("authBackdrop").style.display = "flex";
    document.getElementById("mainDashboard").style.display = "none";
    if (chuKyPolling) clearInterval(chuKyPolling);
}

function hienThiAppChinh() {
    document.getElementById("authBackdrop").style.display = "none";
    document.getElementById("mainDashboard").style.display = "block";
    document.getElementById("welcomeUsername").textContent = tenNguoiDung || "Sếp";
    lucide.createIcons();

    chuyenTrang('quan-ly-tab');
    batDauPolling();
}

async function xuLyXacThuc(e) {
    e.preventDefault();
    const user = document.getElementById("authUsername").value.trim();
    const pass = document.getElementById("authPassword").value.trim();
    const btn = document.getElementById("btnAuthSubmit");

    btn.disabled = true;
    btn.innerHTML = `<i data-lucide="loader-2" class="spin"></i> Đang xử lý...`;
    lucide.createIcons();

    const endpoint = cheDoAuth === "login" ? "/api/login" : "/api/register";
    try {
        const res = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: user, password: pass })
        });
        const data = await res.json();
        if (data.success && data.token) {
            maToken = data.token;
            tenNguoiDung = data.username;
            localStorage.setItem("zalo_web_token", maToken);
            localStorage.setItem("zalo_web_user", tenNguoiDung);
            hienThiAppChinh();
        } else {
            alert(data.message || "Xác thực thất bại");
        }
    } catch (err) {
        alert("Lỗi kết nối máy chủ: " + err);
    } finally {
        btn.disabled = false;
        chuyenCheDoAuth(cheDoAuth);
    }
}

async function xuLyDangXuat() {
    if (maToken) {
        try {
            await fetch("/api/logout", {
                method: "POST",
                headers: { "Authorization": "Bearer " + maToken }
            });
        } catch(e) {}
    }
    maToken = null;
    tenNguoiDung = "";
    localStorage.removeItem("zalo_web_token");
    localStorage.removeItem("zalo_web_user");
    dongMenu3Gach();
    hienThiAuth();
}

// ==========================================
// 3. MENU 3 GẠCH VÀ ĐIỀU HƯỚNG MÀN HÌNH
// ==========================================
function moMenu3Gach() {
    document.getElementById("drawerMenu").classList.add("open");
    document.getElementById("drawerOverlay").classList.add("show");
}

function dongMenu3Gach() {
    document.getElementById("drawerMenu").classList.remove("open");
    document.getElementById("drawerOverlay").classList.remove("show");
}

function chuyenTrang(trang) {
    dongMenu3Gach();

    document.getElementById("viewQuanLyTab").style.display = "none";
    document.getElementById("viewTaoTab").style.display = "none";
    document.getElementById("viewLienHe").style.display = "none";
    document.getElementById("viewChiTietTab").style.display = "none";

    document.querySelectorAll(".drawer-nav-item").forEach(el => el.classList.remove("active"));

    if (trang === "quan-ly-tab") {
        document.getElementById("viewQuanLyTab").style.display = "block";
        document.getElementById("menuItemQuanLyTab").classList.add("active");
        taiDanhSachTabs();
    } else if (trang === "tao-tab") {
        document.getElementById("viewTaoTab").style.display = "block";
        document.getElementById("menuItemTaoTab").classList.add("active");
        document.getElementById("inputTenTabMoi").value = "";
        document.getElementById("inputTenTabMoi").focus();
    } else if (trang === "lien-he") {
        document.getElementById("viewLienHe").style.display = "block";
        document.getElementById("menuItemLienHe").classList.add("active");
    } else if (trang === "chi-tiet-tab") {
        document.getElementById("viewChiTietTab").style.display = "block";
    }

    lucide.createIcons();
}

function saoChepDiscord(text) {
    navigator.clipboard.writeText(text);
    alert(`Đã sao chép Discord username: ${text} vào bộ nhớ tạm!`);
}

// ==============================================================
// 4. QUẢN LÝ TAB DẠNG HÌNH NGANG (FULL VIỀN XANH / ĐỎ)
// ==============================================================
async function taiDanhSachTabs() {
    if (!maToken) return;
    try {
        const res = await fetch("/api/tabs", {
            headers: { "Authorization": "Bearer " + maToken }
        });
        if (res.status === 401) {
            xuLyDangXuat();
            return;
        }
        const data = await res.json();
        if (data.success && data.tabs) {
            renderDanhSachTabsNgang(data.tabs);
        }
    } catch(e) {}
}

function renderDanhSachTabsNgang(tabs) {
    const container = document.getElementById("vungDanhSachTabsNgang");
    if (!container) return;

    if (tabs.length === 0) {
        container.innerHTML = `
            <div class="card-3d" style="text-align: center; padding: 50px 20px;">
                <i data-lucide="layers" style="width: 48px; height: 48px; color: #64748b; margin-bottom: 12px;"></i>
                <h3 style="font-size: 1.15rem; color: #fff;">Chưa có tab nào được tạo</h3>
                <p style="color: var(--text-muted); margin-top: 6px; margin-bottom: 20px;">Sếp bấm vào nút bên dưới để tạo tab mới nhé!</p>
                <button class="btn-glow btn-primary" onclick="chuyenTrang('tao-tab')">
                    <i data-lucide="plus" style="width: 16px; height: 16px;"></i>
                    Tạo Tab Mới Ngay
                </button>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    let html = "";
    tabs.forEach(t => {
        // QUY TẮC CỦA SẾP:
        // ĐANG CHẠY -> FULL VIỀN NGANG MÀU XANH LÁ (.running)
        // KHÔNG CHẠY -> FULL VIỀN NGANG MÀU ĐỎ (.stopped)
        const classVien = t.is_running ? "running" : "stopped";
        const badgeTrangThai = t.is_running 
            ? `<span style="color: #34d399; font-weight: 700; font-size: 0.8rem;">⚡ ĐANG CHẠY (${t.runtime_formatted || '00:00:00'})</span>`
            : `<span style="color: #f87171; font-weight: 700; font-size: 0.8rem;">⏹ ĐÃ DỪNG</span>`;

        const iconTrangThai = t.is_running
            ? `<i data-lucide="activity" style="width: 22px; height: 22px;"></i>`
            : `<i data-lucide="pause-circle" style="width: 22px; height: 22px;"></i>`;

        const btnBatDungNhanh = t.is_running
            ? `<button class="btn-glow btn-danger" onclick="dungNhanhTab('${t.id}')" title="Dừng tab này"><i data-lucide="square" style="width: 14px; height: 14px;"></i> Dừng</button>`
            : `<button class="btn-glow btn-success" onclick="moChiTietTab('${t.id}')" title="Chạy tab này"><i data-lucide="play" style="width: 14px; height: 14px;"></i> Chạy</button>`;

        html += `
        <div class="tab-horizontal-card ${classVien}">
            <div class="tab-info-left">
                <div class="tab-status-icon">
                    ${iconTrangThai}
                </div>
                <div>
                    <div class="tab-name-title">${escapeHtml(t.name)}</div>
                    <div class="tab-meta-desc">
                        ${badgeTrangThai}
                        <span>👥 ${t.acc_count || 1} Acc</span>
                        <span>📤 Đã gửi: <strong style="color: #fff;">${t.total_sent || 0}</strong></span>
                        <span>🎯 Nhóm: <strong style="color: #fff;">${escapeHtml(t.target_group_name || 'Chưa chọn')}</strong></span>
                    </div>
                </div>
            </div>
            <div class="tab-actions-right">
                ${btnBatDungNhanh}
                <button class="btn-glow btn-primary" onclick="moChiTietTab('${t.id}')">
                    <i data-lucide="sliders" style="width: 15px; height: 15px;"></i>
                    Cấu hình Tab
                </button>
                <button class="btn-glow btn-outline" onclick="xoaTab('${t.id}')" style="color: #f87171;" title="Xóa tab này">
                    <i data-lucide="trash-2" style="width: 15px; height: 15px;"></i>
                </button>
            </div>
        </div>
        `;
    });

    container.innerHTML = html;
    lucide.createIcons();
}

// Tạo tab mới -> Tự động chuyển qua Quản lý tab
async function xuLyTaoTabMoi(e) {
    e.preventDefault();
    const tenTab = document.getElementById("inputTenTabMoi").value.trim();
    if (!tenTab) {
        alert("Vui lòng nhập tên tab");
        return;
    }

    try {
        const res = await fetch("/api/tabs/create", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + maToken
            },
            body: JSON.stringify({ name: tenTab })
        });
        const data = await res.json();
        if (data.success) {
            alert(`Đã tạo tab "${tenTab}" thành công!`);
            // TỰ ĐỘNG CHUYỂN QUA QUẢN LÝ TAB ĐÚNG YÊU CẦU CỦA SẾP
            chuyenTrang('quan-ly-tab');
        } else {
            alert(data.message || "Lỗi tạo tab");
        }
    } catch (err) {
        alert("Lỗi kết nối: " + err);
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
            alert(data.message || "Không thể xóa tab");
        }
    } catch(e) {}
}

// ==============================================================
// 5. CẤU HÌNH & CHẠY TAB CỤ THỂ (GIAO DIỆN 3D NHƯ NÃY)
// ==============================================================
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
        alert("Lỗi khi mở tab: " + e);
    }
}

function napDuLieuVaoTabForm(tab, status) {
    const cfg = tab.config || {};
    const accs = cfg.accounts && cfg.accounts.length > 0 ? cfg.accounts : [{ imei: "", cookie: "" }];

    document.getElementById("inputTabSoLuongAcc").value = accs.length;
    renderTabFormAccs(accs);

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

            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div>
                    <label style="font-size: 0.76rem; color: var(--text-muted); margin-bottom: 3px;">IMEI:</label>
                    <input type="text" id="tab_acc_imei_${i}" value="${escapeHtml(imeiVal)}" placeholder="IMEI Acc #${i + 1}..." required>
                </div>
                <div>
                    <label style="font-size: 0.76rem; color: var(--text-muted); margin-bottom: 3px;">Cookie (JSON, chuỗi cookie hoặc token zpw_sek):</label>
                    <textarea id="tab_acc_cookie_${i}" style="min-height: 48px; font-size: 0.76rem;" placeholder='Dán Cookie hoặc token zpw_sek (VD: {"zpw_sek": "tzao..."} hoặc chuỗi cookie)...' required>${escapeHtml(cookieVal)}</textarea>
                    <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 2px;">
                        💡 <em>Lưu ý: Cookie phải còn hạn đăng nhập trên web chat.zalo.me</em>
                    </div>
                </div>

                <!-- CẤU HÌNH NHÓM RIÊNG CHO ACC NÀY -->
                <div class="acc-group-box">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 0.76rem; font-weight: 600; color: var(--neon-cyan);">🎯 Nhóm của Acc #${i + 1}:</span>
                        <button type="button" class="btn-glow btn-outline" id="btnLayNhomAcc_${i}" style="padding: 3px 8px; font-size: 0.72rem;" onclick="tabLayDanhSachNhomTheoAcc(${i})">
                            <i data-lucide="refresh-cw" style="width: 12px; height: 12px;"></i>
                            Lấy nhóm của Acc #${i + 1}
                        </button>
                    </div>
                    <select id="tab_acc_select_group_${i}" onchange="doiNhomAcc(${i})" style="margin-bottom: 6px; font-size: 0.8rem;">
                        <option value="">${groupIdVal ? (escapeHtml(groupNameVal) || ('Nhóm ' + escapeHtml(groupIdVal))) : '-- Bấm nút "Lấy nhóm" hoặc nhập ID bên dưới --'}</option>
                    </select>
                    <input type="text" id="tab_acc_group_id_${i}" value="${escapeHtml(groupIdVal)}" placeholder="ID nhóm Zalo của Acc #${i + 1}..." style="font-size: 0.8rem;" oninput="nhapTayNhomAcc(${i})">
                    <input type="hidden" id="tab_acc_group_name_${i}" value="${escapeHtml(groupNameVal)}">
                </div>
            </div>
        </div>
        `;
    }
    container.innerHTML = html;
    lucide.createIcons();
}

async function tabLayDanhSachNhomTheoAcc(accIndex) {
    const imeiEl = document.getElementById(`tab_acc_imei_${accIndex}`);
    const cookieEl = document.getElementById(`tab_acc_cookie_${accIndex}`);
    const btn = document.getElementById(`btnLayNhomAcc_${accIndex}`);
    const btnChung = (accIndex === 0) ? document.getElementById("btnTabLayNhom") : null;

    if (!imeiEl || !imeiEl.value.trim()) {
        alert(`Vui lòng nhập IMEI của Acc #${accIndex + 1}!`);
        return;
    }
    if (!cookieEl || !cookieEl.value.trim()) {
        alert(`Vui lòng nhập Cookie của Acc #${accIndex + 1}!`);
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i data-lucide="loader-2" class="spin" style="width: 12px; height: 12px;"></i> Đang tải...`;
    }
    if (btnChung) {
        btnChung.disabled = true;
        btnChung.innerHTML = `<i data-lucide="loader-2" class="spin" style="width: 15px; height: 15px;"></i> Đang tải nhóm...`;
    }
    lucide.createIcons();

    try {
        const res = await fetch("/api/get-groups", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + maToken
            },
            body: JSON.stringify({
                imei: imeiEl.value.trim(),
                cookie: cookieEl.value.trim()
            })
        });

        const data = await res.json();
        if (data.success && data.groups) {
            const selectEl = document.getElementById(`tab_acc_select_group_${accIndex}`);
            if (data.groups.length === 0) {
                if (selectEl) selectEl.innerHTML = `<option value="">Acc #${accIndex + 1} không tham gia nhóm nào</option>`;
                alert(`Acc #${accIndex + 1} không tham gia nhóm nào!`);
            } else {
                let optHtml = `<option value="">-- Chọn 1 nhóm (${data.groups.length} nhóm tìm thấy) --</option>`;
                data.groups.forEach(g => {
                    optHtml += `<option value="${escapeHtml(g.id)}" data-name="${escapeHtml(g.name)}">${escapeHtml(g.name)} (ID: ${escapeHtml(g.id)})</option>`;
                });
                if (selectEl) selectEl.innerHTML = optHtml;

                // Nếu là Acc 0, cập nhật cả select nhóm chung
                if (accIndex === 0) {
                    const selectChung = document.getElementById("selectTabNhomZalo");
                    if (selectChung) selectChung.innerHTML = optHtml;
                }

                alert(`Đã tải thành công ${data.groups.length} nhóm của Acc #${accIndex + 1}!`);
            }
        } else {
            alert(data.message || `Không thể tải nhóm của Acc #${accIndex + 1}`);
        }
    } catch(e) {
        alert("Lỗi kết nối Zalo: " + e);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i data-lucide="refresh-cw" style="width: 12px; height: 12px;"></i> Lấy nhóm của Acc #${accIndex + 1}`;
        }
        if (btnChung) {
            btnChung.disabled = false;
            btnChung.innerHTML = `<i data-lucide="refresh-cw" style="width: 15px; height: 15px;"></i> Lấy danh sách nhóm từ Acc #1`;
        }
        lucide.createIcons();
    }
}

function doiNhomAcc(accIndex) {
    const selectEl = document.getElementById(`tab_acc_select_group_${accIndex}`);
    const inputId = document.getElementById(`tab_acc_group_id_${accIndex}`);
    const inputName = document.getElementById(`tab_acc_group_name_${accIndex}`);
    if (!selectEl || !inputId) return;

    const val = selectEl.value;
    if (val) {
        inputId.value = val;
        const opt = selectEl.options[selectEl.selectedIndex];
        const gName = opt?.getAttribute("data-name") || opt?.text || ("Nhóm " + val);
        if (inputName) inputName.value = gName;

        if (accIndex === 0) {
            const manualChung = document.getElementById("inputTabManualGroupId");
            if (manualChung) manualChung.value = val;
            const selectChung = document.getElementById("selectTabNhomZalo");
            if (selectChung) selectChung.value = val;
        }
    }
}

function nhapTayNhomAcc(accIndex) {
    const inputId = document.getElementById(`tab_acc_group_id_${accIndex}`);
    const inputName = document.getElementById(`tab_acc_group_name_${accIndex}`);
    if (inputId && inputName) {
        inputName.value = "Nhóm " + inputId.value.trim();
    }
}

function dongBoNhomChoTatCaAcc() {
    const count = parseInt(document.getElementById("inputTabSoLuongAcc").value) || 1;
    const gid0 = document.getElementById("tab_acc_group_id_0")?.value.trim() || document.getElementById("inputTabManualGroupId")?.value.trim() || document.getElementById("selectTabNhomZalo")?.value.trim();
    const gname0 = document.getElementById("tab_acc_group_name_0")?.value.trim() || ("Nhóm " + gid0);

    if (!gid0) {
        alert("Vui lòng chọn hoặc nhập ID nhóm cho Acc #1 trước khi đồng bộ!");
        return;
    }

    for (let i = 1; i < count; i++) {
        const inputId = document.getElementById(`tab_acc_group_id_${i}`);
        const inputName = document.getElementById(`tab_acc_group_name_${i}`);
        const selectEl = document.getElementById(`tab_acc_select_group_${i}`);
        if (inputId) inputId.value = gid0;
        if (inputName) inputName.value = gname0;
        if (selectEl) {
            selectEl.innerHTML = `<option value="${escapeHtml(gid0)}" selected>${escapeHtml(gname0)} (ID: ${escapeHtml(gid0)})</option>`;
        }
    }
    alert(`Đã áp dụng nhóm [${gname0}] cho tất cả ${count} tài khoản!`);
}

function doiNhomChung(val) {
    const manualChung = document.getElementById("inputTabManualGroupId");
    if (manualChung) manualChung.value = val;
    // Đồng bộ sang Acc #0 nếu Acc #0 chưa có nhóm
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
        alert(`Đã tải file: ${file.name} (${evt.target.result.split('\n').length} dòng ngôn)`);
    };
    reader.readAsText(file, "UTF-8");
}

function renderBangMauTab() {
    const grid = document.getElementById("vungTabBangMau");
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
        document.getElementById("lblTabMauDangChon").textContent = `Cố định: ${colorName} (${colorId})`;
        document.getElementById("tabColorPicker").value = colorId;
    }
}

function tabChonMauPicker(hex) {
    document.querySelectorAll(".palette-item").forEach(el => el.classList.remove("active"));
    document.getElementById("tabColorMode").value = "fixed";
    document.getElementById("tabColorHex").value = hex;
    document.getElementById("lblTabMauDangChon").textContent = `Màu tùy chỉnh: ${hex}`;
}

function chonMauTab(mode, hex) {
    if (mode === "random_line") {
        tabChonMauClick("random_line", "Ngẫu nhiên dòng", 0);
    } else if (mode === "random_msg") {
        tabChonMauClick("random_msg", "Ngẫu nhiên tin", 1);
    } else {
        const foundIdx = TOOL_COLORS.findIndex(c => c.id === hex);
        if (foundIdx >= 0) {
            tabChonMauClick(hex, TOOL_COLORS[foundIdx].ten, foundIdx);
        } else {
            tabChonMauPicker(hex);
        }
    }
}

// Bắt đầu chạy Tab
async function tabBatDauTreo() {
    if (!currentEditingTabId) return;

    const count = parseInt(document.getElementById("inputTabSoLuongAcc").value) || 1;
    const accounts = [];

    // Nhóm mặc định chung (nếu có)
    let defaultGroupId = (document.getElementById("inputTabManualGroupId")?.value || "").trim() || (document.getElementById("selectTabNhomZalo")?.value || "").trim();
    let defaultGroupName = "";
    const selectChung = document.getElementById("selectTabNhomZalo");
    if (selectChung && selectChung.selectedIndex >= 0 && selectChung.options[selectChung.selectedIndex]) {
        defaultGroupName = selectChung.options[selectChung.selectedIndex].getAttribute("data-name") || selectChung.options[selectChung.selectedIndex].text;
    }
    if (!defaultGroupName && defaultGroupId) {
        defaultGroupName = "Nhóm " + defaultGroupId;
    }

    for (let i = 0; i < count; i++) {
        const imei = (document.getElementById(`tab_acc_imei_${i}`)?.value || "").trim();
        const cookie = (document.getElementById(`tab_acc_cookie_${i}`)?.value || "").trim();
        let accGid = (document.getElementById(`tab_acc_group_id_${i}`)?.value || "").trim();
        let accGname = (document.getElementById(`tab_acc_group_name_${i}`)?.value || "").trim();

        // Nếu acc này chưa chọn nhóm riêng, fallback về nhóm mặc định chung
        if (!accGid && defaultGroupId) {
            accGid = defaultGroupId;
            accGname = defaultGroupName;
        }

        if (imei && cookie) {
            accounts.push({
                imei,
                cookie,
                group_id: accGid,
                group_name: accGname || (accGid ? ("Nhóm " + accGid) : "")
            });
        }
    }

    if (accounts.length === 0) {
        alert("Vui lòng nhập đầy đủ IMEI và Cookie của ít nhất 1 tài khoản!");
        return;
    }

    // Kiểm tra xem đã có nhóm nào được chọn hay chưa
    const coNhom = accounts.some(a => Boolean(a.group_id)) || Boolean(defaultGroupId);
    if (!coNhom) {
        alert("Vui lòng chọn hoặc nhập nhóm Zalo cho các tài khoản!");
        return;
    }

    const messageText = document.getElementById("textareaTabNoiDungNgon").value.trim();
    if (!messageText) {
        alert("Vui lòng nhập nội dung ngôn hoặc bấm 'Chọn File Ngôn (.txt)'!");
        return;
    }

    const delay = parseInt(document.getElementById("inputTabDelay").value) || 5;
    const fontSize = parseInt(document.getElementById("inputTabFontSize").value) || 500;
    const colorMode = document.getElementById("tabColorMode").value;
    const chosenColor = document.getElementById("tabColorHex").value;

    const btnStart = document.getElementById("btnTabStart");
    btnStart.disabled = true;

    try {
        const res = await fetch(`/api/tabs/${currentEditingTabId}/start`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + maToken
            },
            body: JSON.stringify({
                accounts,
                group_id: defaultGroupId || accounts[0].group_id,
                group_name: defaultGroupName || accounts[0].group_name,
                message_text: messageText,
                delay,
                color_mode: colorMode,
                chosen_color: chosenColor,
                font_size: fontSize
            })
        });
        const data = await res.json();
        if (data.success) {
            alert("🚀 BẮT ĐẦU TREO TAB THÀNH CÔNG!");
        } else {
            alert(data.message || "Lỗi khởi động tab");
        }
    } catch(e) {
        alert("Lỗi kết nối: " + e);
    } finally {
        btnStart.disabled = false;
    }
}

async function tabDungTreo() {
    if (!currentEditingTabId) return;
    try {
        await fetch(`/api/tabs/${currentEditingTabId}/stop`, {
            method: "POST",
            headers: { "Authorization": "Bearer " + maToken }
        });
        alert("⏹ Đã gửi lệnh dừng tiến trình tab này.");
    } catch(e) {}
}

function capNhatStatusTabUI(st) {
    if (!st) return;
    const badge = document.getElementById("badgeTabDangChay");
    const btnStart = document.getElementById("btnTabStart");
    const btnStop = document.getElementById("btnTabStop");

    if (st.is_running) {
        badge.textContent = `ĐANG TREO (${st.runtime_formatted || '00:00:00'})`;
        badge.style.background = "rgba(16, 185, 129, 0.2)";
        badge.style.color = "#34d399";
        badge.style.border = "1px solid rgba(16, 185, 129, 0.5)";
        btnStart.disabled = true;
        btnStart.style.opacity = "0.5";
        btnStop.disabled = false;
        btnStop.style.opacity = "1";
    } else {
        badge.textContent = "ĐÃ DỪNG";
        badge.style.background = "rgba(239, 68, 68, 0.2)";
        badge.style.color = "#f87171";
        badge.style.border = "1px solid rgba(239, 68, 68, 0.4)";
        btnStart.disabled = false;
        btnStart.style.opacity = "1";
        btnStop.disabled = true;
        btnStop.style.opacity = "0.5";
    }

    document.getElementById("lblTabTimerDisplay").textContent = st.runtime_formatted || "00:00:00";
    document.getElementById("lblTabSentDisplay").textContent = st.total_sent || 0;
    document.getElementById("lblTabFailedDisplay").textContent = st.total_failed || 0;
    document.getElementById("lblTabAccCountDisplay").textContent = st.acc_count || 0;

    if (st.logs && st.logs.length > 0) {
        const term = document.getElementById("tabTerminalLogs");
        let logHtml = "";
        st.logs.forEach(l => {
            logHtml += `
            <div class="log-row">
                <span class="log-time">[${l.time}]</span>
                <span class="log-${l.level}">${escapeHtml(l.message)}</span>
            </div>
            `;
        });
        term.innerHTML = logHtml;
        term.scrollTop = term.scrollHeight;
    }
}

// ==========================================
// 6. POLLING REALTIME CẬP NHẬT TRẠNG THÁI
// ==========================================
function batDauPolling() {
    if (chuKyPolling) clearInterval(chuKyPolling);
    chuKyPolling = setInterval(tickRealtime, 1000);
    tickRealtime();
}

async function tickRealtime() {
    if (!maToken) return;

    // Cập nhật viền xanh / đỏ của Quản lý tab
    if (document.getElementById("viewQuanLyTab").style.display !== "none") {
        taiDanhSachTabs();
    }

    // Cập nhật đồng hồ và logs của tab đang mở cấu hình
    if (document.getElementById("viewChiTietTab").style.display !== "none" && currentEditingTabId) {
        try {
            const res = await fetch(`/api/tabs/${currentEditingTabId}`, {
                headers: { "Authorization": "Bearer " + maToken }
            });
            const data = await res.json();
            if (data.success && data.status) {
                capNhatStatusTabUI(data.status);
            }
        } catch(e) {}
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
