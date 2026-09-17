/**
 * TV Europe Sales Management Portal - Unified Smart TopBar Component
 * 
 * Auto-injects a standardized top navigation bar when accessing sub-dashboards directly.
 * Features:
 * - Clean "← 포탈로 돌아가기" button linking to main portal
 * - Sub-dashboard title display & badge
 * - Iframe auto-detection (hides itself when rendered inside Portal Viewer)
 * - Stitch Strategic Insight System styling & RemixIcons
 */
(function () {
  // Check if page is loaded inside an iframe (e.g. Portal Viewer Overlay)
  const isIframe = (function () {
    try {
      return window.self !== window.top;
    } catch (e) {
      return true; // Security error means cross-origin iframe -> definitely in iframe
    }
  })();

  // If inside iframe, do NOT render standalone TopBar (Portal Viewer already provides navigation)
  if (isIframe) {
    // Hide legacy return buttons if present
    document.addEventListener('DOMContentLoaded', function () {
      const legacyBtns = document.querySelectorAll('.legacy-portal-return, #btn-return-portal-local');
      legacyBtns.forEach(el => el.style.display = 'none');
    });
    return;
  }

  function initUnifiedTopBar() {
    // 1. Inject Standard Fonts & Icons if not loaded
    if (!document.getElementById('portal-unified-fonts')) {
      const fontLink = document.createElement('link');
      fontLink.id = 'portal-unified-fonts';
      fontLink.rel = 'stylesheet';
      fontLink.href = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap';
      document.head.appendChild(fontLink);
    }

    if (!document.getElementById('portal-unified-icons')) {
      const iconLink = document.createElement('link');
      iconLink.id = 'portal-unified-icons';
      iconLink.rel = 'stylesheet';
      iconLink.href = 'https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css';
      document.head.appendChild(iconLink);
    }

    // 2. Determine Dashboard Title
    let pageTitle = document.title || 'LGE Sales Dashboard';
    pageTitle = pageTitle.replace(/Executive Portal\s*\|\s*/i, '').replace(/Dashboard\s*\|\s*/i, '');

    // 3. Create TopBar DOM Element
    const topBar = document.createElement('div');
    topBar.id = 'portal-unified-topbar';
    topBar.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 56px;
      background-color: #0F172A;
      border-bottom: 1px solid #1E293B;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      box-sizing: border-box;
      z-index: 99999;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    `;

    // Dynamic portal URL detection (local vs Firebase Hosting)
    let portalUrl = '../00. TV Europe Sales Management Portal/index.html';
    if (window.location.hostname.includes('web.app') || window.location.hostname.includes('firebase')) {
      portalUrl = 'https://tv-sales-portal-2026.web.app';
    }

    topBar.innerHTML = `
      <style>
        #portal-unified-topbar .portal-back-btn {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 7px 14px;
          background: rgba(255, 255, 255, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.18);
          border-radius: 6px;
          color: #FFFFFF;
          font-family: 'Inter', sans-serif;
          font-size: 13.5px;
          font-weight: 500;
          text-decoration: none;
          cursor: pointer;
          transition: all 0.2s ease-in-out;
          line-height: 1;
        }
        #portal-unified-topbar .portal-back-btn:hover {
          background-color: #0D9488;
          border-color: #0D9488;
          color: #FFFFFF;
          box-shadow: 0 2px 8px rgba(13, 148, 136, 0.3);
          transform: translateY(-1px);
        }
        #portal-unified-topbar .portal-dash-title {
          font-family: 'IBM Plex Sans', 'Inter', sans-serif;
          font-size: 15px;
          font-weight: 600;
          color: #F8FAFC;
          display: flex;
          align-items: center;
          gap: 10px;
        }
        #portal-unified-topbar .portal-badge {
          background-color: rgba(13, 148, 136, 0.2);
          border: 1px solid rgba(13, 148, 136, 0.4);
          color: #2DD4BF;
          font-size: 11px;
          font-weight: 600;
          padding: 2px 8px;
          border-radius: 4px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
      </style>
      
      <div style="display: flex; align-items: center; gap: 16px;">
        <a href="${portalUrl}" class="portal-back-btn" id="btn-portal-back-action">
          <i class="ri-arrow-left-line" style="font-size: 16px;"></i>
          <span id="portal-back-text">포탈로 돌아가기</span>
        </a>
      </div>

      <div class="portal-dash-title">
        <span class="portal-badge">STANDALONE VIEW</span>
        <span id="portal-title-text">${pageTitle}</span>
      </div>
    `;

    // Function to update topbar language
    function updateTopbarLanguage(lang, customTitle) {
      const backText = topBar.querySelector('#portal-back-text');
      const titleText = topBar.querySelector('#portal-title-text');
      if (backText) {
        backText.innerText = (lang === 'en') ? 'Return to Portal' : '포탈로 돌아가기';
      }
      if (titleText && customTitle) {
        titleText.innerText = customTitle;
      }
    }

    // Listen for language changes from dashboard
    window.addEventListener('dashboardLanguageChanged', function (e) {
      if (e.detail) {
        updateTopbarLanguage(e.detail.lang, e.detail.title);
      }
    });

    // Check initial language preference
    const initialLang = (new URLSearchParams(window.location.search).get('lang') || localStorage.getItem('tv_sim_lang') || 'ko');
    if (initialLang === 'en') {
      updateTopbarLanguage('en');
    }

    // Add back navigation logic
    const backBtn = topBar.querySelector('#btn-portal-back-action');
    backBtn.addEventListener('click', function (e) {
      if (window.history.length > 1 && document.referrer.includes('Portal')) {
        e.preventDefault();
        window.history.back();
      }
    });

    function applyLayoutAdjustments() {
      document.body.style.paddingTop = '56px';
      const sidebar = document.querySelector('aside');
      if (sidebar) {
        sidebar.style.top = '56px';
        sidebar.style.height = 'calc(100vh - 56px)';
      }
    }

    // Prepend to body
    if (document.body) {
      document.body.insertBefore(topBar, document.body.firstChild);
      applyLayoutAdjustments();
    } else {
      document.addEventListener('DOMContentLoaded', function () {
        document.body.insertBefore(topBar, document.body.firstChild);
        applyLayoutAdjustments();
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUnifiedTopBar);
  } else {
    initUnifiedTopBar();
  }
})();
