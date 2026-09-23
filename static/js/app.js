/**
 * Crypto Trading Journal - Modern Frontend Application Logic
 * Hỗ trợ Đa Người Dùng (Multi-User Authentication) & Phân quyền dữ liệu
 */

document.addEventListener("DOMContentLoaded", () => {
    // State management
    const state = {
        user: null,
        trades: [],
        stats: null,
        config: null,
        currentTab: "dashboard",
        calDate: new Date(),
        chartInstance: null,
    };

    // DOM Elements
    const elements = {
        // Auth Elements
        modalAuth: document.getElementById("modal-auth"),
        tabLoginBtn: document.getElementById("tab-login-btn"),
        tabRegisterBtn: document.getElementById("tab-register-btn"),
        formLogin: document.getElementById("form-login"),
        formRegister: document.getElementById("form-register"),
        authAlert: document.getElementById("auth-alert"),
        loginUsername: document.getElementById("login-username"),
        loginPassword: document.getElementById("login-password"),
        regUsername: document.getElementById("reg-username"),
        regPassword: document.getElementById("reg-password"),
        regDisplayName: document.getElementById("reg-display-name"),
        btnSubmitLogin: document.getElementById("btn-submit-login"),
        btnSubmitRegister: document.getElementById("btn-submit-register"),
        linkForgotPwd: document.getElementById("link-forgot-pwd"),
        linkBackLogin: document.getElementById("link-back-login"),
        formResetPwd: document.getElementById("form-reset-pwd"),
        resetUsername: document.getElementById("reset-username"),
        resetNewPassword: document.getElementById("reset-new-password"),
        btnSubmitResetPwd: document.getElementById("btn-submit-reset-pwd"),

        // User Profile Chip
        userProfileChip: document.getElementById("user-profile-chip"),
        userAvatarText: document.getElementById("user-avatar-text"),
        userDisplayName: document.getElementById("user-display-name"),
        btnLogout: document.getElementById("btn-logout"),

        // Navigation Tabs
        tabBtns: document.querySelectorAll(".nav-tab"),
        tabViews: document.querySelectorAll(".tab-content"),
        totalTradesCounter: document.getElementById("total-trades-counter"),

        // Action Buttons
        btnOpenAddTrade: document.getElementById("btn-open-add-trade"),
        btnExportCsv: document.getElementById("btn-export-csv"),
        btnRefresh: document.getElementById("btn-refresh"),
        btnEmptyAddTrade: document.getElementById("btn-empty-add-trade"),

        // Filter Elements
        filterSearch: document.getElementById("filter-search"),
        filterSymbol: document.getElementById("filter-symbol"),
        filterStatus: document.getElementById("filter-status"),
        filterResult: document.getElementById("filter-result"),
        filterStrategy: document.getElementById("filter-strategy"),
        btnResetFilters: document.getElementById("btn-reset-filters"),
        filterStatsLabel: document.getElementById("filter-stats-label"),

        // Table
        tradesTbody: document.getElementById("trades-tbody"),
        tradesEmptyState: document.getElementById("trades-empty-state"),

        // Trade Modal & Form
        modalTradeForm: document.getElementById("modal-trade-form"),
        tradeForm: document.getElementById("trade-form"),
        tradeModalTitle: document.getElementById("trade-modal-title"),
        btnCloseTradeModal: document.getElementById("btn-close-trade-modal"),
        btnCancelTrade: document.getElementById("btn-cancel-trade"),
        btnSaveTrade: document.getElementById("btn-save-trade"),
        btnSaveText: document.getElementById("btn-save-text"),

        // Form Inputs
        formTradeId: document.getElementById("form-trade-id"),
        formSymbol: document.getElementById("form-symbol"),
        typeLong: document.getElementById("type-long"),
        typeShort: document.getElementById("type-short"),
        formMarketType: document.getElementById("form-market-type"),
        formLeverage: document.getElementById("form-leverage"),
        formStatus: document.getElementById("form-status"),
        formTimeframe: document.getElementById("form-timeframe"),
        formEntryDate: document.getElementById("form-entry-date"),
        formExitDate: document.getElementById("form-exit-date"),
        formEntryPrice: document.getElementById("form-entry-price"),
        formStopLoss: document.getElementById("form-stop-loss"),
        formTakeProfit: document.getElementById("form-take-profit"),
        formExitPrice: document.getElementById("form-exit-price"),
        formPositionSize: document.getElementById("form-position-size"),
        formFees: document.getElementById("form-fees"),
        formStrategy: document.getElementById("form-strategy"),
        formEmotion: document.getElementById("form-emotion"),
        formNotes: document.getElementById("form-notes"),
        formLessons: document.getElementById("form-lessons"),
        formChartPath: document.getElementById("form-chart-path"),

        // Live calculation elements
        livePlannedRr: document.getElementById("live-planned-rr"),
        liveRealizedRr: document.getElementById("live-realized-rr"),
        livePnl: document.getElementById("live-pnl"),
        liveRoi: document.getElementById("live-roi"),

        // Dropzone & Charts
        chartDropzone: document.getElementById("chart-dropzone"),
        dropzoneIdle: document.getElementById("dropzone-idle"),
        dropzonePreview: document.getElementById("dropzone-preview"),
        previewChartImg: document.getElementById("preview-chart-img"),
        fileChartInput: document.getElementById("file-chart-input"),
        btnRemoveChart: document.getElementById("btn-remove-chart"),

        pairsDatalist: document.getElementById("pairs-datalist"),

        // Lightbox
        modalLightbox: document.getElementById("modal-lightbox"),
        lightboxImg: document.getElementById("lightbox-img"),
        btnCloseLightbox: document.getElementById("btn-close-lightbox"),

        // Calendar Elements
        calMonthTitle: document.getElementById("cal-month-title"),
        calMonthPnl: document.getElementById("cal-month-pnl"),
        calMonthWr: document.getElementById("cal-month-wr"),
        calMonthTradesCount: document.getElementById("cal-month-trades-count"),
        calendarDaysGrid: document.getElementById("calendar-days-grid"),
        btnCalPrev: document.getElementById("btn-cal-prev"),
        btnCalNext: document.getElementById("btn-cal-next"),
        btnCalToday: document.getElementById("btn-cal-today"),

        toastContainer: document.getElementById("toast-container"),
    };

    // ==========================================
    // TOAST NOTIFICATIONS
    // ==========================================
    function showToast(message, type = "info") {
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        
        let icon = "ℹ️";
        if (type === "success") icon = "✅";
        if (type === "error") icon = "❌";

        toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
        elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(40px)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // ==========================================
    // AUTHENTICATION LOGIC (LOGIN / REGISTER / LOGOUT)
    // ==========================================
    async function checkAuthStatus() {
        try {
            const res = await fetch("/api/auth/me");
            const data = await res.json();
            if (data.logged_in && data.user) {
                onUserLoggedIn(data.user);
            } else {
                showAuthModal();
            }
        } catch (err) {
            console.error("Lỗi kiểm tra auth:", err);
            showAuthModal();
        }
    }

    function showAuthModal() {
        elements.modalAuth.classList.add("active");
        elements.userProfileChip.style.display = "none";
        hideAuthAlert();
    }

    function hideAuthModal() {
        elements.modalAuth.classList.remove("active");
    }

    function showAuthAlert(msg, type = "error") {
        elements.authAlert.textContent = msg;
        elements.authAlert.className = `auth-alert auth-alert-${type}`;
        elements.authAlert.style.display = "block";
    }

    function hideAuthAlert() {
        elements.authAlert.style.display = "none";
        elements.authAlert.textContent = "";
    }

    function onUserLoggedIn(user) {
        state.user = user;
        hideAuthModal();

        // Cập nhật Profile Badge ở Header
        const firstLetter = (user.display_name || user.username || "T").charAt(0).toUpperCase();
        elements.userAvatarText.textContent = firstLetter;
        elements.userDisplayName.textContent = user.display_name || user.username;
        elements.userProfileChip.style.display = "flex";

        // Nạp dữ liệu riêng của user này
        refreshAllData();
    }

    async function handleLoginSubmit(e) {
        e.preventDefault();
        hideAuthAlert();
        const username = elements.loginUsername.value.trim();
        const password = elements.loginPassword.value;

        if (!username || !password) {
            showAuthAlert("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!");
            return;
        }

        try {
            elements.btnSubmitLogin.disabled = true;
            elements.btnSubmitLogin.textContent = "Đang xác thực...";

            const res = await fetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();

            if (!res.ok) {
                showAuthAlert(data.error || "Đăng nhập thất bại!");
                return;
            }

            showToast(`Chào mừng bạn trở lại, ${data.user.display_name || data.user.username}!`, "success");
            onUserLoggedIn(data.user);
            elements.formLogin.reset();

        } catch (err) {
            showAuthAlert("Không thể kết nối đến máy chủ. Vui lòng thử lại!");
        } finally {
            elements.btnSubmitLogin.disabled = false;
            elements.btnSubmitLogin.textContent = "Đăng Nhập Vào Nhật Ký";
        }
    }

    async function handleRegisterSubmit(e) {
        e.preventDefault();
        hideAuthAlert();
        const username = elements.regUsername.value.trim();
        const password = elements.regPassword.value;
        const displayName = elements.regDisplayName.value.trim();

        if (username.length < 3) {
            showAuthAlert("Tên đăng nhập phải có ít nhất 3 ký tự!");
            return;
        }
        if (password.length < 4) {
            showAuthAlert("Mật khẩu phải có ít nhất 4 ký tự!");
            return;
        }

        try {
            elements.btnSubmitRegister.disabled = true;
            elements.btnSubmitRegister.textContent = "Đang tạo tài khoản...";

            const res = await fetch("/api/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password, display_name: displayName })
            });
            const data = await res.json();

            if (!res.ok) {
                showAuthAlert(data.error || "Đăng ký thất bại!");
                return;
            }

            showToast(`Đăng ký tài khoản thành công! Chào mừng ${data.user.display_name}!`, "success");
            onUserLoggedIn(data.user);
            elements.formRegister.reset();

        } catch (err) {
            showAuthAlert("Lỗi kết nối máy chủ khi đăng ký!");
        } finally {
            elements.btnSubmitRegister.disabled = false;
            elements.btnSubmitRegister.textContent = "Tạo Tài Khoản Mới";
        }
    }

    async function handleLogout() {
        if (!confirm("Bạn có chắc chắn muốn đăng xuất không?")) return;
        try {
            await fetch("/api/auth/logout", { method: "POST" });
            state.user = null;
            state.trades = [];
            state.stats = null;
            showToast("Đã đăng xuất thành công!", "info");
            showAuthModal();
        } catch (err) {
            console.error("Lỗi đăng xuất:", err);
            showAuthModal();
        }
    }

    // ==========================================
    // INITIALIZATION & DATA FETCHING
    // ==========================================
    async function initApp() {
        setupEventListeners();
        await loadConfig();
        await checkAuthStatus();
    }

    async function loadConfig() {
        try {
            const res = await fetch("/api/config");
            const data = await res.json();
            state.config = data;

            elements.pairsDatalist.innerHTML = "";
            elements.filterSymbol.innerHTML = '<option value="Tất cả">Tất cả Cặp tiền</option>';
            data.pairs.forEach(pair => {
                const opt = document.createElement("option");
                opt.value = pair;
                elements.pairsDatalist.appendChild(opt);

                const filterOpt = document.createElement("option");
                filterOpt.value = pair;
                filterOpt.textContent = pair;
                elements.filterSymbol.appendChild(filterOpt);
            });

            elements.formStrategy.innerHTML = '<option value="">-- Chọn chiến lược --</option>';
            elements.filterStrategy.innerHTML = '<option value="Tất cả">Tất cả Chiến lược</option>';
            data.strategies.forEach(s => {
                const opt = document.createElement("option");
                opt.value = s;
                opt.textContent = s;
                elements.formStrategy.appendChild(opt);

                const fOpt = document.createElement("option");
                fOpt.value = s;
                fOpt.textContent = s;
                elements.filterStrategy.appendChild(fOpt);
            });

            elements.formEmotion.innerHTML = '<option value="">-- Chọn tâm lý lúc vào lệnh --</option>';
            data.emotions.forEach(e => {
                const opt = document.createElement("option");
                opt.value = e;
                opt.textContent = e;
                elements.formEmotion.appendChild(opt);
            });

        } catch (err) {
            console.error("Lỗi tải cấu hình:", err);
        }
    }

    async function refreshAllData() {
        if (!state.user) return;
        await Promise.all([loadStats(), loadTrades()]);
        if (state.currentTab === "calendar") {
            renderCalendar();
        }
    }

    // ==========================================
    // STATS & DASHBOARD VIEW
    // ==========================================
    async function loadStats() {
        try {
            const res = await fetch("/api/stats");
            if (res.status === 401) {
                showAuthModal();
                return;
            }
            const stats = await res.json();
            state.stats = stats;

            renderKpiCards(stats);
            renderEquityChart(stats.equity_curve || []);
            renderBreakdowns(stats);
        } catch (err) {
            console.error("Lỗi nạp thống kê:", err);
        }
    }

    function renderKpiCards(stats) {
        const pnlEl = document.getElementById("kpi-net-pnl");
        const pnlVal = stats.net_pnl || 0;
        pnlEl.textContent = `${pnlVal >= 0 ? "+" : ""}$${pnlVal.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        pnlEl.className = `kpi-value ${pnlVal > 0 ? "text-win" : pnlVal < 0 ? "text-loss" : "text-be"}`;
        
        document.getElementById("kpi-pnl-sub").textContent = `${stats.closed_trades_count || 0} lệnh đã hoàn tất (${stats.open_trades_count || 0} đang mở)`;

        const wrEl = document.getElementById("kpi-win-rate");
        const wrVal = stats.win_rate || 0;
        wrEl.textContent = `${wrVal.toFixed(1)}%`;
        wrEl.className = `kpi-value ${wrVal >= 50 ? "text-win" : "text-loss"}`;
        document.getElementById("kpi-wins").textContent = `${stats.win_trades || 0}W`;
        document.getElementById("kpi-losses").textContent = `${stats.loss_trades || 0}L`;
        document.getElementById("kpi-be").textContent = `${stats.breakeven_trades || 0}BE`;

        document.getElementById("kpi-profit-factor").textContent = (stats.profit_factor || 0).toFixed(2);
        document.getElementById("kpi-total-profit").textContent = `+$${(stats.total_profit || 0).toLocaleString()}`;
        document.getElementById("kpi-total-loss").textContent = `-$${(stats.total_loss || 0).toLocaleString()}`;

        document.getElementById("kpi-avg-win").textContent = `+$${(stats.avg_win || 0).toFixed(2)}`;
        document.getElementById("kpi-avg-loss").textContent = `-$${(stats.avg_loss || 0).toFixed(2)}`;
        const ratio = stats.avg_loss > 0 ? (stats.avg_win / stats.avg_loss).toFixed(1) : "N/A";
        document.getElementById("kpi-win-loss-ratio").textContent = `Tỷ lệ Lãi:Lỗ: ${ratio}x`;

        document.getElementById("kpi-avg-rr").textContent = `1 : ${(stats.avg_rr || 0).toFixed(2)}`;
        document.getElementById("kpi-max-wins").textContent = `${stats.max_consecutive_wins || 0}W`;
        document.getElementById("kpi-max-losses").textContent = `${stats.max_consecutive_losses || 0}L`;
    }

    function renderEquityChart(curveData) {
        const ctx = document.getElementById("equityChart");
        if (!ctx) return;

        let labels = [];
        let dataPoints = [];

        if (!curveData || curveData.length === 0) {
            labels = ["Bắt đầu"];
            dataPoints = [0];
        } else {
            labels = curveData.map(c => c[0]);
            dataPoints = curveData.map(c => c[1]);
        }

        if (state.chartInstance) {
            state.chartInstance.destroy();
        }

        const isPositive = dataPoints[dataPoints.length - 1] >= 0;
        const mainColor = isPositive ? "#00F59B" : "#FF4757";
        const gradientBg = ctx.getContext("2d").createLinearGradient(0, 0, 0, 300);
        gradientBg.addColorStop(0, isPositive ? "rgba(0, 245, 155, 0.25)" : "rgba(255, 71, 87, 0.25)");
        gradientBg.addColorStop(1, "rgba(13, 17, 23, 0.0)");

        state.chartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Lợi Nhuận Tích Lũy ($)",
                    data: dataPoints,
                    borderColor: mainColor,
                    borderWidth: 2.5,
                    backgroundColor: gradientBg,
                    fill: true,
                    tension: 0.35,
                    pointRadius: curveData.length > 25 ? 2 : 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: mainColor,
                    pointBorderColor: "#151A22",
                    pointBorderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: "index" },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: "#161B22",
                        titleColor: "#9BA3AF",
                        bodyColor: "#F0F6FC",
                        borderColor: "#30363D",
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: (context) => {
                                const val = context.parsed.y;
                                return `Lũy kế: ${val >= 0 ? "+" : ""}$${val.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#656E7B", font: { size: 11 } }
                    },
                    y: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: {
                            color: "#656E7B",
                            font: { size: 11 },
                            callback: (value) => `$${value}`
                        }
                    }
                }
            }
        });
    }

    function renderBreakdowns(stats) {
        // Strategy
        const stratContainer = document.getElementById("strategy-breakdown-list");
        stratContainer.innerHTML = "";
        const strats = stats.strategy_stats || {};
        const stratKeys = Object.keys(strats);

        if (stratKeys.length === 0) {
            stratContainer.innerHTML = '<div class="no-chart">Chưa có dữ liệu chiến lược</div>';
        } else {
            stratKeys.sort((a, b) => (strats[b].pnl || 0) - (strats[a].pnl || 0));
            stratKeys.forEach(name => {
                const item = strats[name];
                const pnl = item.pnl || 0;
                const wr = item.win_rate || 0;
                const el = document.createElement("div");
                el.className = "breakdown-item";
                el.innerHTML = `
                    <div class="breakdown-item-header">
                        <span class="breakdown-name">${name} (${item.count} lệnh)</span>
                        <span class="breakdown-stats ${pnl >= 0 ? 'text-win' : 'text-loss'}">
                            ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)} | WR: ${wr}%
                        </span>
                    </div>
                    <div class="breakdown-bar-bg">
                        <div class="breakdown-bar-fill" style="width: ${Math.min(wr, 100)}%;"></div>
                    </div>
                `;
                stratContainer.appendChild(el);
            });
        }

        // Emotion
        const emoContainer = document.getElementById("emotion-breakdown-list");
        emoContainer.innerHTML = "";
        const emos = stats.emotion_stats || {};
        const emoKeys = Object.keys(emos);

        if (emoKeys.length === 0) {
            emoContainer.innerHTML = '<div class="no-chart">Chưa có dữ liệu tâm lý</div>';
        } else {
            emoKeys.forEach(name => {
                const item = emos[name];
                const pnl = item.pnl || 0;
                const wr = item.win_rate || 0;
                const el = document.createElement("div");
                el.className = "breakdown-item";
                el.innerHTML = `
                    <div class="breakdown-item-header">
                        <span class="breakdown-name">${name} (${item.count} lệnh)</span>
                        <span class="breakdown-stats ${pnl >= 0 ? 'text-win' : 'text-loss'}">
                            ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)} | WR: ${wr}%
                        </span>
                    </div>
                    <div class="breakdown-bar-bg">
                        <div class="breakdown-bar-fill" style="width: ${Math.min(wr, 100)}%; background: ${pnl >= 0 ? 'var(--win-green)' : 'var(--loss-red)'};"></div>
                    </div>
                `;
                emoContainer.appendChild(el);
            });
        }

        // Symbol
        const symContainer = document.getElementById("symbol-breakdown-list");
        symContainer.innerHTML = "";
        const syms = stats.symbol_stats || {};
        const symKeys = Object.keys(syms);

        if (symKeys.length === 0) {
            symContainer.innerHTML = '<div class="no-chart">Chưa có dữ liệu cặp tiền</div>';
        } else {
            symKeys.forEach(name => {
                const item = syms[name];
                const pnl = item.pnl || 0;
                const wr = item.win_rate || 0;
                const el = document.createElement("div");
                el.className = "breakdown-item";
                el.innerHTML = `
                    <div class="breakdown-item-header">
                        <span class="breakdown-name font-bold">${name} (${item.count} lệnh)</span>
                        <span class="breakdown-stats ${pnl >= 0 ? 'text-win' : 'text-loss'}">
                            ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)} | WR: ${wr}%
                        </span>
                    </div>
                    <div class="breakdown-bar-bg">
                        <div class="breakdown-bar-fill" style="width: ${Math.min(wr, 100)}%;"></div>
                    </div>
                `;
                symContainer.appendChild(el);
            });
        }
    }

    // ==========================================
    // TRADES JOURNAL TABLE VIEW
    // ==========================================
    async function loadTrades() {
        try {
            const params = new URLSearchParams();
            if (elements.filterSearch.value.trim()) params.append("search", elements.filterSearch.value.trim());
            if (elements.filterSymbol.value !== "Tất cả") params.append("symbol", elements.filterSymbol.value);
            if (elements.filterStatus.value !== "Tất cả") params.append("status", elements.filterStatus.value);
            if (elements.filterResult.value !== "Tất cả") params.append("result", elements.filterResult.value);
            if (elements.filterStrategy.value !== "Tất cả") params.append("strategy", elements.filterStrategy.value);

            const res = await fetch(`/api/trades?${params.toString()}`);
            if (res.status === 401) {
                showAuthModal();
                return;
            }
            const trades = await res.json();
            state.trades = trades;

            renderTradesTable(trades);
            elements.totalTradesCounter.textContent = trades.length;
            elements.filterStatsLabel.textContent = `Đang hiển thị ${trades.length} lệnh`;
        } catch (err) {
            console.error("Lỗi nạp danh sách lệnh:", err);
        }
    }

    function renderTradesTable(trades) {
        elements.tradesTbody.innerHTML = "";

        if (!trades || trades.length === 0) {
            elements.tradesEmptyState.style.display = "block";
            return;
        }

        elements.tradesEmptyState.style.display = "none";

        trades.forEach(t => {
            const tr = document.createElement("tr");

            const isLong = (t.trade_type || "Long").toLowerCase() === "long";
            const typeBadge = `<span class="badge ${isLong ? 'badge-long' : 'badge-short'}">${isLong ? '↗ LONG' : '↘ SHORT'}</span>`;

            const isFutures = (t.market_type || "Futures") === "Futures";
            const marketInfo = `<span class="badge ${isFutures ? 'badge-open' : 'badge-closed'}">${t.market_type} ${isFutures ? `x${t.leverage || 1}` : ''}</span>`;
            const statusBadge = `<span class="badge ${t.status === 'Open' ? 'badge-open' : 'badge-closed'}">${t.status}</span>`;

            const pnl = t.pnl || 0;
            const pnlPercent = t.pnl_percent || 0;
            let pnlHtml = "-";
            let roiHtml = "-";

            if (t.status === "Closed") {
                const pnlClass = pnl > 0 ? "pnl-win" : pnl < 0 ? "pnl-loss" : "pnl-be";
                pnlHtml = `<span class="pnl-pill ${pnlClass}">${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}</span>`;
                roiHtml = `<span class="font-bold ${pnl >= 0 ? 'text-win' : 'text-loss'}">${pnlPercent >= 0 ? '+' : ''}${pnlPercent.toFixed(2)}%</span>`;
            } else if (t.status === "Open") {
                pnlHtml = `<span class="badge badge-open">Đang chạy</span>`;
            }

            const rr = t.status === "Closed" ? (t.realized_rr || 0).toFixed(2) : (t.planned_rr || 0).toFixed(2);
            const rrHtml = `<span class="mono">${rr > 0 ? `1:${rr}` : '-'}</span>`;

            let chartHtml = `<span class="no-chart">Không</span>`;
            if (t.chart_image_path) {
                const chartUrl = t.chart_image_path.startsWith("/") || t.chart_image_path.startsWith("http") 
                    ? t.chart_image_path 
                    : `/charts/${t.chart_image_path.split(/[\\/]/).pop()}`;
                chartHtml = `<img src="${chartUrl}" class="chart-thumb" alt="Chart" data-src="${chartUrl}" title="Nhấn để phóng to">`;
            }

            const dateStr = t.entry_date ? t.entry_date.substring(5, 16) : "-";

            tr.innerHTML = `
                <td class="mono text-muted">#${t.id}</td>
                <td><strong class="font-bold">${t.symbol}</strong> <span class="text-muted" style="font-size:11px;">${t.timeframe || ''}</span></td>
                <td>${typeBadge}</td>
                <td>${marketInfo}</td>
                <td>${statusBadge}</td>
                <td class="mono">$${(t.entry_price || 0).toLocaleString()}</td>
                <td class="mono">${t.exit_price ? '$' + Number(t.exit_price).toLocaleString() : '-'}</td>
                <td class="mono">$${(t.position_size || 0).toFixed(0)}</td>
                <td>${pnlHtml}</td>
                <td>${roiHtml}</td>
                <td>${rrHtml}</td>
                <td><span style="font-size:12px;">${t.strategy || '-'}</span></td>
                <td><span style="font-size:12px;">${t.emotion || '-'}</span></td>
                <td>${chartHtml}</td>
                <td class="text-muted" style="font-size:11px;">${dateStr}</td>
                <td>
                    <div class="row-actions">
                        <button class="action-btn btn-edit" data-id="${t.id}" title="Chỉnh sửa">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                        </button>
                        <button class="action-btn btn-delete" data-id="${t.id}" title="Xóa lệnh">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
                        </button>
                    </div>
                </td>
            `;

            tr.addEventListener("click", (e) => {
                if (e.target.closest(".action-btn") || e.target.closest(".chart-thumb")) return;
                openEditModal(t.id);
            });

            elements.tradesTbody.appendChild(tr);
        });

        document.querySelectorAll(".chart-thumb").forEach(img => {
            img.addEventListener("click", (e) => {
                e.stopPropagation();
                openLightbox(img.getAttribute("data-src"));
            });
        });

        document.querySelectorAll(".btn-edit").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                openEditModal(btn.getAttribute("data-id"));
            });
        });

        document.querySelectorAll(".btn-delete").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                handleDeleteTrade(btn.getAttribute("data-id"));
            });
        });
    }

    // ==========================================
    // TRADING CALENDAR (TAB 3)
    // ==========================================
    function renderCalendar() {
        const year = state.calDate.getFullYear();
        const month = state.calDate.getMonth();

        const monthNames = [
            "Tháng 01", "Tháng 02", "Tháng 03", "Tháng 04",
            "Tháng 05", "Tháng 06", "Tháng 07", "Tháng 08",
            "Tháng 09", "Tháng 10", "Tháng 11", "Tháng 12"
        ];
        elements.calMonthTitle.textContent = `${monthNames[month]} / ${year}`;

        const firstDayOfMonth = new Date(year, month, 1);
        const lastDayOfMonth = new Date(year, month + 1, 0);
        const totalDays = lastDayOfMonth.getDate();

        let startingDay = firstDayOfMonth.getDay() - 1;
        if (startingDay === -1) startingDay = 6;

        const dailyData = {};
        let monthTotalPnl = 0;
        let monthWins = 0;
        let monthLosses = 0;
        let monthTradesCount = 0;

        state.trades.forEach(t => {
            if (t.status !== "Closed") return;
            const dateStr = t.exit_date || t.entry_date;
            if (!dateStr) return;

            const dayKey = dateStr.substring(0, 10);
            const [tY, tM] = dayKey.split("-").map(Number);
            
            if (tY === year && tM === month + 1) {
                if (!dailyData[dayKey]) {
                    dailyData[dayKey] = { pnl: 0, wins: 0, losses: 0, count: 0 };
                }
                const pnl = t.pnl || 0;
                dailyData[dayKey].pnl += pnl;
                dailyData[dayKey].count += 1;
                monthTradesCount += 1;
                monthTotalPnl += pnl;

                if (pnl > 0) {
                    dailyData[dayKey].wins += 1;
                    monthWins += 1;
                } else if (pnl < 0) {
                    dailyData[dayKey].losses += 1;
                    monthLosses += 1;
                }
            }
        });

        elements.calMonthPnl.textContent = `${monthTotalPnl >= 0 ? '+' : ''}$${monthTotalPnl.toFixed(2)}`;
        elements.calMonthPnl.className = `chip-value ${monthTotalPnl >= 0 ? 'text-win' : 'text-loss'}`;
        const totalDecided = monthWins + monthLosses;
        const wr = totalDecided > 0 ? ((monthWins / totalDecided) * 100).toFixed(0) : "0";
        elements.calMonthWr.textContent = `${wr}%`;
        elements.calMonthTradesCount.textContent = `${monthTradesCount} lệnh`;

        elements.calendarDaysGrid.innerHTML = "";

        const prevMonthLastDay = new Date(year, month, 0).getDate();
        for (let i = startingDay - 1; i >= 0; i--) {
            const cell = document.createElement("div");
            cell.className = "cal-day-cell other-month";
            cell.innerHTML = `<span class="cal-day-number">${prevMonthLastDay - i}</span>`;
            elements.calendarDaysGrid.appendChild(cell);
        }

        for (let d = 1; d <= totalDays; d++) {
            const dStr = String(d).padStart(2, "0");
            const mStr = String(month + 1).padStart(2, "0");
            const dayKey = `${year}-${mStr}-${dStr}`;
            const info = dailyData[dayKey];

            const cell = document.createElement("div");
            cell.className = "cal-day-cell";

            if (info) {
                const isWin = info.pnl >= 0;
                cell.classList.add(isWin ? "day-win" : "day-loss");
                cell.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="cal-day-number font-bold">${d}</span>
                        <span class="cal-day-trades">${info.wins}W - ${info.losses}L</span>
                    </div>
                    <div class="cal-day-pnl ${isWin ? 'text-win' : 'text-loss'}">
                        ${isWin ? '+' : ''}$${info.pnl.toFixed(1)}
                    </div>
                    <div class="cal-day-trades">${info.count} lệnh</div>
                `;
            } else {
                cell.innerHTML = `
                    <span class="cal-day-number">${d}</span>
                    <div class="text-muted" style="font-size:11px; margin-top:auto;">-</div>
                `;
            }

            elements.calendarDaysGrid.appendChild(cell);
        }
    }

    // ==========================================
    // MODAL & FORM INTERACTIONS
    // ==========================================
    function openAddModal() {
        if (!state.user) {
            showAuthModal();
            return;
        }
        elements.tradeForm.reset();
        elements.formTradeId.value = "";
        elements.tradeModalTitle.textContent = "Ghi Nhận Lệnh Mới";
        elements.btnSaveText.textContent = "Lưu Lệnh Vào Nhật Ký";

        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        elements.formEntryDate.value = now.toISOString().slice(0, 16);

        resetDropzone();
        updateFormLiveCalculations();

        elements.modalTradeForm.classList.add("active");
    }

    async function openEditModal(tradeId) {
        try {
            const res = await fetch(`/api/trades/${tradeId}`);
            if (res.status === 401) {
                showAuthModal();
                return;
            }
            if (!res.ok) throw new Error("Không tìm thấy lệnh");
            const trade = await res.json();

            elements.formTradeId.value = trade.id;
            elements.tradeModalTitle.textContent = `Chỉnh Sửa Lệnh #${trade.id} (${trade.symbol})`;
            elements.btnSaveText.textContent = "Cập Nhật Lệnh";

            elements.formSymbol.value = trade.symbol || "";
            if ((trade.trade_type || "Long") === "Long") {
                elements.typeLong.checked = true;
            } else {
                elements.typeShort.checked = true;
            }

            elements.formMarketType.value = trade.market_type || "Futures";
            elements.formLeverage.value = trade.leverage || 10;
            elements.formStatus.value = trade.status || "Closed";
            elements.formTimeframe.value = trade.timeframe || "H1";

            if (trade.entry_date) {
                elements.formEntryDate.value = trade.entry_date.replace(" ", "T").substring(0, 16);
            }
            if (trade.exit_date) {
                elements.formExitDate.value = trade.exit_date.replace(" ", "T").substring(0, 16);
            }

            elements.formEntryPrice.value = trade.entry_price || "";
            elements.formStopLoss.value = trade.stop_loss || "";
            elements.formTakeProfit.value = trade.take_profit || "";
            elements.formExitPrice.value = trade.exit_price || "";
            elements.formPositionSize.value = trade.position_size || "";
            elements.formFees.value = trade.fees || 0;

            elements.formStrategy.value = trade.strategy || "";
            elements.formEmotion.value = trade.emotion || "";
            elements.formNotes.value = trade.notes || "";
            elements.formLessons.value = trade.lessons || "";

            if (trade.chart_image_path) {
                const chartUrl = trade.chart_image_path.startsWith("/") || trade.chart_image_path.startsWith("http")
                    ? trade.chart_image_path
                    : `/charts/${trade.chart_image_path.split(/[\\/]/).pop()}`;
                setDropzonePreview(chartUrl, trade.chart_image_path);
            } else {
                resetDropzone();
            }

            updateFormLiveCalculations();
            elements.modalTradeForm.classList.add("active");

        } catch (err) {
            showToast(err.message, "error");
        }
    }

    function closeTradeModal() {
        elements.modalTradeForm.classList.remove("active");
    }

    async function handleSaveTrade(e) {
        e.preventDefault();

        const tradeId = elements.formTradeId.value;
        const payload = {
            symbol: elements.formSymbol.value.trim().toUpperCase(),
            trade_type: elements.typeLong.checked ? "Long" : "Short",
            market_type: elements.formMarketType.value,
            leverage: parseInt(elements.formLeverage.value) || 1,
            status: elements.formStatus.value,
            timeframe: elements.formTimeframe.value,
            entry_date: elements.formEntryDate.value.replace("T", " ") + ":00",
            exit_date: elements.formExitDate.value ? elements.formExitDate.value.replace("T", " ") + ":00" : null,
            entry_price: parseFloat(elements.formEntryPrice.value) || 0,
            stop_loss: elements.formStopLoss.value ? parseFloat(elements.formStopLoss.value) : null,
            take_profit: elements.formTakeProfit.value ? parseFloat(elements.formTakeProfit.value) : null,
            exit_price: elements.formExitPrice.value ? parseFloat(elements.formExitPrice.value) : null,
            position_size: parseFloat(elements.formPositionSize.value) || 0,
            fees: parseFloat(elements.formFees.value) || 0,
            strategy: elements.formStrategy.value,
            emotion: elements.formEmotion.value,
            notes: elements.formNotes.value,
            lessons: elements.formLessons.value,
            chart_image_path: elements.formChartPath.value,
        };

        const url = tradeId ? `/api/trades/${tradeId}` : "/api/trades";
        const method = tradeId ? "PUT" : "POST";

        try {
            elements.btnSaveTrade.disabled = true;
            elements.btnSaveText.textContent = "Đang lưu...";

            const res = await fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await res.json();
            if (!res.ok) throw new Error(result.error || "Lỗi lưu lệnh");

            showToast(tradeId ? "Cập nhật lệnh thành công!" : "Thêm lệnh mới thành công!", "success");
            closeTradeModal();
            await refreshAllData();

        } catch (err) {
            showToast(err.message, "error");
        } finally {
            elements.btnSaveTrade.disabled = false;
            elements.btnSaveText.textContent = tradeId ? "Cập Nhật Lệnh" : "Lưu Lệnh Vào Nhật Ký";
        }
    }

    async function handleDeleteTrade(tradeId) {
        if (!confirm(`Bạn có chắc chắn muốn xóa lệnh #${tradeId} này không?`)) return;

        try {
            const res = await fetch(`/api/trades/${tradeId}`, { method: "DELETE" });
            const result = await res.json();
            if (!res.ok) throw new Error(result.error || "Không thể xóa");

            showToast("Đã xóa lệnh thành công!", "success");
            await refreshAllData();
        } catch (err) {
            showToast(err.message, "error");
        }
    }

    function updateFormLiveCalculations() {
        const isLong = elements.typeLong.checked;
        const entry = parseFloat(elements.formEntryPrice.value) || 0;
        const exit = parseFloat(elements.formExitPrice.value) || null;
        const sl = parseFloat(elements.formStopLoss.value) || null;
        const tp = parseFloat(elements.formTakeProfit.value) || null;
        const margin = parseFloat(elements.formPositionSize.value) || 0;
        const lev = parseInt(elements.formLeverage.value) || 1;
        const fees = parseFloat(elements.formFees.value) || 0;

        let plannedRr = 0;
        let realizedRr = 0;
        let pnl = 0;
        let roi = 0;

        if (entry > 0 && sl && tp) {
            let risk = isLong ? (entry - sl) : (sl - entry);
            let reward = isLong ? (tp - entry) : (entry - tp);
            if (risk > 0 && reward > 0) {
                plannedRr = reward / risk;
            }
        }

        if (entry > 0 && exit && exit > 0 && margin > 0) {
            let priceChangeRatio = isLong ? (exit - entry) / entry : (entry - exit) / entry;
            let rawPnl = priceChangeRatio * (margin * lev);
            pnl = rawPnl - fees;
            roi = (pnl / margin) * 100;

            if (sl && sl > 0) {
                let risk = isLong ? (entry - sl) : (sl - entry);
                let realizedDiff = isLong ? (exit - entry) : (entry - exit);
                if (risk > 0) {
                    realizedRr = realizedDiff / risk;
                }
            }
        }

        elements.livePlannedRr.textContent = plannedRr > 0 ? `1 : ${plannedRr.toFixed(2)}` : "-";
        elements.liveRealizedRr.textContent = realizedRr !== 0 ? `1 : ${realizedRr.toFixed(2)}` : "-";
        
        const pnlEl = elements.livePnl;
        const roiEl = elements.liveRoi;

        if (exit && exit > 0) {
            pnlEl.textContent = `${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}`;
            roiEl.textContent = `${roi >= 0 ? '+' : ''}${roi.toFixed(2)}%`;
            pnlEl.className = `live-item-val font-bold ${pnl >= 0 ? 'text-win' : 'text-loss'}`;
            roiEl.className = `live-item-val font-bold ${roi >= 0 ? 'text-win' : 'text-loss'}`;
        } else {
            pnlEl.textContent = "$0.00";
            roiEl.textContent = "0.00%";
            pnlEl.className = "live-item-val font-bold text-muted";
            roiEl.className = "live-item-val font-bold text-muted";
        }
    }

    function setupDropzone() {
        elements.chartDropzone.addEventListener("click", () => {
            elements.fileChartInput.click();
        });

        elements.fileChartInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) uploadImageFile(file);
        });

        elements.btnRemoveChart.addEventListener("click", (e) => {
            e.stopPropagation();
            resetDropzone();
            showToast("Đã gỡ ảnh biểu đồ", "info");
        });

        ["dragenter", "dragover"].forEach(eventName => {
            elements.chartDropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                elements.chartDropzone.style.borderColor = "var(--win-green)";
            });
        });

        ["dragleave", "drop"].forEach(eventName => {
            elements.chartDropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                elements.chartDropzone.style.borderColor = "";
            });
        });

        elements.chartDropzone.addEventListener("drop", (e) => {
            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                uploadImageFile(files[0]);
            }
        });

        window.addEventListener("paste", (e) => {
            if (!elements.modalTradeForm.classList.contains("active")) return;
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf("image") !== -1) {
                    const blob = items[i].getAsFile();
                    uploadImageFile(blob);
                    e.preventDefault();
                    break;
                }
            }
        });
    }

    async function uploadImageFile(file) {
        showToast("Đang tải ảnh biểu đồ lên...", "info");
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("/api/upload-chart", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || "Lỗi tải ảnh");

            setDropzonePreview(data.url, data.filepath);
            showToast("📋 Đã dán ảnh biểu đồ TradingView thành công!", "success");
        } catch (err) {
            showToast(err.message, "error");
        }
    }

    function setDropzonePreview(url, fullPath) {
        elements.previewChartImg.src = url;
        elements.formChartPath.value = fullPath || url;
        elements.dropzoneIdle.style.display = "none";
        elements.dropzonePreview.style.display = "flex";
    }

    function resetDropzone() {
        elements.previewChartImg.src = "";
        elements.formChartPath.value = "";
        elements.fileChartInput.value = "";
        elements.dropzoneIdle.style.display = "block";
        elements.dropzonePreview.style.display = "none";
    }

    function openLightbox(src) {
        elements.lightboxImg.src = src;
        elements.modalLightbox.classList.add("active");
    }

    function closeLightbox() {
        elements.modalLightbox.classList.remove("active");
        elements.lightboxImg.src = "";
    }

    function setupEventListeners() {
        // Auth Tab switching
        elements.tabLoginBtn.addEventListener("click", () => {
            elements.tabLoginBtn.classList.add("active");
            elements.tabRegisterBtn.classList.remove("active");
            elements.formLogin.style.display = "flex";
            elements.formRegister.style.display = "none";
            hideAuthAlert();
        });

        elements.tabRegisterBtn.addEventListener("click", () => {
            elements.tabRegisterBtn.classList.add("active");
            elements.tabLoginBtn.classList.remove("active");
            elements.formRegister.style.display = "flex";
            elements.formLogin.style.display = "none";
            hideAuthAlert();
        });

        // Auth Form Submits
        elements.formLogin.addEventListener("submit", handleLoginSubmit);
        elements.formRegister.addEventListener("submit", handleRegisterSubmit);

        // Forgot password handlers
        if (elements.linkForgotPwd) {
            elements.linkForgotPwd.addEventListener("click", (e) => {
                e.preventDefault();
                elements.formLogin.style.display = "none";
                elements.formRegister.style.display = "none";
                elements.formResetPwd.style.display = "flex";
                elements.resetUsername.value = elements.loginUsername.value.trim();
                hideAuthAlert();
            });
        }

        if (elements.linkBackLogin) {
            elements.linkBackLogin.addEventListener("click", (e) => {
                e.preventDefault();
                elements.formResetPwd.style.display = "none";
                elements.formLogin.style.display = "flex";
                hideAuthAlert();
            });
        }

        if (elements.formResetPwd) {
            elements.formResetPwd.addEventListener("submit", async (e) => {
                e.preventDefault();
                hideAuthAlert();
                const username = elements.resetUsername.value.trim();
                const newPassword = elements.resetNewPassword.value;

                if (!username || newPassword.length < 4) {
                    showAuthAlert("Vui lòng nhập tên đăng nhập và mật khẩu mới tối thiểu 4 ký tự!");
                    return;
                }

                try {
                    elements.btnSubmitResetPwd.disabled = true;
                    elements.btnSubmitResetPwd.textContent = "Đang đặt lại...";

                    const res = await fetch("/api/auth/reset-password", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ username, new_password: newPassword })
                    });
                    const data = await res.json();

                    if (!res.ok) {
                        showAuthAlert(data.error || "Không thể đặt lại mật khẩu!");
                        return;
                    }

                    showToast("Đặt lại mật khẩu thành công! Đã đăng nhập.", "success");
                    onUserLoggedIn(data.user);
                    elements.formResetPwd.reset();

                } catch (err) {
                    showAuthAlert("Lỗi kết nối máy chủ!");
                } finally {
                    elements.btnSubmitResetPwd.disabled = false;
                    elements.btnSubmitResetPwd.textContent = "Đặt Lại Mật Khẩu & Đăng Nhập";
                }
            });
        }
        elements.btnLogout.addEventListener("click", handleLogout);

        // App Navigation Tabs
        elements.tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                const targetTab = btn.getAttribute("data-tab");
                state.currentTab = targetTab;

                elements.tabBtns.forEach(b => b.classList.remove("active"));
                elements.tabViews.forEach(v => v.classList.remove("active"));

                btn.classList.add("active");
                document.getElementById(`view-${targetTab}`).classList.add("active");

                if (targetTab === "calendar") {
                    renderCalendar();
                } else if (targetTab === "dashboard" && state.chartInstance) {
                    state.chartInstance.resize();
                }
            });
        });

        // Trade Actions
        elements.btnOpenAddTrade.addEventListener("click", openAddModal);
        elements.btnEmptyAddTrade.addEventListener("click", openAddModal);
        elements.btnCloseTradeModal.addEventListener("click", closeTradeModal);
        elements.btnCancelTrade.addEventListener("click", closeTradeModal);
        elements.tradeForm.addEventListener("submit", handleSaveTrade);

        [
            elements.formEntryPrice, elements.formExitPrice, elements.formStopLoss,
            elements.formTakeProfit, elements.formPositionSize, elements.formLeverage,
            elements.formFees, elements.typeLong, elements.typeShort
        ].forEach(input => {
            input.addEventListener("input", updateFormLiveCalculations);
            input.addEventListener("change", updateFormLiveCalculations);
        });

        let debounceTimer;
        elements.filterSearch.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(loadTrades, 300);
        });
        [elements.filterSymbol, elements.filterStatus, elements.filterResult, elements.filterStrategy].forEach(select => {
            select.addEventListener("change", loadTrades);
        });
        elements.btnResetFilters.addEventListener("click", () => {
            elements.filterSearch.value = "";
            elements.filterSymbol.value = "Tất cả";
            elements.filterStatus.value = "Tất cả";
            elements.filterResult.value = "Tất cả";
            elements.filterStrategy.value = "Tất cả";
            loadTrades();
        });

        elements.btnExportCsv.addEventListener("click", () => {
            window.location.href = "/api/export-csv";
            showToast("Đang tải file CSV về máy...", "success");
        });

        elements.btnRefresh.addEventListener("click", async () => {
            showToast("Đang làm mới dữ liệu...", "info");
            await refreshAllData();
            showToast("Dữ liệu đã được cập nhật mới nhất!", "success");
        });

        elements.btnCloseLightbox.addEventListener("click", closeLightbox);
        elements.modalLightbox.addEventListener("click", (e) => {
            if (e.target === elements.modalLightbox) closeLightbox();
        });

        elements.btnCalPrev.addEventListener("click", () => {
            state.calDate.setMonth(state.calDate.getMonth() - 1);
            renderCalendar();
        });
        elements.btnCalNext.addEventListener("click", () => {
            state.calDate.setMonth(state.calDate.getMonth() + 1);
            renderCalendar();
        });
        elements.btnCalToday.addEventListener("click", () => {
            state.calDate = new Date();
            renderCalendar();
        });

        window.addEventListener("keydown", (e) => {
            if (e.ctrlKey && e.key.toLowerCase() === "n") {
                e.preventDefault();
                openAddModal();
            }
            if (e.key === "Escape") {
                if (elements.modalLightbox.classList.contains("active")) {
                    closeLightbox();
                } else if (elements.modalTradeForm.classList.contains("active")) {
                    closeTradeModal();
                }
            }
        });

        setupDropzone();
    }

    initApp();
});
