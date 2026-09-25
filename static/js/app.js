/**
 * Crypto Trading Journal - Modern Frontend Application Logic
 * Hỗ trợ Đa Người Dùng (Multi-User Authentication) & Phân quyền dữ liệu
 */

document.addEventListener("DOMContentLoaded", () => {
    // State management
    const state = {
        user: null,
        mt5Accounts: [],
        currentMt5AccountId: (localStorage.getItem("active_mt5_account_id") === "manual" ? "all" : (localStorage.getItem("active_mt5_account_id") || "all")),
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
                btnResetFilters: document.getElementById("btn-reset-filters"),
        filterStatsLabel: document.getElementById("filter-stats-label"),

        // Table
        tradesTbody: document.getElementById("trades-tbody"),
        tradesCardsContainer: document.getElementById("trades-cards-container"),
        bnavTradeCounter: document.getElementById("bnav-trade-counter"),
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
        formAccountId: document.getElementById("form-account-id"),
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
        formRiskAmount: document.getElementById("form-risk-amount"),
        formPlannedReward: document.getElementById("form-planned-reward"),
        formExitPrice: document.getElementById("form-exit-price"),
        formPositionSize: document.getElementById("form-position-size"),
        formFees: document.getElementById("form-fees"),
        formStrategy: document.getElementById("form-strategy"),
        formEmotion: document.getElementById("form-emotion"),
        formNotes: document.getElementById("form-notes"),
        formLessons: document.getElementById("form-lessons"),
        formChartPath: document.getElementById("form-chart-path"),

        // Capital Management elements
        kpiInitialCapital: document.getElementById("kpi-initial-capital"),
        kpiCurrentCapital: document.getElementById("kpi-current-capital"),
        kpiCapitalGrowth: document.getElementById("kpi-capital-growth"),
        btnQuickEditCapital: document.getElementById("btn-quick-edit-capital"),
        capitalDisplayView: document.getElementById("capital-display-view"),
        capitalEditView: document.getElementById("capital-edit-view"),
        inputInitialCapital: document.getElementById("input-initial-capital"),
        btnSaveCapital: document.getElementById("btn-save-capital"),
        btnCancelCapital: document.getElementById("btn-cancel-capital"),

        // Live calculation elements
        livePlannedRr: document.getElementById("live-planned-rr"),
        liveRealizedRr: document.getElementById("live-realized-rr"),
        liveRiskVal: document.getElementById("live-risk-val"),
        liveRewardVal: document.getElementById("live-reward-val"),
        livePnl: document.getElementById("live-pnl"),
        liveRoi: document.getElementById("live-roi"),

        // Dropzone & Charts
        chartDropzone: document.getElementById("chart-dropzone"),
        dropzoneIdle: document.getElementById("dropzone-idle"),
        dropzonePreview: document.getElementById("dropzone-preview"),
        previewChartImg: document.getElementById("preview-chart-img"),
        fileChartInput: document.getElementById("file-chart-input"),
        btnRemoveChart: document.getElementById("btn-remove-chart"),

        
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
    // PERSISTENT AUTHENTICATION (TOKEN & LOCALSTORAGE)
    // ==========================================
    function getAuthHeaders(existingHeaders = {}) {
        const headers = { ...existingHeaders };
        const token = localStorage.getItem("cj_auth_token");
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
            headers["X-Auth-Token"] = token;
        }
        return headers;
    }

    async function authFetch(url, options = {}) {
        options.headers = getAuthHeaders(options.headers);
        return fetch(url, options);
    }

    // ==========================================
    // AUTHENTICATION LOGIC (LOGIN / REGISTER / LOGOUT)
    // ==========================================
    async function checkAuthStatus() {
        try {
            // Khôi phục tức thì hiển thị trên thiết bị để không bị giật lag
            const cachedUserStr = localStorage.getItem("cj_user");
            if (cachedUserStr) {
                try {
                    const cachedUser = JSON.parse(cachedUserStr);
                    if (cachedUser && (cachedUser.display_name || cachedUser.username)) {
                        const firstLetter = (cachedUser.display_name || cachedUser.username || "T").charAt(0).toUpperCase();
                        elements.userAvatarText.textContent = firstLetter;
                        elements.userDisplayName.textContent = cachedUser.display_name || cachedUser.username;
                        elements.userProfileChip.style.display = "flex";
                    }
                } catch (e) {}
            }

            const res = await authFetch("/api/auth/me");
            const data = await res.json();
            if (data.logged_in && data.user) {
                if (data.token) {
                    localStorage.setItem("cj_auth_token", data.token);
                }
                localStorage.setItem("cj_user", JSON.stringify(data.user));
                const wasLoaded = !!state.user;
                state.user = data.user;
                hideAuthModal();

                const firstLetter = (data.user.display_name || data.user.username || "T").charAt(0).toUpperCase();
                if (elements.userAvatarText) elements.userAvatarText.textContent = firstLetter;
                if (elements.userDisplayName) elements.userDisplayName.textContent = data.user.display_name || data.user.username;
                if (elements.userProfileChip) elements.userProfileChip.style.display = "flex";

                if (!wasLoaded) {
                    loadMt5Accounts();
                    refreshAllData();
                }
            } else {
                localStorage.removeItem("cj_auth_token");
                localStorage.removeItem("cj_user");
                showAuthModal();
            }
        } catch (err) {
            console.error("Lỗi kiểm tra auth:", err);
            const token = localStorage.getItem("cj_auth_token");
            if (!token) {
                showAuthModal();
            }
        }
    }

    // ==========================================
    // UTILITY HELPERS (SHARED & PERFORMANCE OPTIMIZED)
    // ==========================================
    function formatChartUrl(path) {
        if (!path) return "";
        if (path.startsWith("/") || path.startsWith("http")) return path;
        return `/charts/${path.split(/[\\/]/).pop()}`;
    }

    function openModalElement(modalEl) {
        if (!modalEl) return;
        modalEl.classList.add("active");
        document.body.classList.add("modal-open");
    }

    function closeModalElement(modalEl) {
        if (!modalEl) return;
        modalEl.classList.remove("active");
        const anyActive = document.querySelector(".modal-backdrop.active, .lightbox-backdrop.active");
        if (!anyActive) {
            document.body.classList.remove("modal-open");
        }
    }

    function selectTradeSymbol(sym) {
        if (!sym) return;
        if (elements.formSymbol) {
            elements.formSymbol.value = sym;
            const val = sym.toUpperCase();
            if (val.includes("XAU") || val.includes("XAG") || val.includes("OIL") || (!val.includes("USDT") && val.includes("/"))) {
                if (elements.formMarketType) elements.formMarketType.value = "Forex / CFD";
            } else {
                if (elements.formMarketType) elements.formMarketType.value = "Futures";
            }
            elements.formSymbol.dispatchEvent(new Event("input"));
        }
        document.querySelectorAll(".symbol-pick-btn").forEach(b => {
            if (b.getAttribute("data-symbol") === sym) b.classList.add("active");
            else b.classList.remove("active");
        });
    }

    function showAuthModal() {
        openModalElement(elements.modalAuth);
        if (elements.userProfileChip) elements.userProfileChip.style.display = "none";
        hideAuthAlert();
    }

    function hideAuthModal() {
        closeModalElement(elements.modalAuth);
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

        // Nạp danh sách tài khoản MT5 và dữ liệu riêng của user này
        loadMt5Accounts();
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

            const res = await authFetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();

            if (!res.ok) {
                showAuthAlert(data.error || "Đăng nhập thất bại!");
                return;
            }

            if (data.token) {
                localStorage.setItem("cj_auth_token", data.token);
            }
            if (data.user) {
                localStorage.setItem("cj_user", JSON.stringify(data.user));
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

            const res = await authFetch("/api/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password, display_name: displayName })
            });
            const data = await res.json();

            if (!res.ok) {
                showAuthAlert(data.error || "Đăng ký thất bại!");
                return;
            }

            if (data.token) {
                localStorage.setItem("cj_auth_token", data.token);
            }
            if (data.user) {
                localStorage.setItem("cj_user", JSON.stringify(data.user));
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
            await authFetch("/api/auth/logout", { method: "POST" });
        } catch (err) {
            console.error("Lỗi đăng xuất:", err);
        } finally {
            localStorage.removeItem("cj_auth_token");
            localStorage.removeItem("cj_user");
            state.user = null;
            state.trades = [];
            state.stats = null;
            showToast("Đã đăng xuất thành công!", "info");
            showAuthModal();
        }
    }

    // ==========================================
    // INITIALIZATION & DATA FETCHING
    // ==========================================
    async function initApp() {
        setupEventListeners();

        // FAST-PATH INITIALIZATION: Tải trước từ bộ nhớ đệm cục bộ để giảm độ trễ tối đa
        const cachedUserStr = localStorage.getItem("cj_user");
        const token = localStorage.getItem("cj_auth_token");
        if (cachedUserStr && token) {
            try {
                const cachedUser = JSON.parse(cachedUserStr);
                if (cachedUser && (cachedUser.display_name || cachedUser.username)) {
                    state.user = cachedUser;
                    const firstLetter = (cachedUser.display_name || cachedUser.username || "T").charAt(0).toUpperCase();
                    if (elements.userAvatarText) elements.userAvatarText.textContent = firstLetter;
                    if (elements.userDisplayName) elements.userDisplayName.textContent = cachedUser.display_name || cachedUser.username;
                    if (elements.userProfileChip) elements.userProfileChip.style.display = "flex";

                    // Khởi chạy dữ liệu song song ngay lập tức mà không phải chờ auth/me phản hồi
                    loadMt5Accounts();
                    refreshAllData();
                }
            } catch (e) {}
        }

        await Promise.all([loadConfig(), checkAuthStatus()]);
    }

    async function loadConfig() {
        try {
            const res = await authFetch("/api/config");
            const data = await res.json();
            state.config = data;

            
            if (elements.filterSymbol) {
                elements.filterSymbol.innerHTML = '<option value="Tất cả">Tất cả Cặp tiền</option>';
            }

            if (data.symbol_categories) {
                for (const [category, pairs] of Object.entries(data.symbol_categories)) {
                    const filterGrp = document.createElement("optgroup");
                    filterGrp.label = category;

                    pairs.forEach(pair => {
                        if (elements.filterSymbol) {
                            const fOpt = document.createElement("option");
                            fOpt.value = pair;
                            fOpt.textContent = pair;
                            filterGrp.appendChild(fOpt);
                        }
                    });

                    if (elements.filterSymbol) {
                        elements.filterSymbol.appendChild(filterGrp);
                    }
                }
            } else if (data.pairs) {
                data.pairs.forEach(pair => {
                    if (elements.filterSymbol) {
                        const filterOpt = document.createElement("option");
                        filterOpt.value = pair;
                        filterOpt.textContent = pair;
                        elements.filterSymbol.appendChild(filterOpt);
                    }
                });
            }

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
            let statsUrl = "/api/stats";
            if (state.currentMt5AccountId && state.currentMt5AccountId !== "all") {
                statsUrl += `?mt5_account_id=${encodeURIComponent(state.currentMt5AccountId)}`;
            }
            const res = await authFetch(statsUrl);
            if (res.status === 401) {
                showAuthModal();
                return;
            }
            const stats = await res.json();
            state.stats = stats;

            renderKpiCards(stats);
            renderEquityChart(stats.equity_curve || []);
            // renderBreakdowns placeholder removed
        } catch (err) {
            console.error("Lỗi nạp thống kê:", err);
        }
    }

    function renderKpiCards(stats) {
        // 1. Quản lý Vốn (Tổng vốn ban đầu & Vốn còn lại)
        const initialCap = stats.initial_capital !== undefined ? Number(stats.initial_capital) : 1000.0;
        const currentCap = stats.current_capital !== undefined ? Number(stats.current_capital) : (initialCap + (stats.net_pnl || 0));
        const growthPct = stats.capital_growth_percent !== undefined ? Number(stats.capital_growth_percent) : (initialCap > 0 ? (((stats.net_pnl || 0)) / initialCap) * 100 : 0);

        if (elements.kpiInitialCapital) {
            elements.kpiInitialCapital.textContent = `$${initialCap.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }
        if (elements.kpiCurrentCapital) {
            elements.kpiCurrentCapital.textContent = `$${currentCap.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            elements.kpiCurrentCapital.className = `kpi-value font-bold ${currentCap > initialCap ? "text-win" : currentCap < initialCap ? "text-loss" : "text-be"}`;
        }
        if (elements.kpiCapitalGrowth) {
            elements.kpiCapitalGrowth.textContent = `${growthPct >= 0 ? "+" : ""}${growthPct.toFixed(2)}%`;
            elements.kpiCapitalGrowth.className = `font-bold ${growthPct > 0 ? "text-win" : growthPct < 0 ? "text-loss" : "text-be"}`;
        }

        // 2. Net PnL và Win Rate
        const pnlEl = document.getElementById("kpi-net-pnl");
        const pnlVal = stats.net_pnl || 0;
        pnlEl.textContent = `${pnlVal >= 0 ? "+" : ""}$${pnlVal.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        pnlEl.className = `kpi-value ${pnlVal > 0 ? "text-win" : pnlVal < 0 ? "text-loss" : "text-be"}`;
        
        const subEl = document.getElementById("kpi-pnl-sub");
        if (subEl) {
            const grossPnl = stats.gross_pnl || 0;
            const totalFees = stats.total_fees || 0;
            const grossSign = grossPnl > 0 ? "+" : (grossPnl < 0 ? "-" : "");
            const grossFormatted = `${grossSign}$${Math.abs(grossPnl).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            const feesSign = totalFees > 0 ? "-" : (totalFees < 0 ? "+" : "");
            const feesFormatted = `${feesSign}$${Math.abs(totalFees).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            const grossColorClass = grossPnl > 0 ? "text-win" : (grossPnl < 0 ? "text-loss" : "text-muted");
            const feesColorClass = totalFees > 0 ? "text-loss" : (totalFees < 0 ? "text-win" : "text-muted");
            
            subEl.innerHTML = `Lãi gộp: <span class="${grossColorClass} font-bold">${grossFormatted}</span> | Phí: <span class="${feesColorClass} font-bold">${feesFormatted}</span>`;
        }

        const wrEl = document.getElementById("kpi-win-rate");
        const wrVal = stats.win_rate || 0;
        wrEl.textContent = `${wrVal.toFixed(1)}%`;
        if ((stats.closed_trades_count || 0) === 0) {
            wrEl.className = "kpi-value text-be";
        } else {
            wrEl.className = `kpi-value ${wrVal >= 50 ? "text-win" : "text-loss"}`;
        }
        document.getElementById("kpi-wins").textContent = `${stats.win_trades || 0}W`;
        document.getElementById("kpi-losses").textContent = `${stats.loss_trades || 0}L`;
        document.getElementById("kpi-be").textContent = `${stats.breakeven_trades || 0}BE`;

        const pfEl = document.getElementById("kpi-profit-factor");
        if ((stats.total_loss || 0) === 0) {
            if ((stats.total_profit || 0) > 0) {
                pfEl.textContent = "MAX";
                pfEl.className = "kpi-value text-win";
            } else {
                pfEl.textContent = "0.00";
                pfEl.className = "kpi-value text-be";
            }
        } else {
            const pfVal = stats.profit_factor || 0;
            pfEl.textContent = pfVal.toFixed(2);
            pfEl.className = `kpi-value ${pfVal >= 1.5 ? "text-win" : pfVal >= 1.0 ? "text-accent" : "text-loss"}`;
        }
        document.getElementById("kpi-total-profit").textContent = `+$${(stats.total_profit || 0).toLocaleString()}`;
        document.getElementById("kpi-total-loss").textContent = `-$${(stats.total_loss || 0).toLocaleString()}`;

        document.getElementById("kpi-avg-win").textContent = `+$${(stats.avg_win || 0).toFixed(2)}`;
        document.getElementById("kpi-avg-loss").textContent = `-$${(stats.avg_loss || 0).toFixed(2)}`;
        const ratioEl = document.getElementById("kpi-win-loss-ratio");
        if ((stats.avg_loss || 0) > 0) {
            const ratio = ((stats.avg_win || 0) / stats.avg_loss).toFixed(1);
            ratioEl.textContent = `Tỷ lệ Lãi:Lỗ: ${ratio}x`;
        } else if ((stats.avg_win || 0) > 0) {
            ratioEl.textContent = `Tỷ lệ Lãi:Lỗ: MAX`;
        } else {
            ratioEl.textContent = `Tỷ lệ Lãi:Lỗ: 0.0x`;
        }

        let avgRrVal = parseFloat(stats.avg_rr) || 0;
        if (avgRrVal <= 0 && (stats.avg_loss || 0) > 0 && (stats.avg_win || 0) > 0) {
            avgRrVal = (stats.avg_win / stats.avg_loss);
        }
        if (isNaN(avgRrVal) || !isFinite(avgRrVal)) avgRrVal = 0;
        document.getElementById("kpi-avg-rr").textContent = `1 : ${avgRrVal.toFixed(2)}`;
        document.getElementById("kpi-max-wins").textContent = `${stats.max_consecutive_wins || 0}W`;
        document.getElementById("kpi-max-losses").textContent = `${stats.max_consecutive_losses || 0}L`;
        // 3. Xử lý giao diện sửa vốn ban đầu:
        // - Khi ở "Tất Cả Tài Khoản": Tự động cộng tổng từ các tài khoản con, không thể sửa trực tiếp
        // - Khi ở tài khoản LIÊN KẾT ĐỒNG BỘ: Khóa vốn ban đầu, không cho sửa tay để bảo toàn dữ liệu sàn
        // - Khi ở tài khoản KHÔNG LIÊN KẾT (Ghi tay): Cho phép nhấp vào dòng phụ để sửa vốn ban đầu
        const isAllAccounts = state.currentMt5AccountId === "all";
        const totalAccs = state.mt5Accounts ? state.mt5Accounts.length : 0;
        const isLinked = stats && stats.is_linked;

        if (elements.btnQuickEditCapital) {
            if (isAllAccounts) {
                elements.btnQuickEditCapital.textContent = totalAccs > 0 
                    ? `📊 Tổng tự động từ ${totalAccs} tài khoản con` 
                    : `📊 Tổng hợp toàn bộ danh mục`;
                elements.btnQuickEditCapital.style.cursor = "default";
                elements.btnQuickEditCapital.style.color = "var(--text-muted)";
                elements.btnQuickEditCapital.style.opacity = "0.75";
                elements.btnQuickEditCapital.title = "Vốn này là tổng hợp tự động từ các tài khoản con, không thể sửa trực tiếp.";
            } else if (isLinked) {
                // Tài khoản liên kết đồng bộ với sàn: KHÓA VỐN BAN ĐẦU
                elements.btnQuickEditCapital.textContent = "🔒 Khóa tự động theo sàn liên kết";
                elements.btnQuickEditCapital.style.cursor = "default";
                elements.btnQuickEditCapital.style.color = "var(--text-muted)";
                elements.btnQuickEditCapital.style.opacity = "0.85";
                elements.btnQuickEditCapital.title = "Tài khoản này được đồng bộ trực tiếp từ sàn, vốn ban đầu được bảo toàn tự động và không thể chỉnh sửa tay.";
            } else {
                // Tài khoản ghi chép thủ công: CHO PHÉP CHỈNH SỬA
                elements.btnQuickEditCapital.textContent = "✏️ Nhấp để sửa vốn ban đầu";
                elements.btnQuickEditCapital.style.cursor = "pointer";
                elements.btnQuickEditCapital.style.color = "var(--accent-cyan)";
                elements.btnQuickEditCapital.style.opacity = "1";
                elements.btnQuickEditCapital.title = "Nhấp để đổi số vốn ban đầu của tài khoản này";
            }
        }
    }

    function showCapitalEditMode() {
        if (!elements.capitalDisplayView || !elements.capitalEditView) return;
        const isAllAccounts = state.currentMt5AccountId === "all";

        if (isAllAccounts) {
            showToast("Vốn ở mục 'Tất Cả Tài Khoản' là tổng hợp tự động từ các tài khoản con. Vui lòng chọn một tài khoản cụ thể bên dưới để sửa vốn ban đầu!", "info");
            return;
        }

        const currentVal = state.stats && state.stats.initial_capital ? state.stats.initial_capital : 1000;
        elements.inputInitialCapital.value = currentVal;
        elements.capitalDisplayView.style.display = "none";
        elements.capitalEditView.style.display = "block";
        elements.inputInitialCapital.focus();
        elements.inputInitialCapital.select();
    }

    function hideCapitalEditMode() {
        if (!elements.capitalDisplayView || !elements.capitalEditView) return;
        elements.capitalEditView.style.display = "none";
        elements.capitalDisplayView.style.display = "";
    }

    async function handleSaveCapital() {
        const newCapital = parseFloat(elements.inputInitialCapital.value);
        if (isNaN(newCapital) || newCapital < 0) {
            showToast("Vui lòng nhập số vốn hợp lệ (>= 0)!", "error");
            return;
        }
        try {
            elements.btnSaveCapital.disabled = true;
            elements.btnSaveCapital.textContent = "...";

            if (state.currentMt5AccountId && state.currentMt5AccountId !== "all") {
                // Lưu vốn ban đầu cho tài khoản con Quỹ / Sàn cụ thể
                const res = await authFetch(`/api/mt5/accounts/${state.currentMt5AccountId}/initial-capital`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ initial_capital: newCapital })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Không thể lưu số vốn");
                showToast("Đã cập nhật số vốn ban đầu của tài khoản thành công!", "success");
                await loadMt5Accounts();
            } else {
                // Fallback nếu chưa có tài khoản con
                const res = await authFetch("/api/user/capital", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ initial_capital: newCapital })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Không thể lưu số vốn");
                showToast("Đã cập nhật số vốn ban đầu thành công!", "success");
            }

            hideCapitalEditMode();
            await loadStats();
        } catch (err) {
            showToast(err.message, "error");
        } finally {
            elements.btnSaveCapital.disabled = false;
            elements.btnSaveCapital.textContent = "Lưu";
        }
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

    // ==========================================
    // TRADES JOURNAL TABLE VIEW
    // ==========================================
    async function loadTrades() {
        try {
            const params = new URLSearchParams();
            if (elements.filterSearch && elements.filterSearch.value.trim()) params.append("search", elements.filterSearch.value.trim());
            if (elements.filterSymbol && elements.filterSymbol.value !== "Tất cả") params.append("symbol", elements.filterSymbol.value);
            if (elements.filterStatus && elements.filterStatus.value !== "Tất cả") params.append("status", elements.filterStatus.value);
            if (elements.filterResult && elements.filterResult.value !== "Tất cả") params.append("result", elements.filterResult.value);
            // filterStrategy removed
            if (state.currentMt5AccountId && state.currentMt5AccountId !== "all") {
                params.append("mt5_account_id", state.currentMt5AccountId);
            }

            const res = await authFetch(`/api/trades?${params.toString()}`);
            if (res.status === 401) {
                showAuthModal();
                return;
            }
            const trades = await res.json();
            state.trades = trades;

            renderTradesTable(trades);
            if (elements.totalTradesCounter) {
                elements.totalTradesCounter.textContent = trades.length;
            }
            if (elements.bnavTradeCounter) {
                elements.bnavTradeCounter.textContent = trades.length;
            }
            if (elements.filterStatsLabel) {
                elements.filterStatsLabel.textContent = `Đang hiển thị ${trades.length} lệnh`;
            }
        } catch (err) {
            console.error("Lỗi nạp danh sách lệnh:", err);
        }
    }

    function renderTradesTable(trades) {
        if (!trades || trades.length === 0) {
            elements.tradesTbody.innerHTML = "";
            if (elements.tradesCardsContainer) {
                elements.tradesCardsContainer.innerHTML = "";
            }
            elements.tradesEmptyState.style.display = "block";
            return;
        }

        elements.tradesEmptyState.style.display = "none";

        const rows = [];
        const cards = [];

        trades.forEach((t, index) => {
            const isLong = (t.trade_type || "Long").toLowerCase() === "long";
            const typeBadge = `<span class="badge ${isLong ? 'badge-long' : 'badge-short'}">${isLong ? '↗ LONG' : '↘ SHORT'}</span>`;

            const isFutures = (t.market_type || "Futures") === "Futures";
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
                const chartUrl = formatChartUrl(t.chart_image_path);
                chartHtml = `<img src="${chartUrl}" class="chart-thumb" alt="Chart" data-src="${chartUrl}" title="Nhấn để phóng to" loading="lazy" decoding="async">`;
            }

            const dateStr = t.entry_date ? t.entry_date.substring(5, 16) : "-";
            const displayId = trades.length - index;

            const fees = Number(t.fees || 0);
            let feesHtml = '<span class="text-muted mono" style="font-size:12px;">$0.00</span>';
            if (fees > 0) {
                feesHtml = `<span class="mono text-loss font-bold" style="font-size:12px;" title="Phí hoa hồng & phí qua đêm (Swap)">-$${fees.toFixed(2)}</span>`;
            } else if (fees < 0) {
                feesHtml = `<span class="mono text-win font-bold" style="font-size:12px;" title="Lãi qua đêm (Positive swap)">+$${Math.abs(fees).toFixed(2)}</span>`;
            }

            // Desktop Table Row
            rows.push(`
                <tr data-trade-id="${t.id}" data-stt="${displayId}" style="cursor: pointer;">
                    <td class="mono text-muted">#${displayId}</td>
                    <td><strong class="font-bold">${t.symbol}</strong> <span class="text-muted" style="font-size:11px;">${t.timeframe || ''}</span></td>
                    <td>${typeBadge}</td>
                    <td>${statusBadge}</td>
                    <td class="mono font-bold">$${(t.entry_price || 0).toLocaleString()}</td>
                    <td class="mono font-bold">${t.exit_price ? '$' + Number(t.exit_price).toLocaleString() : '-'}</td>
                    <td>${feesHtml}</td>
                    <td>${pnlHtml}</td>
                    <td>${roiHtml}</td>
                    <td>${rrHtml}</td>
                    <td>${chartHtml}</td>
                    <td class="text-muted" style="font-size:11px;">${dateStr}</td>
                    <td>
                        <div class="row-actions">
                            <button type="button" class="action-btn btn-edit" data-id="${t.id}" data-stt="${displayId}" title="Chỉnh sửa">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                            </button>
                            <button type="button" class="action-btn btn-delete" data-id="${t.id}" title="Xóa lệnh">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
                            </button>
                        </div>
                    </td>
                </tr>
            `);

            // Mobile Card
            if (elements.tradesCardsContainer) {
                const cardPnlClass = t.status === "Open" ? "card-open" : pnl > 0 ? "card-win" : pnl < 0 ? "card-loss" : "card-be";
                let pnlCardHtml = "-";
                let roiCardHtml = "-";
                if (t.status === "Closed") {
                    const pnlSign = pnl >= 0 ? "+" : "";
                    const pnlColorClass = pnl >= 0 ? "text-win" : "text-loss";
                    pnlCardHtml = `<span class="${pnlColorClass} font-bold">${pnlSign}$${pnl.toFixed(2)}</span>`;
                    roiCardHtml = `<span class="tc-roi-pill ${pnl >= 0 ? 'badge-long' : 'badge-short'}">${pnlSign}${pnlPercent.toFixed(2)}%</span>`;
                } else if (t.status === "Open") {
                    pnlCardHtml = `<span class="badge badge-open">Đang chạy</span>`;
                    roiCardHtml = `<span>-</span>`;
                }

                let chartCardHtml = "";
                if (t.chart_image_path) {
                    const chartUrl = formatChartUrl(t.chart_image_path);
                    chartCardHtml = `
                        <div class="tc-chart-row">
                            <img src="${chartUrl}" class="tc-chart-thumb chart-thumb" alt="Chart" data-src="${chartUrl}" title="Nhấn để phóng to" loading="lazy" decoding="async">
                        </div>
                    `;
                }

                cards.push(`
                    <div class="trade-card ${cardPnlClass}" data-trade-id="${t.id}" data-stt="${displayId}" style="cursor: pointer;">
                        <div class="tc-top-row">
                            <div class="tc-symbol-group">
                                <span class="tc-symbol">${t.symbol}</span>
                                ${t.timeframe ? `<span class="tc-timeframe">${t.timeframe}</span>` : ''}
                            </div>
                            <div class="tc-badges-group">
                                ${typeBadge}
                                ${statusBadge}
                            </div>
                        </div>
                        <div class="tc-metrics-grid">
                            <div class="tc-metric-item">
                                <span class="tc-metric-label">Giá Vào / Ra</span>
                                <span class="tc-metric-value mono">$${(t.entry_price || 0).toLocaleString()} ➔ ${t.exit_price ? '$' + Number(t.exit_price).toLocaleString() : '-'}</span>
                            </div>
                            <div class="tc-metric-item">
                                <span class="tc-metric-label">Phí & Swap</span>
                                <span class="tc-metric-value mono">${fees > 0 ? `<span class="text-loss font-bold">-$${fees.toFixed(2)}</span>` : (fees < 0 ? `<span class="text-win font-bold">+$${Math.abs(fees).toFixed(2)}</span>` : '<span class="text-muted">$0.00</span>')}</span>
                            </div>
                            <div class="tc-metric-item">
                                <span class="tc-metric-label">Tỷ Lệ R:R</span>
                                <span class="tc-metric-value mono">${rrHtml}</span>
                            </div>
                            <div class="tc-metric-item">
                                <span class="tc-metric-label">Rủi Ro (SL)</span>
                                <span class="tc-metric-value mono">${t.risk_amount > 0 ? `<span class="text-loss font-bold">-$${Number(t.risk_amount).toFixed(2)}</span>` : '<span class="text-muted">-</span>'}</span>
                            </div>
                            <div class="tc-pnl-box">
                                <div>
                                    <div class="tc-metric-label">PnL Ròng</div>
                                    <div class="tc-pnl-number mono">${pnlCardHtml}</div>
                                </div>
                                <div>
                                    ${roiCardHtml}
                                </div>
                            </div>
                        </div>
                        ${chartCardHtml}
                        <div class="tc-footer">
                            <span class="tc-date-text">🕒 ${dateStr}</span>
                            <div class="tc-actions-btns">
                                <button type="button" class="tc-btn tc-btn-edit btn-edit" data-id="${t.id}" data-stt="${displayId}" title="Chỉnh sửa">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                                    <span>Sửa</span>
                                </button>
                                <button type="button" class="tc-btn tc-btn-delete btn-delete" data-id="${t.id}" title="Xóa lệnh">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                                    <span>Xóa</span>
                                </button>
                            </div>
                        </div>
                    </div>
                `);
            }
        });

        elements.tradesTbody.innerHTML = rows.join("");
        if (elements.tradesCardsContainer) {
            elements.tradesCardsContainer.innerHTML = cards.join("");
        }
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

        const cellsHtml = [];
        const prevMonthLastDay = new Date(year, month, 0).getDate();
        for (let i = startingDay - 1; i >= 0; i--) {
            cellsHtml.push(`<div class="cal-day-cell other-month"><span class="cal-day-number">${prevMonthLastDay - i}</span></div>`);
        }

        for (let d = 1; d <= totalDays; d++) {
            const dStr = String(d).padStart(2, "0");
            const mStr = String(month + 1).padStart(2, "0");
            const dayKey = `${year}-${mStr}-${dStr}`;
            const info = dailyData[dayKey];

            if (info) {
                const isWin = info.pnl >= 0;
                const winClass = isWin ? "day-win" : "day-loss";
                const pnlClass = isWin ? "text-win" : "text-loss";
                
                const absPnl = Math.abs(info.pnl);
                let pnlStr = "";
                if (absPnl >= 1000) {
                    pnlStr = (info.pnl / 1000).toFixed(1) + "k";
                } else if (absPnl >= 100) {
                    pnlStr = info.pnl.toFixed(0);
                } else {
                    pnlStr = info.pnl.toFixed(1);
                }
                const formattedPnl = (isWin ? "+" : "") + "$" + pnlStr;

                cellsHtml.push(`
                    <div class="cal-day-cell ${winClass}">
                        <div class="cal-cell-top">
                            <span class="cal-day-number font-bold">${d}</span>
                            <span class="cal-day-trades hide-mobile">${info.wins}W-${info.losses}L</span>
                        </div>
                        <div class="cal-day-pnl ${pnlClass}">
                            ${formattedPnl}
                        </div>
                        <div class="cal-day-trades hide-mobile">${info.count} lệnh</div>
                    </div>
                `);
            } else {
                cellsHtml.push(`
                    <div class="cal-day-cell">
                        <div class="cal-cell-top">
                            <span class="cal-day-number">${d}</span>
                        </div>
                    </div>
                `);
            }
        }

        elements.calendarDaysGrid.innerHTML = cellsHtml.join("");
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

        elements.formPositionSize.value = "100";
        elements.formFees.value = "0";
        elements.formLeverage.value = "10";
        elements.formMarketType.value = "Futures";
        elements.formSymbol.value = "BTC/USDT";
        if (elements.formAccountId) {
            if (state.currentMt5AccountId && state.currentMt5AccountId !== "all") {
                elements.formAccountId.value = String(state.currentMt5AccountId);
            } else {
                elements.formAccountId.value = "";
            }
        }
        if (elements.formRiskAmount) elements.formRiskAmount.value = "";
        if (elements.formPlannedReward) elements.formPlannedReward.value = "$0.00";

        document.querySelectorAll(".symbol-pick-btn").forEach(b => {
            if (b.getAttribute("data-symbol") === "BTC/USDT") b.classList.add("active");
            else b.classList.remove("active");
        });

        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        elements.formEntryDate.value = now.toISOString().slice(0, 16);

        resetDropzone();
        updateFormLiveCalculations();
        openModalElement(elements.modalTradeForm);
    }

    function populateTradeForm(trade, displayId = null) {
        elements.formTradeId.value = trade.id;
        const titleStt = displayId ? `#${displayId} ` : '';
        elements.tradeModalTitle.textContent = `Chỉnh Sửa Lệnh ${titleStt}(${trade.symbol})`;
        elements.btnSaveText.textContent = "Cập Nhật Lệnh";

        elements.formSymbol.value = trade.symbol || "BTC/USDT";
        document.querySelectorAll(".symbol-pick-btn").forEach(b => {
            if (b.getAttribute("data-symbol") === (trade.symbol || "BTC/USDT")) b.classList.add("active");
            else b.classList.remove("active");
        });
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
        if (elements.formAccountId) {
            elements.formAccountId.value = trade.mt5_account_id ? String(trade.mt5_account_id) : "";
        }

        if (elements.formRiskAmount) {
            elements.formRiskAmount.value = (trade.risk_amount && trade.risk_amount > 0) ? trade.risk_amount : "";
        }

        elements.formStrategy.value = trade.strategy || "";
        elements.formEmotion.value = trade.emotion || "";
        elements.formNotes.value = trade.notes || "";
        elements.formLessons.value = trade.lessons || "";

        if (trade.chart_image_path) {
            const chartUrl = formatChartUrl(trade.chart_image_path);
            setDropzonePreview(chartUrl, trade.chart_image_path);
        } else {
            resetDropzone();
        }

        updateFormLiveCalculations();
        openModalElement(elements.modalTradeForm);
    }

    async function openEditModal(tradeId, displayId = null) {
        // Ưu tiên tìm ngay trong state.trades đã có -> Phản hồi tức thì 0ms!
        let trade = state.trades.find(t => String(t.id) === String(tradeId));
        if (trade) {
            populateTradeForm(trade, displayId);
            return;
        }

        try {
            const res = await authFetch(`/api/trades/${tradeId}`);
            if (res.status === 401) {
                showAuthModal();
                return;
            }
            if (!res.ok) throw new Error("Không tìm thấy lệnh");
            trade = await res.json();
            populateTradeForm(trade, displayId);
        } catch (err) {
            showToast(err.message, "error");
        }
    }

    function closeTradeModal() {
        closeModalElement(elements.modalTradeForm);
    }

    async function handleSaveTrade(e) {
        e.preventDefault();

        const tradeId = elements.formTradeId.value;
        const accountId = elements.formAccountId ? elements.formAccountId.value : "";
        const payload = {
            mt5_account_id: accountId ? parseInt(accountId) : null,
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
            risk_amount: (elements.formRiskAmount && elements.formRiskAmount.value) ? (parseFloat(elements.formRiskAmount.value) || 0) : 0,
            exit_price: elements.formExitPrice.value ? parseFloat(elements.formExitPrice.value) : null,
            position_size: parseFloat(elements.formPositionSize.value) || 100,
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

            const res = await authFetch(url, {
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
            const res = await authFetch(`/api/trades/${tradeId}`, { method: "DELETE" });
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
        const riskAmount = (elements.formRiskAmount && elements.formRiskAmount.value) ? (parseFloat(elements.formRiskAmount.value) || 0) : 0;
        const margin = parseFloat(elements.formPositionSize.value) || 100;
        const lev = parseInt(elements.formLeverage.value) || 1;
        const fees = parseFloat(elements.formFees.value) || 0;

        let plannedRr = 0;
        let plannedReward = 0;
        let realizedRr = 0;
        let pnl = 0;
        let roi = 0;

        let riskDistance = 0;
        if (entry > 0 && sl && sl > 0) {
            riskDistance = isLong ? (entry - sl) : (sl - entry);
        }

        if (riskDistance > 0 && tp && tp > 0) {
            let rewardDistance = isLong ? (tp - entry) : (entry - tp);
            if (rewardDistance > 0) {
                plannedRr = rewardDistance / riskDistance;
                if (riskAmount > 0) {
                    plannedReward = plannedRr * riskAmount;
                }
            }
        }

        // Cập nhật ô hiển thị lợi nhuận dự kiến tại TP
        if (elements.formPlannedReward) {
            if (plannedReward > 0) {
                elements.formPlannedReward.value = `+$${plannedReward.toFixed(2)}`;
            } else {
                elements.formPlannedReward.value = "$0.00";
            }
        }

        // Cập nhật ô số tiền mất nếu dính SL và lãi nếu TP trong Live Calc Grid
        if (elements.liveRiskVal) {
            elements.liveRiskVal.textContent = riskAmount > 0 ? `-$${riskAmount.toFixed(2)}` : "-";
        }
        if (elements.liveRewardVal) {
            elements.liveRewardVal.textContent = plannedReward > 0 ? `+$${plannedReward.toFixed(2)}` : "-";
        }

        // Tính toán Realized R:R và Lợi Nhuận Net (khi đã có giá thoát)
        if (entry > 0 && exit && exit > 0) {
            if (riskDistance > 0) {
                let realizedDiff = isLong ? (exit - entry) : (entry - exit);
                realizedRr = realizedDiff / riskDistance;
            }

            // CƠ CHẾ CHÍNH: TÍNH THEO SỐ TIỀN MẤT CHO STOPLOSS (RISK AMOUNT $)
            if (riskAmount > 0 && riskDistance > 0) {
                let rawPnl = realizedRr * riskAmount;
                pnl = rawPnl - fees;
                roi = (pnl / riskAmount) * 100;
            } else if (margin > 0) {
                // Cơ chế dự phòng: Theo Margin & Đòn bẩy
                let priceChangeRatio = isLong ? (exit - entry) / entry : (entry - exit) / entry;
                let rawPnl = priceChangeRatio * (margin * lev);
                pnl = rawPnl - fees;
                roi = (pnl / margin) * 100;
            }
        }

        elements.livePlannedRr.textContent = plannedRr > 0 ? `1 : ${plannedRr.toFixed(2)}` : "-";
        elements.liveRealizedRr.textContent = (exit && exit > 0 && realizedRr !== 0) ? `${realizedRr >= 0 ? '+' : ''}${realizedRr.toFixed(2)}R` : "-";
        
        const pnlEl = elements.livePnl;
        const roiEl = elements.liveRoi;

        if (exit && exit > 0) {
            pnlEl.textContent = `${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}`;
            roiEl.textContent = `${roi >= 0 ? '+' : ''}${roi.toFixed(2)}%`;
            pnlEl.className = `live-item-val font-bold ${pnl > 0 ? 'text-win' : pnl < 0 ? 'text-loss' : 'text-be'}`;
            roiEl.className = `live-item-val font-bold ${roi > 0 ? 'text-win' : roi < 0 ? 'text-loss' : 'text-be'}`;
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
            const res = await authFetch("/api/upload-chart", {
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
        if (!src) return;
        elements.lightboxImg.src = src;
        openModalElement(elements.modalLightbox);
    }

    function closeLightbox() {
        closeModalElement(elements.modalLightbox);
        elements.lightboxImg.src = "";
    }


    function escapeHtml(str) {
        if (str === null || str === undefined) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // ==========================================
    // MT5 MULTI-ACCOUNT MANAGEMENT & SWITCHER
    // ==========================================
    async function loadMt5Accounts() {
        try {
            const res = await authFetch("/api/mt5/accounts");
            if (!res.ok) return;
            const accounts = await res.json();
            state.mt5Accounts = accounts;

            renderMt5AccountDropdown(accounts);
            renderMt5AccountCards(accounts);
        } catch (err) {
            console.error("Lỗi nạp danh sách MT5:", err);
        }
    }

    function renderMt5AccountDropdown(accounts) {
        const listEl = document.getElementById("dropdown-account-list");
        const labelEl = document.getElementById("current-account-label");
        const badgeEl = document.getElementById("account-badge-pill");
        if (!listEl) return;

        listEl.innerHTML = "";

        // 1. Mục "Tất cả tài khoản" (Tổng hợp toàn bộ danh mục)
        const allItem = document.createElement("button");
        allItem.type = "button";
        allItem.className = `dropdown-account-item ${state.currentMt5AccountId === "all" ? "selected" : ""}`;
        allItem.innerHTML = `
            <div class="dropdown-account-info">
                <span class="dropdown-account-title">📊 Tất Cả Tài Khoản</span>
                <span class="dropdown-account-sub">Xem tổng hợp danh mục</span>
            </div>
            ${state.currentMt5AccountId === "all" ? '<span style="color:var(--accent-cyan); font-weight:bold;">✓</span>' : ''}
        `;
        allItem.addEventListener("click", () => switchMt5Account("all"));
        listEl.appendChild(allItem);

        // 2. Header phân cách: "Tài Khoản Quỹ & Sàn Giao Dịch"
        const sep = document.createElement("div");
        sep.style.cssText = "padding: 10px 12px 6px 12px; font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;";
        sep.textContent = "Tài Khoản Quỹ & Sàn Giao Dịch";
        listEl.appendChild(sep);

        let activeAccount = null;

        if (!accounts || accounts.length === 0) {
            const emptyTip = document.createElement("div");
            emptyTip.style.cssText = "padding: 10px 12px; font-size: 12px; color: var(--text-muted);";
            emptyTip.textContent = "Chưa có tài khoản con nào. Bấm '+ Quản lý / Thêm Tài Khoản...' bên dưới để tạo.";
            listEl.appendChild(emptyTip);
        } else {
            // Các tài khoản con cụ thể (The5ers, FTMO, Binance, Ghi tay...)
            accounts.forEach(acc => {
                const isSelected = String(state.currentMt5AccountId) === String(acc.id);
                if (isSelected) activeAccount = acc;

                const item = document.createElement("button");
                item.type = "button";
                item.className = `dropdown-account-item ${isSelected ? "selected" : ""}`;
                item.innerHTML = `
                    <div class="dropdown-account-info">
                        <span class="dropdown-account-title">📈 ${escapeHtml(acc.account_name)}</span>
                        <span class="dropdown-account-sub">${escapeHtml(acc.server)} #${escapeHtml(acc.login)}</span>
                    </div>
                    <div style="text-align: right;">
                        <span class="dropdown-account-balance">$${Number(acc.balance || 0).toLocaleString("en-US", {minimumFractionDigits: 0, maximumFractionDigits: 2})}</span>
                        ${isSelected ? '<span style="color:var(--accent-cyan); font-weight:bold; margin-left: 6px;">✓</span>' : ''}
                    </div>
                `;
                item.addEventListener("click", () => switchMt5Account(acc.id));
                listEl.appendChild(item);
            });
        }

        // Cập nhật nhãn và badge trên thanh Header
        if (labelEl) {
            if (activeAccount) {
                labelEl.textContent = `${activeAccount.account_name} ($${Number(activeAccount.balance || 0).toLocaleString("en-US", {maximumFractionDigits: 0})})`;
            } else {
                labelEl.textContent = "Tất Cả Tài Khoản";
            }
        }
        if (badgeEl) {
            if (activeAccount) {
                const s = (activeAccount.server || "").toLowerCase();
                if (s.includes("binance") || s.includes("okx") || s.includes("bybit")) {
                    badgeEl.textContent = "SÀN";
                } else if (s.includes("ftmo") || s.includes("the5ers") || s.includes("fivepercent") || s.includes("fund")) {
                    badgeEl.textContent = "QUỸ";
                } else {
                    badgeEl.textContent = "TÀI KHOẢN";
                }
            } else {
                badgeEl.textContent = "QUỸ & SÀN";
            }
        }

        // Cập nhật options cho Dropdown Tài Khoản trong Modal Thêm/Sửa Lệnh
        const formAccSelect = document.getElementById("form-account-id");
        if (formAccSelect) {
            const currentSelected = formAccSelect.value;
            formAccSelect.innerHTML = '<option value="">-- Mặc định (Tất cả tài khoản) --</option>';
            if (accounts && accounts.length > 0) {
                accounts.forEach(acc => {
                    const opt = document.createElement("option");
                    opt.value = acc.id;
                    opt.textContent = `📈 ${acc.account_name} (${acc.server})`;
                    formAccSelect.appendChild(opt);
                });
            }
            if (currentSelected) {
                formAccSelect.value = currentSelected;
            }
        }
    }

    function renderMt5AccountCards(accounts) {
        const container = document.getElementById("mt5-account-cards-list");
        const badge = document.getElementById("mt5-account-count-badge");
        if (!container) return;

        if (badge) badge.textContent = `${accounts.length} tài khoản`;
        container.innerHTML = "";

        if (accounts.length === 0) {
            container.innerHTML = `<div style="text-align: center; color: var(--text-muted); font-size: 12px; padding: 12px;">Chưa có tài khoản nào được kết nối / tạo sẵn. Bấm bên dưới để thêm.</div>`;
            return;
        }

        accounts.forEach(acc => {
            const card = document.createElement("div");
            card.className = "mt5-card-item";
            const initialCapVal = acc.initial_capital || acc.balance || 0;
            const isAccLinked = Boolean(acc.is_linked || (acc.server && acc.server.toLowerCase() !== "manual" && Number(acc.balance || 0) > 0));
            const typeBadge = isAccLinked 
                ? '<span style="display:inline-block; font-size:10.5px; padding:1px 6px; border-radius:4px; background:rgba(56,189,248,0.12); color:var(--accent-cyan); font-weight:600; margin-left:6px;">🔒 Đồng bộ sàn</span>'
                : '<span style="display:inline-block; font-size:10.5px; padding:1px 6px; border-radius:4px; background:rgba(255,255,255,0.07); color:var(--text-muted); font-weight:600; margin-left:6px;">✍️ Thủ công</span>';

            card.innerHTML = `
                <div class="mt5-card-details">
                    <div class="mt5-card-title">${escapeHtml(acc.account_name)} ${typeBadge}</div>
                    <div class="mt5-card-meta">
                        ${escapeHtml(acc.server)} • ID: <code>${escapeHtml(acc.login)}</code> • Vốn đầu: <strong style="color:var(--accent-cyan);">$${Number(initialCapVal).toLocaleString("en-US", {minimumFractionDigits: 0, maximumFractionDigits: 2})}</strong>
                    </div>
                </div>
                <div class="mt5-card-right">
                    <span class="mt5-card-balance" title="Số dư hiện tại">$${Number(acc.balance || 0).toLocaleString("en-US", {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                    <button type="button" class="btn-delete-mt5" title="Xóa kết nối tài khoản này" data-id="${acc.id}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                    </button>
                </div>
            `;
            
            const btnDel = card.querySelector(".btn-delete-mt5");
            if (btnDel) {
                btnDel.addEventListener("click", async (e) => {
                    e.stopPropagation();
                    if (!confirm(`Bạn có chắc muốn xóa tài khoản "${acc.account_name}"? Toàn bộ các lệnh thuộc tài khoản này cũng sẽ bị hủy bỏ vĩnh viễn.`)) return;
                    try {
                        const res = await authFetch(`/api/mt5/accounts/${acc.id}`, { method: "DELETE" });
                        if (res.ok) {
                            showToast("Đã xóa tài khoản!", "info");
                            if (String(state.currentMt5AccountId) === String(acc.id)) {
                                state.currentMt5AccountId = "all";
                                localStorage.setItem("active_mt5_account_id", "all");
                            }
                            await loadMt5Accounts();
                            await refreshAllData();
                        }
                    } catch (err) {
                        showToast("Lỗi xóa tài khoản", "error");
                    }
                });
            }
            container.appendChild(card);
        });
    }

    async function switchMt5Account(accountId) {
        state.currentMt5AccountId = accountId;
        localStorage.setItem("active_mt5_account_id", accountId);

        // Đóng dropdown menu
        const menu = document.getElementById("account-dropdown-menu");
        if (menu) menu.classList.remove("active");

        // Cập nhật lại giao diện dropdown
        renderMt5AccountDropdown(state.mt5Accounts);

        // Thông báo chuyển đổi
        let accName = "Tất Cả Tài Khoản";
        const targetAcc = state.mt5Accounts.find(a => String(a.id) === String(accountId));
        if (targetAcc) accName = targetAcc.account_name;
        showToast(`Đã chuyển sang: ${accName}`, "success");

        // Tải lại toàn bộ dữ liệu chỉ của tài khoản này
        await refreshAllData();
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

                    const res = await authFetch("/api/auth/reset-password", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ username, new_password: newPassword })
                    });
                    const data = await res.json();

                    if (!res.ok) {
                        showAuthAlert(data.error || "Không thể đặt lại mật khẩu!");
                        return;
                    }

                    if (data.token) {
                        localStorage.setItem("cj_auth_token", data.token);
                    }
                    if (data.user) {
                        localStorage.setItem("cj_user", JSON.stringify(data.user));
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

        // Trade Actions
        elements.btnOpenAddTrade.addEventListener("click", openAddModal);
        elements.btnEmptyAddTrade.addEventListener("click", openAddModal);
        elements.btnCloseTradeModal.addEventListener("click", closeTradeModal);
        elements.btnCancelTrade.addEventListener("click", closeTradeModal);

        // Symbol Pick Buttons & Quick Chips
        document.querySelectorAll(".symbol-pick-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                selectTradeSymbol(btn.getAttribute("data-symbol"));
            });
        });

        document.querySelectorAll(".quick-symbol-chip").forEach(chip => {
            chip.addEventListener("click", () => {
                const sym = chip.getAttribute("data-symbol");
                if (sym) {
                    selectTradeSymbol(sym);
                    if (elements.formSymbol) {
                        elements.formSymbol.style.boxShadow = "0 0 10px rgba(0, 245, 155, 0.5)";
                        setTimeout(() => { elements.formSymbol.style.boxShadow = ""; }, 300);
                    }
                }
            });
        });

        // Event Delegation cho Bảng lệnh (Desktop) - 1 Listener duy nhất, siêu mượt
        if (elements.tradesTbody) {
            elements.tradesTbody.addEventListener("click", (e) => {
                const deleteBtn = e.target.closest(".btn-delete");
                if (deleteBtn) {
                    e.stopPropagation();
                    handleDeleteTrade(deleteBtn.getAttribute("data-id"));
                    return;
                }
                const editBtn = e.target.closest(".btn-edit");
                if (editBtn) {
                    e.stopPropagation();
                    openEditModal(editBtn.getAttribute("data-id"), editBtn.getAttribute("data-stt"));
                    return;
                }
                const thumb = e.target.closest(".chart-thumb");
                if (thumb) {
                    e.stopPropagation();
                    openLightbox(thumb.getAttribute("data-src"));
                    return;
                }
                const row = e.target.closest("tr");
                if (row && row.getAttribute("data-trade-id")) {
                    openEditModal(row.getAttribute("data-trade-id"), row.getAttribute("data-stt"));
                }
            });
        }

        // Event Delegation cho Thẻ lệnh (Mobile) - 1 Listener duy nhất
        if (elements.tradesCardsContainer) {
            elements.tradesCardsContainer.addEventListener("click", (e) => {
                const deleteBtn = e.target.closest(".btn-delete, .tc-btn-delete");
                if (deleteBtn) {
                    e.stopPropagation();
                    handleDeleteTrade(deleteBtn.getAttribute("data-id"));
                    return;
                }
                const editBtn = e.target.closest(".btn-edit, .tc-btn-edit");
                if (editBtn) {
                    e.stopPropagation();
                    openEditModal(editBtn.getAttribute("data-id"), editBtn.getAttribute("data-stt"));
                    return;
                }
                const thumb = e.target.closest(".chart-thumb");
                if (thumb) {
                    e.stopPropagation();
                    openLightbox(thumb.getAttribute("data-src"));
                    return;
                }
                const card = e.target.closest(".trade-card");
                if (card && card.getAttribute("data-trade-id")) {
                    openEditModal(card.getAttribute("data-trade-id"), card.getAttribute("data-stt"));
                }
            });
        }

        // Mobile Navigation & View Switcher Wiring
        const mobileNavItems = document.querySelectorAll(".mobile-nav-item");
        const btnMobileQuickAdd = document.getElementById("btn-mobile-quick-add");
        const btnMobileCamera = document.getElementById("btn-mobile-camera");
        const fileChartInput = document.getElementById("file-chart-input");

        function switchAppTab(targetTab) {
            if (state.currentTab === targetTab) return;
            state.currentTab = targetTab;

            elements.tabBtns.forEach(b => {
                if (b.getAttribute("data-tab") === targetTab) b.classList.add("active");
                else b.classList.remove("active");
            });

            mobileNavItems.forEach(b => {
                if (b.getAttribute("data-tab") === targetTab) b.classList.add("active");
                else b.classList.remove("active");
            });

            elements.tabViews.forEach(v => {
                if (v.id === `view-${targetTab}`) {
                    v.classList.add("active");
                } else {
                    v.classList.remove("active");
                }
            });

            if (targetTab === "calendar") {
                renderCalendar();
            } else if (targetTab === "dashboard" && state.chartInstance) {
                requestAnimationFrame(() => {
                    if (state.chartInstance) state.chartInstance.resize();
                });
            }
            if (window.scrollY > 40) {
                window.scrollTo(0, 0);
            }
        }

        // Connect desktop tabs to switchAppTab
        elements.tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                switchAppTab(btn.getAttribute("data-tab"));
            });
        });

        // Connect mobile bottom navigation items
        mobileNavItems.forEach(item => {
            item.addEventListener("click", () => {
                switchAppTab(item.getAttribute("data-tab"));
            });
        });

        if (btnMobileQuickAdd) {
            btnMobileQuickAdd.addEventListener("click", openAddModal);
        }

        if (btnMobileCamera && fileChartInput) {
            btnMobileCamera.addEventListener("click", (e) => {
                e.preventDefault();
                e.stopPropagation();
                fileChartInput.click();
            });
        }

        // View Mode Switcher (Card View vs Table View)
        const btnViewCards = document.getElementById("btn-view-cards");
        const btnViewTable = document.getElementById("btn-view-table");
        const cardsContainer = document.getElementById("trades-cards-container");
        const tableContainer = document.querySelector(".table-container");

        if (btnViewCards && btnViewTable && cardsContainer && tableContainer) {
            btnViewCards.addEventListener("click", () => {
                btnViewCards.classList.add("active");
                btnViewTable.classList.remove("active");
                cardsContainer.classList.remove("hide-cards");
                tableContainer.classList.add("hide-table");
                localStorage.setItem("preferred_trade_view", "cards");
            });

            btnViewTable.addEventListener("click", () => {
                btnViewTable.classList.add("active");
                btnViewCards.classList.remove("active");
                cardsContainer.classList.add("hide-cards");
                tableContainer.classList.remove("hide-table");
                localStorage.setItem("preferred_trade_view", "table");
            });

            // Khởi tạo chế độ xem phù hợp cho từng thiết bị
            const savedView = localStorage.getItem("preferred_trade_view");
            if (window.innerWidth <= 768) {
                if (savedView === "table") {
                    btnViewTable.click();
                } else {
                    btnViewCards.click();
                }
            } else {
                if (savedView === "cards") {
                    btnViewCards.click();
                } else {
                    btnViewTable.click();
                }
            }
        }

        elements.tradeForm.addEventListener("submit", handleSaveTrade);

        // Lắng nghe thay đổi các trường giá và số tiền rủi ro trong form
        [
            elements.formEntryPrice, elements.formExitPrice, elements.formStopLoss,
            elements.formTakeProfit, elements.formRiskAmount, elements.formPositionSize, elements.formLeverage,
            elements.formFees, elements.typeLong, elements.typeShort
        ].filter(Boolean).forEach(input => {
            input.addEventListener("input", updateFormLiveCalculations);
            input.addEventListener("change", updateFormLiveCalculations);
        });

        // Lắng nghe sự kiện chỉnh sửa số vốn ban đầu (Dashboard Capital)
        if (elements.btnQuickEditCapital) {
            elements.btnQuickEditCapital.addEventListener("click", () => {
                if (state.currentMt5AccountId === "all") return;
                if (state.stats && state.stats.is_linked) {
                    showToast("Tài khoản này được đồng bộ trực tiếp từ sàn, vốn ban đầu được bảo toàn tự động và khóa chỉnh sửa.", "info");
                    return;
                }
                showCapitalEditMode();
            });
        }
        if (elements.btnCancelCapital) {
            elements.btnCancelCapital.addEventListener("click", hideCapitalEditMode);
        }
        if (elements.btnSaveCapital) {
            elements.btnSaveCapital.addEventListener("click", handleSaveCapital);
        }
        if (elements.inputInitialCapital) {
            elements.inputInitialCapital.addEventListener("keydown", (e) => {
                if (e.key === "Enter") {
                    e.preventDefault();
                    handleSaveCapital();
                } else if (e.key === "Escape") {
                    hideCapitalEditMode();
                }
            });
        }

        let debounceTimer;
        if (elements.filterSearch) {
            elements.filterSearch.addEventListener("input", () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(loadTrades, 300);
            });
        }
        [elements.filterSymbol, elements.filterStatus, elements.filterResult].filter(Boolean).forEach(select => {
            select.addEventListener("change", loadTrades);
        });
        if (elements.btnResetFilters) {
            elements.btnResetFilters.addEventListener("click", () => {
                if (elements.filterSearch) elements.filterSearch.value = "";
                if (elements.filterSymbol) elements.filterSymbol.value = "Tất cả";
                if (elements.filterStatus) elements.filterStatus.value = "Tất cả";
                if (elements.filterResult) elements.filterResult.value = "Tất cả";
                loadTrades();
            });
        }

        elements.btnExportCsv.addEventListener("click", () => {
            let url = "/api/export-csv";
            if (state.currentMt5AccountId && state.currentMt5AccountId !== "all") {
                url += `?mt5_account_id=${encodeURIComponent(state.currentMt5AccountId)}`;
            }
            window.location.href = url;
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
                } else if (modalMt5 && modalMt5.classList.contains("active")) {
                    closeMt5Modal();
                }
            }
        });


        // MT5 Account Switcher Toggle & Modal Handlers
        const btnAccountSwitcher = document.getElementById("btn-account-switcher");
        const accountDropdownMenu = document.getElementById("account-dropdown-menu");
        const modalMt5 = document.getElementById("modal-mt5-accounts");
        const btnOpenAddMt5Modal = document.getElementById("btn-open-add-mt5-modal");
        const btnCloseMt5Modal = document.getElementById("btn-close-mt5-modal");
        const btnCancelMt5 = document.getElementById("btn-cancel-mt5");
        const formAddMt5 = document.getElementById("form-add-mt5");

        if (btnAccountSwitcher && accountDropdownMenu) {
            btnAccountSwitcher.addEventListener("click", (e) => {
                e.stopPropagation();
                accountDropdownMenu.classList.toggle("active");
            });

            document.addEventListener("click", (e) => {
                if (!btnAccountSwitcher.contains(e.target) && !accountDropdownMenu.contains(e.target)) {
                    accountDropdownMenu.classList.remove("active");
                }
            });
        }

        if (btnOpenAddMt5Modal && modalMt5) {
            btnOpenAddMt5Modal.addEventListener("click", () => {
                if (accountDropdownMenu) accountDropdownMenu.classList.remove("active");
                const alertEl = document.getElementById("mt5-form-alert");
                if (alertEl) alertEl.style.display = "none";
                loadMt5Accounts();
                openModalElement(modalMt5);
            });
        }

        function closeMt5Modal() {
            if (modalMt5) closeModalElement(modalMt5);
            const alertEl = document.getElementById("mt5-form-alert");
            if (alertEl) alertEl.style.display = "none";
        }

        if (btnCloseMt5Modal) btnCloseMt5Modal.addEventListener("click", closeMt5Modal);
        if (btnCancelMt5) btnCancelMt5.addEventListener("click", closeMt5Modal);
        if (modalMt5) {
            modalMt5.addEventListener("click", (e) => {
                if (e.target === modalMt5) closeMt5Modal();
            });
        }

        if (formAddMt5) {
            formAddMt5.addEventListener("submit", async (e) => {
                e.preventDefault();
                const name = document.getElementById("mt5-account-name").value.trim();
                const server = document.getElementById("mt5-server").value.trim();
                const login = document.getElementById("mt5-login").value.trim();
                const password = document.getElementById("mt5-password").value.trim();
                const balance = parseFloat(document.getElementById("mt5-balance").value) || 0;
                const accountTypeEl = document.getElementById("mt5-account-type");
                const accountType = accountTypeEl ? accountTypeEl.value : "linked";

                const alertEl = document.getElementById("mt5-form-alert");
                if (alertEl) alertEl.style.display = "none";

                try {
                    const res = await authFetch("/api/mt5/accounts", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ 
                            account_name: name, 
                            server, 
                            login, 
                            password, 
                            balance, 
                            initial_capital: balance,
                            account_type: accountType
                        })
                    });
                    let data = {};
                    try {
                        data = await res.json();
                    } catch (jsonErr) {
                        data = { error: `Máy chủ phản hồi mã ${res.status}. Vui lòng thử lại sau giây lát!` };
                    }

                    if (!res.ok) {
                        if (alertEl) {
                            alertEl.textContent = data.error || "Thất bại!";
                            alertEl.style.display = "block";
                        }
                        return;
                    }

                    // Lưu thành công: Đóng modal và reset form ngay lập tức
                    closeMt5Modal();
                    formAddMt5.reset();
                    showToast(data.message || "Đã lưu tài khoản thành công!", "success");

                    try {
                        await loadMt5Accounts();
                        if (data.account_id) {
                            await switchMt5Account(data.account_id);
                        }
                    } catch (uiErr) {
                        console.error("Lỗi cập nhật danh sách MT5:", uiErr);
                    }
                } catch (err) {
                    if (alertEl) {
                        alertEl.textContent = "Không thể kết nối đến máy chủ Web (Backend đang khởi động hoặc mất mạng). Vui lòng thử lại sau vài giây!";
                        alertEl.style.display = "block";
                    }
                }
            });
        }

        setupDropzone();
    }

    initApp();
});
