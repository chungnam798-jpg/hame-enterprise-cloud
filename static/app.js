// ═══════════════════════════════════════════
//  FBPoster v1.1 – Client-Side Application
// ═══════════════════════════════════════════
const API = '/api';

let state = {
  accounts: [],
  posts: [],
  settings: {},
  rules: [],
  engageLogs: [],
  alTargets: [],
  alLogs: [],
  templates: [],
  bulkGroups: [],
  targetLists: [],
  analytics: {},
  trashPosts: [],
  selectedTemplateContent: ''
};

// ─── Init ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.nav-item').forEach(el =>
    el.addEventListener('click', e => { e.preventDefault(); switchTab(el.dataset.tab); }));

  bindForm('add-account-form', handleAddAccount);
  bindForm('create-post-form', handleCreatePost);
  bindForm('settings-form', handleSaveSettings);
  bindForm('add-rule-form', handleAddRule);
  bindForm('manual-scan-form', handleManualScan);
  bindForm('manual-autofeed-form', handleManualAutofeed);
  bindForm('bulk-form', handleBulkCreate);
  bindForm('autolike-form', handleAddAutolikeTarget);
  bindForm('template-form', handleSaveTemplate);
  bindForm('analyzer-form', handleLinkAnalysis);
  bindForm('autojoin-form', handleStartAutojoin);
  bindForm('autojoin-topic-form', handleStartTopicCampaign);
  bindForm('shopee-bulk-form', handleShopeeBulkImport);
  bindForm('claude-schedule-form', handleClaudeScheduleImport);

  const fileInput = document.getElementById('post-media');
  if (fileInput) fileInput.addEventListener('change', handleFilePreview);

  const postAccountSelect = document.getElementById('post-account');
  if (postAccountSelect) {
    postAccountSelect.addEventListener('change', (e) => {
      const acc = state.accounts.find(a => a.id === e.target.value);
      const row = document.getElementById('post-type')?.closest('.form-row');
      if (acc && acc.platform === 'threads') {
        if (row) row.style.display = 'none';
        setVal('post-type', 'profile');
        setVal('post-target-id', 'me');
      } else {
        if (row) row.style.display = 'flex';
        toggleTargetIdPlaceholder();
      }
    });
  }

  setDefaultScheduledDate('post-scheduled-at');
  setDefaultScheduledDate('bulk-scheduled-at');
  
  if (window.cleanTargetIdInput) {
    window.cleanTargetIdInput('post-target-id');
  }

  loadAll();
  setInterval(refreshDynamic, 6000);
});

function bindForm(id, handler) {
  const el = document.getElementById(id);
  if (el) el.addEventListener('submit', handler);
}

// ─── Tab switching ──────────────────────────
function switchTab(tabId) {
  document.querySelectorAll('.nav-item').forEach(el =>
    el.classList.toggle('active', el.dataset.tab === tabId));
  document.querySelectorAll('.tab-content').forEach(el =>
    el.classList.toggle('active', el.id === `tab-${tabId}`));

  const titles = {
    dashboard: 'Bảng điều khiển',
    accounts: 'Quản lý tài khoản',
    'create-post': 'Soạn bài viết mới',
    bulk: 'Đăng hàng loạt',
    posts: 'Lịch sử & Hẹn giờ',
    engage: 'Tương tác tự động',
    autolike: 'Auto-Like',
    templates: 'Templates bài viết',
    analyzer: 'Phân tích Link FB',
    trash: 'Thùng rác bài viết',
    autojoin: 'Tự động tham gia nhóm',
    settings: 'Cấu hình hệ thống'
  };
  document.getElementById('current-tab-title').textContent = titles[tabId] || 'FBPoster';

  if (tabId === 'autojoin') { fetchAutojoinLogs(); fetchTargetLists(); populateSelect('autojoin-account'); populateSelect('autojoin-topic-account'); }

  if (tabId === 'create-post') { setDefaultScheduledDate('post-scheduled-at'); fetchTargetLists(); }
  if (tabId === 'bulk') setDefaultScheduledDate('bulk-scheduled-at');
  if (tabId === 'engage') { fetchRules(); fetchEngageLogs(); populateSelect('scan-account'); populateSelect('autofeed-run-account'); }
  if (tabId === 'autolike') { fetchAutolikeTargets(); fetchAutolikeLogs(); fetchTargetLists(); populateSelect('autolike-account'); }
  if (tabId === 'templates') fetchTemplates();
  if (tabId === 'bulk') { fetchBulkGroups(); fetchTargetLists(); populateSelect('bulk-account'); }
  if (tabId === 'analyzer') { populateSelect('analyzer-account'); }
  if (tabId === 'trash') fetchTrashPosts();
}

function setDefaultScheduledDate(inputId) {
  const el = document.getElementById(inputId);
  if (!el) return;
  const now = new Date();
  el.value = new Date(now - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

// ─── Load all data ──────────────────────────
async function loadAll() {
  await Promise.all([fetchAccounts(), fetchPosts(), fetchSettings(), fetchTargetLists()]);
  renderDashboard();
}

async function refreshDynamic() {
  try {
    await fetchPostsSilent();
    renderDashboard();
    const active = document.querySelector('.nav-item.active')?.dataset.tab;
    if (active === 'engage') await fetchEngageLogs();
    if (active === 'autolike') { await fetchAutolikeTargets(); await fetchAutolikeLogs(); }
    if (active === 'bulk') { await fetchBulkGroups(); }
    if (active === 'trash') await fetchTrashPosts();
    if (active === 'autojoin') await fetchAutojoinLogs();
    
    if (['create-post', 'bulk', 'autolike', 'autojoin'].includes(active)) {
      await fetchTargetLists();
    }
  } catch(e) { /* silent */ }
}

// ─── API: Accounts ──────────────────────────
async function fetchAccounts() {
  const r = await fetch(`${API}/accounts`);
  if (r.ok) {
    state.accounts = await r.json();
    renderAccounts();
    populateAllAccountSelects();
  }
}

function renderAccounts() {
  const el = document.getElementById('accounts-list');
  if (!el) return;
  if (!state.accounts.length) {
    el.innerHTML = '<div class="text-center text-muted py-4 w-100">Chưa có tài khoản nào.</div>';
    return;
  }
  el.innerHTML = state.accounts.map(a => {
    let statusBadge = '';
    if (a.status === 'active') {
      statusBadge = '<span class="badge badge-active">Hoạt động</span>';
    } else if (a.status === 'logging_in') {
      statusBadge = '<span class="badge badge-posting"><i class="fa-solid fa-spinner fa-spin"></i> Đang đăng nhập...</span>';
    } else {
      statusBadge = '<span class="badge badge-inactive">Lỗi/Hết hạn</span>';
    }

    let autoLoginBadge = '';
    let refreshBtn = '';
    if (a.username) {
      autoLoginBadge = `<span style="font-size:0.7rem; color:var(--primary); margin-top:2px; display:inline-block;"><i class="fa-solid fa-shield-halved"></i> Tự động</span>`;
      refreshBtn = `<button class="action-btn" style="color:var(--primary);" title="Đăng nhập lại và làm mới Cookie" onclick="triggerAutoLogin('${a.id}')"><i class="fa-solid fa-rotate"></i></button>`;
    }

    return `
    <div class="account-card">
      <div class="account-card-header">
        <div class="account-info">
          <div class="account-avatar">${a.name.charAt(0).toUpperCase()}</div>
          <div class="account-meta">
            <h4>${esc(a.name)}</h4>
            <small>${a.id}</small>
            ${autoLoginBadge}
          </div>
        </div>
        <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px;">
          <span class="badge badge-posting" style="text-transform:capitalize; font-size:0.65rem; padding:0.1rem 0.45rem;">${esc(a.platform || 'facebook')}</span>
          ${statusBadge}
        </div>
      </div>
      <div class="account-card-footer">
        <small class="text-muted">${fmtTime(a.updated_at)}</small>
        <div style="display:flex; gap:8px;">
          ${refreshBtn}
          <button class="action-btn btn-delete" onclick="deleteAccount('${a.id}')"><i class="fa-solid fa-trash"></i></button>
        </div>
      </div>
    </div>`;
  }).join('');
}

function populateSelect(selectId, accounts) {
  const el = document.getElementById(selectId);
  if (!el) return;
  const src = accounts || state.accounts;
  el.innerHTML = '<option value="">-- Chọn tài khoản --</option>';
  src.filter(a => a.status === 'active').forEach(a => {
    const o = document.createElement('option');
    o.value = a.id; o.textContent = a.name;
    el.appendChild(o);
  });
}

function populateAllAccountSelects() {
  ['post-account', 'bulk-account', 'scan-account', 'autolike-account', 'autofeed-run-account', 'analyzer-account', 'autojoin-account', 'autojoin-topic-account', 'setting-shopee-poster-account-id'].forEach(id => populateSelect(id));
}

async function triggerAutoLogin(accountId) {
  const btn = event.currentTarget;
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
  
  await fetchAccounts();
  
  try {
    const res = await fetch(`${API}/accounts/${accountId}/auto-login`, { method: 'POST' });
    const data = await res.json();
    if (res.ok) {
      alert('Đăng nhập và làm mới Cookie thành công!');
    } else {
      alert('Lỗi: ' + (data.error || 'Đăng nhập tự động thất bại.'));
    }
  } catch (err) {
    alert('Lỗi kết nối: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalHtml;
    await fetchAccounts();
    renderDashboard();
  }
}

async function handleAddAccount(e) {
  e.preventDefault();
  const name = v('acc-name'), cookie = v('acc-cookie'), platform = v('acc-platform') || 'facebook';
  const username = v('acc-username'), password = v('acc-password'), two_factor_key = v('acc-2fa');
  const r = await post(`${API}/accounts`, { name, cookie, platform, username, password, two_factor_key });
  if (r.error) { alert('Lỗi: ' + r.error); return; }
  alert('Lưu tài khoản thành công!');
  e.target.reset();
  if (window.toggleCookiePlaceholder) window.toggleCookiePlaceholder();
  await fetchAccounts();
  renderDashboard();
}

async function deleteAccount(id) {
  if (!confirm('Xóa tài khoản này?')) return;
  await fetch(`${API}/accounts/${id}`, { method: 'DELETE' });
  await fetchAccounts();
  renderDashboard();
}

// ─── API: Posts ─────────────────────────────
async function fetchPosts() {
  const r = await fetch(`${API}/posts`);
  if (r.ok) { state.posts = await r.json(); renderPostsTable(); }
}

async function fetchPostsSilent() {
  const r = await fetch(`${API}/posts`);
  if (r.ok) { state.posts = await r.json(); renderPostsTable(); }
}

function renderDashboard() {
  const acc  = state.accounts.filter(a => a.status === 'active').length;
  const pend = state.posts.filter(p => p.status === 'pending').length;
  const succ = state.posts.filter(p => p.status === 'posted').length;
  const fail = state.posts.filter(p => p.status === 'failed').length;

  setText('stat-active-accounts', acc);
  setText('stat-pending-posts', pend);
  setText('stat-success-posts', succ);
  setText('stat-failed-posts', fail);
  setText('stat-engage', state.engageLogs.filter(l => l.status==='success').length);
  setText('stat-likes', state.alLogs.filter(l => l.status==='success').length);

  const el = document.getElementById('recent-posts-list');
  if (!el) return;
  const recent = state.posts.slice(0, 6);
  if (!recent.length) { el.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Chưa có dữ liệu.</td></tr>'; return; }
  el.innerHTML = recent.map(p => {
    let actions = '';
    if (p.status === 'pending') actions += `<button class="action-btn btn-post-now" title="Đăng ngay" onclick="publishNow('${p.id}')"><i class="fa-solid fa-paper-plane"></i></button>`;
    actions += `<button class="action-btn" style="color:var(--accent)" title="Sửa bài" onclick="openEditPost('${p.id}')"><i class="fa-solid fa-pen-to-square"></i></button>`;
    if (p.screenshot) actions += `<button class="action-btn btn-screenshot-view" onclick="viewScreenshot('${p.screenshot}')"><i class="fa-solid fa-image"></i></button>`;
    actions += `<button class="action-btn btn-delete" onclick="deletePost('${p.id}')"><i class="fa-solid fa-trash"></i></button>`;
    return `<tr>
      <td><strong>${esc(p.account_name||'')}</strong></td>
      <td>${typeLabel(p.type)} (${esc(p.target_id)})</td>
      <td class="post-content-cell" title="${esc(p.content)}">${esc(p.content)}</td>
      <td>${fmtTime(p.scheduled_at)}</td>
      <td>${statusBadge(p.status)}</td>
      <td><small class="text-muted">${esc(p.result_log||'-')}</small></td>
      <td><div class="action-icons">${actions}</div></td>
    </tr>`;
  }).join('');
}

function renderPostsTable() {
  const el = document.getElementById('all-posts-list');
  if (!el) return;
  // Reset bulk selection
  const selectAll = document.getElementById('select-all-posts');
  if (selectAll) selectAll.checked = false;
  const panel = document.getElementById('bulk-posts-actions-panel');
  if (panel) panel.style.display = 'none';

  if (!state.posts.length) { el.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-4">Chưa có bài đăng.</td></tr>'; return; }
  el.innerHTML = state.posts.map(p => {
    let actions = '';
    if (p.status === 'pending') actions += `<button class="action-btn btn-post-now" title="Đăng ngay" onclick="publishNow('${p.id}')"><i class="fa-solid fa-paper-plane"></i></button>`;
    actions += `<button class="action-btn" style="color:var(--accent)" title="Sửa bài" onclick="openEditPost('${p.id}')"><i class="fa-solid fa-pen-to-square"></i></button>`;
    if (p.screenshot) actions += `<button class="action-btn btn-screenshot-view" onclick="viewScreenshot('${p.screenshot}')"><i class="fa-solid fa-image"></i></button>`;
    actions += `<button class="action-btn btn-delete" onclick="deletePost('${p.id}')"><i class="fa-solid fa-trash"></i></button>`;
    return `<tr>
      <td><input type="checkbox" class="post-item-checkbox" value="${p.id}" onchange="onPostItemCheckboxChange()"></td>
      <td><strong>${esc(p.account_name||'')}</strong></td>
      <td>${typeLabel(p.type)}</td>
      <td><code>${esc(p.target_id)}</code></td>
      <td class="post-content-cell" title="${esc(p.content)}">${esc(p.content)}</td>
      <td>${fmtTime(p.scheduled_at)}</td>
      <td>${statusBadge(p.status)}</td>
      <td><small>${esc(p.result_log||'-')}</small></td>
      <td><div class="action-icons">${actions}</div></td>
    </tr>`;
  }).join('');
}

let aiGeneratedImages = [];

async function handleCreatePost(e) {
  e.preventDefault();
  const accountId = v('post-account');
  if (!accountId) { alert('Vui lòng chọn tài khoản.'); return; }
  const acc = state.accounts.find(a => a.id === accountId);
  const platform = acc ? acc.platform : 'facebook';
  const fd = new FormData();
  fd.append('account_id', accountId);
  fd.append('type', v('post-type'));
  fd.append('target_id', v('post-target-id'));
  fd.append('content', v('post-content'));
  fd.append('first_comment', v('post-first-comment'));
  fd.append('scheduled_at', new Date(v('post-scheduled-at')).toISOString());
  fd.append('existing_media', JSON.stringify(aiGeneratedImages));
  fd.append('platform', platform);
  const targetListId = v('post-target-list');
  if (targetListId) {
    fd.append('target_list_id', targetListId);
  }
  Array.from(document.getElementById('post-media').files).forEach(f => fd.append('media', f));
  const redirectToggle = document.getElementById('post-redirect-toggle');
  if (redirectToggle && redirectToggle.checked) {
    const redirectUrl = v('post-redirect-url').trim();
    if (!redirectUrl) {
      alert('Vui lòng nhập đường link chuyển hướng.');
      return;
    }
    const files = document.getElementById('post-media').files;
    const totalImages = files.length + aiGeneratedImages.length;
    if (totalImages !== 1) {
      alert('Để đăng ảnh clickable, bạn phải chọn đúng 1 bức ảnh (tải lên hoặc ảnh từ AI/Shopee).');
      return;
    }
    fd.append('redirect_url', redirectUrl);
    fd.append('redirect_title', v('post-redirect-title').trim());
    fd.append('redirect_desc', v('post-redirect-desc').trim());
  }

  const btn = setLoading(e.target, 'Đang tải lên...');
  const r = await fetch(`${API}/posts`, { method: 'POST', body: fd });
  resetLoading(e.target, btn, '<i class="fa-solid fa-paper-plane"></i>Lên lịch đăng');
  if (r.ok) { alert('Đã lên lịch bài đăng!'); resetPostForm(); await fetchPosts(); renderDashboard(); switchTab('posts'); }
  else {
    let errMsg = `Lỗi máy chủ (Mã HTTP: ${r.status}).`;
    try {
      const err = await r.json();
      errMsg = err.error || errMsg;
    } catch (e) {}
    alert('Lỗi: ' + errMsg);
  }
}

function resetPostForm() {
  document.getElementById('create-post-form').reset();
  document.getElementById('media-preview-container').innerHTML = '';
  document.getElementById('file-count').textContent = 'Chưa chọn file nào';
  aiGeneratedImages = [];
  setDefaultScheduledDate('post-scheduled-at');
  const selectPost = document.getElementById('post-target-list');
  if (selectPost) selectPost.value = '';
  togglePostTargetListSelection('');
  const redirectToggle = document.getElementById('post-redirect-toggle');
  if (redirectToggle) {
    redirectToggle.checked = false;
    toggleRedirectFields();
  }
  toggleTargetIdPlaceholder();
  const row = document.getElementById('post-type')?.closest('.form-row');
  if (row) row.style.display = 'flex';
}

async function publishNow(id) {
  await fetch(`${API}/posts/${id}/publish`, { method: 'POST' });
  alert('Đã kích hoạt đăng ngay. Theo dõi trạng thái trong vài giây...');
  setTimeout(fetchPosts, 2000);
}

async function deletePost(id) {
  if (!confirm('Xóa bài đăng này? Bài đăng sẽ được chuyển vào Thùng rác.')) return;
  const r = await fetch(`${API}/posts/${id}`, { method: 'DELETE' });
  if (r.ok) {
    await fetchPosts();
    renderDashboard();
  }
}

async function fetchTrashPosts() {
  const r = await fetch(`${API}/posts/deleted`);
  if (r.ok) {
    state.trashPosts = await r.json();
    renderTrashTable();
  }
}

function renderTrashTable() {
  const el = document.getElementById('trash-posts-list');
  if (!el) return;
  // Reset bulk selection
  const selectAll = document.getElementById('select-all-trash');
  if (selectAll) selectAll.checked = false;
  const panel = document.getElementById('bulk-trash-actions-panel');
  if (panel) panel.style.display = 'none';

  if (!state.trashPosts || !state.trashPosts.length) {
    el.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">Thùng rác trống.</td></tr>';
    return;
  }
  el.innerHTML = state.trashPosts.map(p => `<tr>
    <td><input type="checkbox" class="trash-item-checkbox" value="${p.id}" onchange="onTrashItemCheckboxChange()"></td>
    <td><strong>${esc(p.account_name||'')}</strong></td>
    <td>${typeLabel(p.type)} (${esc(p.target_id)})</td>
    <td class="post-content-cell" title="${esc(p.content)}">${esc(p.content)}</td>
    <td>${fmtTime(p.updated_at)}</td>
    <td>
      <div class="action-icons">
        <button class="action-btn btn-post-now" title="Khôi phục" onclick="restorePost('${p.id}')"><i class="fa-solid fa-rotate-left"></i></button>
        <button class="action-btn btn-delete" title="Xóa vĩnh viễn" onclick="deletePostPermanent('${p.id}')"><i class="fa-solid fa-trash-can"></i></button>
      </div>
    </td>
  </tr>`).join('');
}

async function restorePost(id) {
  if (!confirm('Khôi phục bài đăng này về danh sách?')) return;
  const r = await fetch(`${API}/posts/${id}/restore`, { method: 'POST' });
  if (r.ok) {
    alert('Đã khôi phục bài đăng!');
    await fetchTrashPosts();
    await fetchPosts();
    renderDashboard();
  }
}

async function deletePostPermanent(id) {
  if (!confirm('CẢNH BÁO: Xóa vĩnh viễn bài đăng này và tất cả các file đính kèm? Không thể khôi phục lại!')) return;
  const r = await fetch(`${API}/posts/${id}/permanent`, { method: 'DELETE' });
  if (r.ok) {
    alert('Đã xóa vĩnh viễn bài đăng!');
    await fetchTrashPosts();
  }
}

// ─── Bulk Actions ───────────────────────────
window.toggleSelectAllPosts = function(masterCb) {
  document.querySelectorAll('.post-item-checkbox').forEach(cb => {
    cb.checked = masterCb.checked;
  });
  window.onPostItemCheckboxChange();
};

window.onPostItemCheckboxChange = function() {
  const cbs = Array.from(document.querySelectorAll('.post-item-checkbox'));
  const selected = cbs.filter(cb => cb.checked).map(cb => cb.value);
  const panel = document.getElementById('bulk-posts-actions-panel');
  const countText = document.getElementById('bulk-posts-selected-count');
  
  if (selected.length > 0) {
    if (panel) panel.style.display = 'flex';
    if (countText) countText.textContent = `Đã chọn ${selected.length} bài viết`;
  } else {
    if (panel) panel.style.display = 'none';
  }
  
  const selectAll = document.getElementById('select-all-posts');
  if (selectAll) {
    selectAll.checked = cbs.length > 0 && selected.length === cbs.length;
  }
};

window.bulkDeletePosts = async function() {
  const selected = Array.from(document.querySelectorAll('.post-item-checkbox'))
    .filter(cb => cb.checked).map(cb => cb.value);
  if (selected.length === 0) return;
  if (!confirm(`Xóa ${selected.length} bài viết đã chọn? Các bài viết sẽ được chuyển vào Thùng rác.`)) return;
  
  const r = await post(`${API}/posts/bulk-delete`, { ids: selected });
  if (!r.error) {
    alert('Đã chuyển các bài đăng vào Thùng rác!');
    await fetchPosts();
    renderDashboard();
  } else {
    alert('Lỗi: ' + r.error);
  }
};

window.toggleSelectAllTrash = function(masterCb) {
  document.querySelectorAll('.trash-item-checkbox').forEach(cb => {
    cb.checked = masterCb.checked;
  });
  window.onTrashItemCheckboxChange();
};

window.onTrashItemCheckboxChange = function() {
  const cbs = Array.from(document.querySelectorAll('.trash-item-checkbox'));
  const selected = cbs.filter(cb => cb.checked).map(cb => cb.value);
  const panel = document.getElementById('bulk-trash-actions-panel');
  const countText = document.getElementById('bulk-trash-selected-count');
  
  if (selected.length > 0) {
    if (panel) panel.style.display = 'flex';
    if (countText) countText.textContent = `Đã chọn ${selected.length} bài viết`;
  } else {
    if (panel) panel.style.display = 'none';
  }
  
  const selectAll = document.getElementById('select-all-trash');
  if (selectAll) {
    selectAll.checked = cbs.length > 0 && selected.length === cbs.length;
  }
};

window.bulkRestoreTrash = async function() {
  const selected = Array.from(document.querySelectorAll('.trash-item-checkbox'))
    .filter(cb => cb.checked).map(cb => cb.value);
  if (selected.length === 0) return;
  if (!confirm(`Khôi phục ${selected.length} bài viết đã chọn về danh sách chính?`)) return;
  
  const r = await post(`${API}/posts/bulk-restore`, { ids: selected });
  if (!r.error) {
    alert('Đã khôi phục các bài đăng thành công!');
    await fetchTrashPosts();
    await fetchPosts();
    renderDashboard();
  } else {
    alert('Lỗi: ' + r.error);
  }
};

window.bulkDeletePermanentTrash = async function() {
  const selected = Array.from(document.querySelectorAll('.trash-item-checkbox'))
    .filter(cb => cb.checked).map(cb => cb.value);
  if (selected.length === 0) return;
  if (!confirm(`CẢNH BÁO NGHIÊM TRỌNG: Bạn có chắc chắn muốn xóa vĩnh viễn ${selected.length} bài viết đã chọn và tất cả file đính kèm? Hành động này không thể hoàn tác!`)) return;
  
  const r = await post(`${API}/posts/bulk-permanent`, { ids: selected });
  if (!r.error) {
    alert('Đã xóa vĩnh viễn các bài đăng thành công!');
    await fetchTrashPosts();
  } else {
    alert('Lỗi: ' + r.error);
  }
};

// ─── Bulk Posting ───────────────────────────
async function fetchBulkGroups() {
  const r = await fetch(`${API}/bulk`);
  if (r.ok) { state.bulkGroups = await r.json(); renderBulkGroups(); }
}

function renderBulkGroups() {
  const el = document.getElementById('bulk-list');
  if (!el) return;
  if (!state.bulkGroups.length) { el.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Chưa có chiến dịch.</td></tr>'; return; }
  el.innerHTML = state.bulkGroups.map(bg => `<tr>
    <td><strong>${esc(bg.name)}</strong></td>
    <td>${bg.total_posts}</td>
    <td style="color:var(--success)">${bg.success_count}</td>
    <td style="color:var(--danger)">${bg.fail_count}</td>
    <td>${statusBadge(bg.status)}</td>
    <td>
      <div class="action-icons">
        <button class="action-btn btn-delete" onclick="deleteBulkGroup('${bg.id}')" title="Xóa chiến dịch"><i class="fa-solid fa-trash"></i></button>
      </div>
    </td>
  </tr>`).join('');
}

async function deleteBulkGroup(id) {
  if (!confirm('Xóa chiến dịch này? Tất cả bài viết thuộc chiến dịch sẽ được chuyển vào Thùng rác.')) return;
  const r = await fetch(`${API}/bulk/${id}`, { method: 'DELETE' });
  if (r.ok) {
    alert('Đã xóa chiến dịch!');
    await fetchBulkGroups();
    await fetchPosts();
    renderDashboard();
  } else {
    alert('Không thể xóa chiến dịch.');
  }
}

async function handleBulkCreate(e) {
  e.preventDefault();
  const accountId = v('bulk-account');
  const rawTargets = v('bulk-targets');
  if (!accountId) { alert('Vui lòng chọn tài khoản.'); return; }

  const targets = rawTargets.trim().split('\n').map(line => {
    line = line.trim();
    if (!line) return null;

    // Detect if it is a Facebook URL
    if (line.includes('facebook.com') || line.includes('fb.com')) {
      if (line.includes('/groups/')) {
        const match = line.match(/\/groups\/([^/?#\s]+)/);
        if (match) return { type: 'group', target_id: match[1] };
      } else {
        if (line.includes('profile.php')) {
          try {
            const urlObj = new URL(line);
            const id = urlObj.searchParams.get('id');
            if (id) return { type: 'page', target_id: id };
          } catch(err) {}
        }
        const cleanUrl = line.split('?')[0].split('#')[0];
        const parts = cleanUrl.replace(/\/+$/, '').split('/');
        const lastPart = parts[parts.length - 1];
        if (lastPart && lastPart !== 'facebook.com' && lastPart !== 'fb.com') {
          return { type: 'page', target_id: lastPart };
        }
      }
    }

    // Prefixes support as fallback
    if (line.startsWith('group:')) return { type: 'group', target_id: line.replace('group:', '').trim() };
    if (line.startsWith('page:')) return { type: 'page', target_id: line.replace('page:', '').trim() };

    // Raw input logic (digits -> group, string -> page)
    if (/^\d+$/.test(line)) {
      return { type: 'group', target_id: line };
    } else {
      return { type: 'page', target_id: line };
    }
  }).filter(Boolean);

  if (!targets.length) { alert('Vui lòng nhập ít nhất 1 mục tiêu hợp lệ.'); return; }

  const btn = setLoading(e.target, 'Đang tạo chiến dịch...');
  const r = await post(`${API}/bulk`, {
    name: v('bulk-name'),
    account_id: accountId,
    content: v('bulk-content'),
    targets,
    scheduled_at: new Date(v('bulk-scheduled-at')).toISOString()
  });
  resetLoading(e.target, btn, '<i class="fa-solid fa-layer-group"></i>Tạo chiến dịch');
  if (r.error) { alert('Lỗi: ' + r.error); return; }
  alert(`Đã tạo chiến dịch "${v('bulk-name')}" với ${r.posts_created} bài đăng trong hàng đợi!`);
  e.target.reset();
  await fetchBulkGroups(); await fetchPosts();
}

async function fetchSettings() {
  const r = await fetch(`${API}/settings`);
  if (r.ok) {
    state.settings = await r.json();
    setVal('setting-delay', state.settings.delay_between_posts || 60);
    setVal('setting-engage-interval', state.settings.engage_interval_minutes || 15);
    setVal('setting-autolike-interval', state.settings.autolike_interval_minutes || 30);
    setVal('setting-max-replies', state.settings.max_replies_per_scan || 5);
    setVal('setting-max-likes', state.settings.max_likes_per_scan || 10);
    setVal('setting-gemini-key', state.settings.gemini_api_key || '');
    setVal('setting-public-domain', state.settings.public_domain || '');

    setVal('setting-shopee-poster-account-id', state.settings.shopee_poster_account_id || '');
    setVal('setting-shopee-poster-type', state.settings.shopee_poster_type || 'profile');
    setVal('setting-shopee-poster-target-id', state.settings.shopee_poster_target_id || 'me');
    setVal('setting-shopee-poster-format', state.settings.shopee_poster_format || 'clickable');
    setVal('setting-shopee-poster-delay-minutes', state.settings.shopee_poster_delay_minutes || 15);
    setVal('setting-shopee-auto-comment-link', state.settings.shopee_auto_comment_link || '1');
    setVal('setting-shopee-comment-template', state.settings.shopee_comment_template || 'Link mua sản phẩm tại đây nhé cả nhà: {link}');
    setVal('setting-shopee-affiliate-id', state.settings.shopee_affiliate_id || '');
    setVal('setting-shopee-sub-id', state.settings.shopee_sub_id || 'fbposter');

    const headless = state.settings.browser_headless === '1';
    const headlessCheckbox = document.getElementById('setting-browser-headless');
    if (headlessCheckbox) {
      headlessCheckbox.checked = headless;
    }
    setVal('setting-engage-speed', state.settings.engage_speed_mode || 'turbo');

    const enabled = state.settings.autofeed_engage_enabled === '1';
    const enabledCheckbox = document.getElementById('setting-autofeed-enabled');
    if (enabledCheckbox) {
      enabledCheckbox.checked = enabled;
    }
    setVal('setting-autofeed-source', state.settings.autofeed_engage_source || 'groups');
    setVal('setting-autofeed-interval', state.settings.autofeed_engage_interval_minutes || 30);
    setVal('setting-autofeed-max-posts', state.settings.autofeed_max_posts_per_scan || 5);
    setVal('setting-autofeed-style', state.settings.autofeed_engage_style || 'spintax');
    setVal('setting-autofeed-text', state.settings.autofeed_engage_text || '');

    const teleEnabled = state.settings.telegram_enabled === '1';
    const teleEnabledCheckbox = document.getElementById('setting-telegram-enabled');
    if (teleEnabledCheckbox) {
      teleEnabledCheckbox.checked = teleEnabled;
    }
    setVal('setting-telegram-token', state.settings.telegram_token || '');
    setVal('setting-telegram-chat-id', state.settings.telegram_chat_id || '');
    
    const teleNotifySuccess = state.settings.telegram_notify_success === '1';
    const teleNotifySuccessCheckbox = document.getElementById('setting-telegram-notify-success');
    if (teleNotifySuccessCheckbox) {
      teleNotifySuccessCheckbox.checked = teleNotifySuccess;
    }
    
    const teleNotifyFail = state.settings.telegram_notify_fail === '1';
    const teleNotifyFailCheckbox = document.getElementById('setting-telegram-notify-fail');
    if (teleNotifyFailCheckbox) {
      teleNotifyFailCheckbox.checked = teleNotifyFail;
    }

    const inboxEnabled = state.settings.inbox_chatbot_enabled === '1';
    const inboxEnabledCheckbox = document.getElementById('setting-inbox-chatbot-enabled');
    if (inboxEnabledCheckbox) {
      inboxEnabledCheckbox.checked = inboxEnabled;
    }
    setVal('setting-inbox-keywords', state.settings.inbox_keywords || '');
    setVal('setting-inbox-comment-reply-template', state.settings.inbox_comment_reply_template || '');
    setVal('setting-inbox-message-template', state.settings.inbox_message_template || '');

    if (window.toggleAutofeedSettingsDisplay) window.toggleAutofeedSettingsDisplay();
    if (window.toggleAutofeedSpintaxDisplay) window.toggleAutofeedSpintaxDisplay();
    if (window.toggleTelegramSettingsDisplay) window.toggleTelegramSettingsDisplay();
    if (window.toggleInboxSettingsDisplay) window.toggleInboxSettingsDisplay();
  }
}

async function handleSaveSettings(e) {
  e.preventDefault();
  const enabledCheckbox = document.getElementById('setting-autofeed-enabled');
  const headlessCheckbox = document.getElementById('setting-browser-headless');
  const teleEnabledCheckbox = document.getElementById('setting-telegram-enabled');
  const teleNotifySuccessCheckbox = document.getElementById('setting-telegram-notify-success');
  const teleNotifyFailCheckbox = document.getElementById('setting-telegram-notify-fail');
  const inboxEnabledCheckbox = document.getElementById('setting-inbox-chatbot-enabled');
  await post(`${API}/settings`, {
    delay_between_posts: v('setting-delay'),
    engage_interval_minutes: v('setting-engage-interval'),
    autolike_interval_minutes: v('setting-autolike-interval'),
    max_replies_per_scan: v('setting-max-replies'),
    max_likes_per_scan: v('setting-max-likes'),
    gemini_api_key: v('setting-gemini-key'),
    public_domain: v('setting-public-domain'),
    shopee_poster_account_id: v('setting-shopee-poster-account-id'),
    shopee_poster_type: v('setting-shopee-poster-type'),
    shopee_poster_target_id: v('setting-shopee-poster-target-id'),
    shopee_poster_format: v('setting-shopee-poster-format'),
    shopee_poster_delay_minutes: v('setting-shopee-poster-delay-minutes'),
    shopee_auto_comment_link: v('setting-shopee-auto-comment-link'),
    shopee_comment_template: v('setting-shopee-comment-template'),
    shopee_affiliate_id: v('setting-shopee-affiliate-id'),
    shopee_sub_id: v('setting-shopee-sub-id'),
    browser_headless: headlessCheckbox && headlessCheckbox.checked ? '1' : '0',
    engage_speed_mode: v('setting-engage-speed'),
    autofeed_engage_enabled: enabledCheckbox && enabledCheckbox.checked ? '1' : '0',
    autofeed_engage_source: v('setting-autofeed-source'),
    autofeed_engage_interval_minutes: v('setting-autofeed-interval'),
    autofeed_max_posts_per_scan: v('setting-autofeed-max-posts'),
    autofeed_engage_style: v('setting-autofeed-style'),
    autofeed_engage_text: v('setting-autofeed-text'),
    telegram_enabled: teleEnabledCheckbox && teleEnabledCheckbox.checked ? '1' : '0',
    telegram_token: v('setting-telegram-token'),
    telegram_chat_id: v('setting-telegram-chat-id'),
    telegram_notify_success: teleNotifySuccessCheckbox && teleNotifySuccessCheckbox.checked ? '1' : '0',
    telegram_notify_fail: teleNotifyFailCheckbox && teleNotifyFailCheckbox.checked ? '1' : '0',
    inbox_chatbot_enabled: inboxEnabledCheckbox && inboxEnabledCheckbox.checked ? '1' : '0',
    inbox_keywords: v('setting-inbox-keywords'),
    inbox_comment_reply_template: v('setting-inbox-comment-reply-template'),
    inbox_message_template: v('setting-inbox-message-template')
  });
  alert('Đã lưu cấu hình!');
  await fetchSettings();
}


window.toggleAutofeedSettingsDisplay = function() {
  const enabled = document.getElementById('setting-autofeed-enabled')?.checked;
  const group = document.getElementById('autofeed-settings-group');
  if (group) {
    group.style.display = enabled ? 'block' : 'none';
  }
};

window.toggleAutofeedSpintaxDisplay = function() {
  const style = document.getElementById('setting-autofeed-style')?.value || 'AI';
  const group = document.getElementById('autofeed-text-group');
  if (group) {
    group.style.display = style === 'spintax' ? 'block' : 'none';
  }
};

window.toggleTelegramSettingsDisplay = function() {
  const enabled = document.getElementById('setting-telegram-enabled')?.checked;
  const group = document.getElementById('telegram-settings-group');
  if (group) {
    group.style.display = enabled ? 'block' : 'none';
  }
};

window.toggleInboxSettingsDisplay = function() {
  const enabled = document.getElementById('setting-inbox-chatbot-enabled')?.checked;
  const group = document.getElementById('inbox-settings-group');
  if (group) {
    group.style.display = enabled ? 'block' : 'none';
  }
};

window.testTelegramConnection = async function() {
  const token = document.getElementById('setting-telegram-token')?.value || '';
  const chatId = document.getElementById('setting-telegram-chat-id')?.value || '';
  if (!token || !chatId) {
    alert('Vui lòng điền đầy đủ Token và Chat ID trước khi gửi tin nhắn test.');
    return;
  }
  
  const btn = document.getElementById('btn-test-telegram');
  if (btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang gửi...';
  
  try {
    const res = await fetch(`${API}/telegram/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, chat_id: chatId })
    });
    const r = await res.json();
    if (r.error) {
      alert('Lỗi: ' + r.error);
    } else {
      alert('Đã gửi tin nhắn test thành công! Hãy kiểm tra ứng dụng Telegram trên điện thoại của bạn.');
    }
  } catch (err) {
    alert('Lỗi kết nối máy chủ: ' + err);
  } finally {
    if (btn) btn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Gửi tin nhắn thử nghiệm';
  }
};

// ─── FB-Engage ──────────────────────────────
async function fetchRules() {
  const r = await fetch(`${API}/engagement/rules`);
  if (r.ok) { state.rules = await r.json(); renderRules(); }
}

function renderRules() {
  const el = document.getElementById('rules-list');
  if (!el) return;
  if (!state.rules.length) { el.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Chưa có kịch bản.</td></tr>'; return; }
  el.innerHTML = state.rules.map(r => `<tr>
    <td><code>${esc(r.keywords)}</code></td>
    <td>${esc(r.reply_text)}</td>
    <td><span class="badge ${r.status==='active'?'badge-active':'badge-inactive'}">${r.status==='active'?'Bật':'Tắt'}</span></td>
    <td><button class="action-btn btn-delete" onclick="deleteRule('${r.id}')"><i class="fa-solid fa-trash"></i></button></td>
  </tr>`).join('');
}

async function handleAddRule(e) {
  e.preventDefault();
  const r = await post(`${API}/engagement/rules`, { keywords: v('rule-keywords'), reply_text: v('rule-reply-text') });
  if (r.error) { alert('Lỗi: ' + r.error); return; }
  alert('Đã lưu kịch bản!'); e.target.reset(); await fetchRules();
}

async function deleteRule(id) {
  if (!confirm('Xóa kịch bản?')) return;
  await fetch(`${API}/engagement/rules/${id}`, { method: 'DELETE' });
  await fetchRules();
}

async function fetchEngageLogs() {
  const r = await fetch(`${API}/engagement/logs`);
  if (r.ok) { state.engageLogs = await r.json(); renderEngageLogs(); }
}

function renderEngageLogs() {
  const el = document.getElementById('engage-logs-list');
  if (!el) return;
  if (!state.engageLogs.length) { el.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Chưa có nhật ký.</td></tr>'; return; }
  el.innerHTML = state.engageLogs.map(l => `<tr>
    <td><strong>${esc(l.commenter_name)}</strong></td>
    <td class="post-content-cell">${esc(l.comment_content)}</td>
    <td>${esc(l.reply_content)}</td>
    <td>${fmtTime(l.created_at)}</td>
    <td><span class="badge ${l.status==='success'?'badge-active':'badge-inactive'}">${l.status==='success'?'OK':'Lỗi'}</span></td>
    <td>${l.screenshot ? `<button class="action-btn btn-screenshot-view" onclick="viewScreenshot('${l.screenshot}')"><i class="fa-solid fa-image"></i></button>` : ''}</td>
  </tr>`).join('');
}

async function handleManualScan(e) {
  e.preventDefault();
  const accountId = v('scan-account'), postUrl = v('scan-post-url');
  if (!accountId) { alert('Chọn tài khoản.'); return; }
  const btn = setLoading(e.target, 'Đang quét...');
  const r = await post(`${API}/engagement/scan`, { account_id: accountId, post_url: postUrl });
  resetLoading(e.target, btn, '<i class="fa-solid fa-magnifying-glass"></i>Quét & Phản hồi ngay');
  if (r.error) { alert('Lỗi: ' + r.error); return; }
  alert('Đã kích hoạt quét. Nhật ký sẽ xuất hiện sau 1-2 phút.');
  e.target.reset();
}

async function handleManualAutofeed(e) {
  e.preventDefault();
  const accountId = v('autofeed-run-account'), source = v('autofeed-run-source');
  if (!accountId) { alert('Chọn tài khoản.'); return; }
  const btn = setLoading(e.target, 'Đang chạy...');
  const r = await post(`${API}/engagement/autofeed`, { account_id: accountId, source: source });
  resetLoading(e.target, btn, '<i class="fa-solid fa-robot"></i> Chạy bình luận dạo ngay');
  if (r.error) { alert('Lỗi: ' + r.error); return; }
  alert('Đã kích hoạt bình luận dạo. Quá trình quét ngầm bắt đầu và nhật ký tương tác sẽ cập nhật sau vài phút.');
  e.target.reset();
}

// ─── Auto-Like ──────────────────────────────
async function fetchAutolikeTargets() {
  const r = await fetch(`${API}/autolike/targets`);
  if (r.ok) { state.alTargets = await r.json(); renderAutolikeTargets(); }
}

function renderAutolikeTargets() {
  const el = document.getElementById('autolike-targets-list');
  if (!el) return;
  if (!state.alTargets.length) { el.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Chưa có mục tiêu.</td></tr>'; return; }
  el.innerHTML = state.alTargets.map(t => `<tr>
    <td>
      <strong>${esc(t.target_name)}</strong>
      ${t.auto_comment ? `<br><small class="text-muted" style="display:inline-flex;align-items:center;gap:3px;margin-top:2px;"><i class="fa-solid fa-comment-dots" style="color:var(--primary);"></i> Auto-Comment: ${t.comment_style}</small>` : ''}
    </td>
    <td>${esc(t.account_name||'')}</td>
    <td><a href="${esc(t.target_url)}" target="_blank" style="color:var(--primary);font-size:.8rem;">Mở link</a></td>
    <td>${t.last_run ? fmtTime(t.last_run) : '<span class="text-muted">Chưa chạy</span>'}</td>
    <td><span class="badge ${t.status==='active'?'badge-active':'badge-inactive'}">${t.status==='active'?'Bật':'Tắt'}</span></td>
    <td>
      <div class="action-icons">
        <button class="action-btn btn-run" title="Chạy ngay" onclick="runAutolikeNow('${t.id}')"><i class="fa-solid fa-play"></i></button>
        <button class="action-btn btn-delete" onclick="deleteAutolikeTarget('${t.id}')"><i class="fa-solid fa-trash"></i></button>
      </div>
    </td>
  </tr>`).join('');
}

async function handleAddAutolikeTarget(e) {
  e.preventDefault();
  const isCommentChecked = document.getElementById('autolike-comment-toggle')?.checked ? 1 : 0;
  const r = await post(`${API}/autolike/targets`, {
    account_id: v('autolike-account'),
    target_name: v('autolike-name'),
    target_url: v('autolike-url'),
    auto_comment: isCommentChecked,
    comment_style: v('autolike-comment-style') || 'AI',
    comment_text: v('autolike-comment-text') || ''
  });
  if (r.error) { alert('Lỗi: ' + r.error); return; }
  alert('Đã thêm mục tiêu tương tác tự động!');
  e.target.reset();
  if (window.toggleCommentStyleGroup) window.toggleCommentStyleGroup();
  await fetchAutolikeTargets();
}

async function deleteAutolikeTarget(id) {
  if (!confirm('Xóa mục tiêu?')) return;
  await fetch(`${API}/autolike/targets/${id}`, { method: 'DELETE' });
  await fetchAutolikeTargets();
}

async function runAutolikeNow(id) {
  const r = await post(`${API}/autolike/run`, { target_id: id });
  if (r.error) { alert('Lỗi: ' + r.error); return; }
  alert('Đã kích hoạt Auto-Like trong nền. Nhật ký sẽ cập nhật sau vài phút.');
}

async function fetchAutolikeLogs() {
  const r = await fetch(`${API}/autolike/logs`);
  if (r.ok) { state.alLogs = await r.json(); renderAutolikeLogs(); }
}

function renderAutolikeLogs() {
  const el = document.getElementById('autolike-logs-list');
  if (!el) return;
  if (!state.alLogs.length) { el.innerHTML = '<tr><td colspan="3" class="text-center text-muted">Chưa có nhật ký.</td></tr>'; return; }
  el.innerHTML = state.alLogs.map(l => `<tr>
    <td class="post-content-cell"><a href="${esc(l.post_url)}" target="_blank" style="color:var(--primary);font-size:.82rem;">${esc(l.post_url)}</a></td>
    <td>${fmtTime(l.created_at)}</td>
    <td><span class="badge ${l.status==='success'?'badge-active':'badge-inactive'}">${l.status==='success'?'OK':'Lỗi'}</span></td>
  </tr>`).join('');
}

// ─── Templates ──────────────────────────────
async function fetchTemplates() {
  const r = await fetch(`${API}/templates`);
  if (r.ok) { state.templates = await r.json(); renderTemplates(); }
}

function renderTemplates() {
  const el = document.getElementById('templates-list');
  if (!el) return;
  if (!state.templates.length) { el.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Chưa có mẫu nào.</td></tr>'; return; }
  el.innerHTML = state.templates.map(t => `<tr>
    <td><strong>${esc(t.name)}</strong></td>
    <td>${t.tags ? t.tags.split(',').map(tag => `<span class="badge badge-posting">${esc(tag.trim())}</span>`).join(' ') : '-'}</td>
    <td class="post-content-cell">${esc(t.content)}</td>
    <td>${fmtTime(t.created_at)}</td>
    <td>
      <div class="action-icons">
        <button class="action-btn btn-post-now" title="Dùng mẫu này" onclick="openTemplateModal('${t.id}')"><i class="fa-solid fa-arrow-up-right-from-square"></i></button>
        <button class="action-btn btn-delete" onclick="deleteTemplate('${t.id}')"><i class="fa-solid fa-trash"></i></button>
      </div>
    </td>
  </tr>`).join('');
}

async function handleSaveTemplate(e) {
  e.preventDefault();
  const r = await post(`${API}/templates`, { name: v('tpl-name'), content: v('tpl-content'), tags: v('tpl-tags') });
  if (r.error) { alert('Lỗi: ' + r.error); return; }
  alert('Đã lưu mẫu!'); e.target.reset(); await fetchTemplates();
}

async function deleteTemplate(id) {
  if (!confirm('Xóa mẫu?')) return;
  await fetch(`${API}/templates/${id}`, { method: 'DELETE' });
  await fetchTemplates();
}

function openTemplateModal(id) {
  const tpl = state.templates.find(t => t.id === id);
  if (!tpl) return;
  state.selectedTemplateContent = tpl.content;
  document.getElementById('modal-template-content').textContent = tpl.content;
  document.getElementById('template-use-modal').classList.add('active');
}

function closeTemplateModal() {
  document.getElementById('template-use-modal').classList.remove('active');
}

function applyTemplate() {
  document.getElementById('post-content').value = state.selectedTemplateContent;
  closeTemplateModal();
  switchTab('create-post');
}

// ─── UI helpers ─────────────────────────────
function toggleTargetIdPlaceholder() {
  const type = v('post-type');
  const label = document.getElementById('target-id-label');
  const input = document.getElementById('post-target-id');
  const hint  = document.getElementById('target-id-hint');
  if (type === 'profile') { label.textContent = 'ID cá nhân'; input.value = 'me'; input.placeholder = 'me'; hint.textContent = 'Điền "me" để đăng lên tường nhà mình.'; }
  else if (type === 'group') { label.textContent = 'ID Nhóm'; input.value = ''; input.placeholder = 'VD: 123456789'; hint.textContent = 'Lấy ID từ link nhóm Facebook.'; }
  else { label.textContent = 'ID / Username Trang'; input.value = ''; input.placeholder = 'VD: mypage'; hint.textContent = 'Tên trang hoặc ID số của Fanpage.'; }
}

function handleFilePreview() {
  const inp = document.getElementById('post-media');
  const cnt = document.getElementById('file-count');
  const con = document.getElementById('media-preview-container');
  con.innerHTML = '';
  if (!inp.files.length) { cnt.textContent = 'Chưa chọn file nào'; return; }
  cnt.textContent = `Đã chọn ${inp.files.length} file`;
  Array.from(inp.files).forEach(file => {
    const reader = new FileReader();
    reader.onload = e => {
      const wrap = document.createElement('div');
      wrap.className = 'media-preview-item';
      wrap.innerHTML = `<img src="${e.target.result}"><button class="remove-btn" onclick="clearFiles()">&times;</button>`;
      con.appendChild(wrap);
    };
    reader.readAsDataURL(file);
  });
}

function clearFiles() {
  document.getElementById('post-media').value = '';
  document.getElementById('file-count').textContent = 'Chưa chọn file nào';
  document.getElementById('media-preview-container').innerHTML = '';
  aiGeneratedImages = [];
}

function viewScreenshot(path) {
  document.getElementById('modal-image').src = `${API}/uploads/${path}`;
  document.getElementById('screenshot-modal').classList.add('active');
}

function closeScreenshotModal() {
  document.getElementById('screenshot-modal').classList.remove('active');
}

// ─── Micro-utilities ────────────────────────
const v    = id => document.getElementById(id)?.value || '';
const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
const setText = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
const esc  = str => str ? String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;') : '';
const typeLabel = t => ({ profile:'Cá nhân', group:'Nhóm', page:'Fanpage' }[t] || t);

function fmtTime(iso) {
  if (!iso) return '-';
  try {
    const d = new Date(iso);
    if (isNaN(d)) return iso;
    return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')} ${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}/${d.getFullYear()}`;
  } catch { return iso; }
}

function statusBadge(s) {
  const map = {
    pending:  ['badge-pending', 'Đang chờ'],
    pending_approval: ['badge-pending', '<i class="fa-solid fa-hourglass-half"></i> Chờ duyệt'],
    posting:  ['badge-posting', '<i class="fa-solid fa-spinner fa-spin"></i> Đang đăng'],
    posted:   ['badge-active',  '<i class="fa-solid fa-check"></i> Đã đăng'],
    failed:   ['badge-inactive','<i class="fa-solid fa-xmark"></i> Thất bại'],
    completed:['badge-active',  '<i class="fa-solid fa-check"></i> Hoàn tất'],
    running:  ['badge-posting', '<i class="fa-solid fa-spinner fa-spin"></i> Đang chạy'],
  };
  const [cls, label] = map[s] || ['badge-pending', s];
  return `<span class="badge ${cls}">${label}</span>`;
}

async function post(url, data) {
  try {
    const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    const text = await r.text();
    let parsed;
    try {
      parsed = JSON.parse(text);
    } catch (e) {
      return { error: `Phản hồi từ máy chủ không phải là JSON hợp lệ (Mã HTTP: ${r.status}).` };
    }
    if (!r.ok) {
      return { error: parsed.error || `Lỗi máy chủ (Mã HTTP: ${r.status}).` };
    }
    return parsed;
  } catch (err) {
    return { error: `Lỗi kết nối: ${err.message}` };
  }
}

function setLoading(form, text) {
  const btn = form.querySelector('button[type="submit"]');
  if (btn) { btn._original = btn.innerHTML; btn.disabled = true; btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>${text}`; }
  return btn;
}

function resetLoading(form, btn, text) {
  if (btn) { btn.disabled = false; btn.innerHTML = text; }
}

// ─── AI Assistant ───────────────────────────
async function generateAIText() {
  const shopeeUrl = document.getElementById('ai-shopee-url').value.trim();
  const prompt = document.getElementById('ai-prompt-text').value;
  const btn = document.getElementById('btn-ai-write');
  
  btn._original = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang soạn bài...`;
  
  try {
    const res = await post(`${API}/ai/generate-text`, { shopee_url: shopeeUrl, prompt: prompt });
    if (res.error) {
      alert("Lỗi: " + res.error);
    } else {
      if (res.text) {
        document.getElementById('post-content').value = res.text;
      }
      if (res.shopee_image) {
        clearFiles();
        aiGeneratedImages.push(res.shopee_image);
        
        const con = document.getElementById('media-preview-container');
        const wrap = document.createElement('div');
        wrap.className = 'media-preview-item';
        wrap.innerHTML = `<img src="${API}/uploads/${res.shopee_image}"><button class="remove-btn" onclick="clearFiles()">&times;</button>`;
        con.appendChild(wrap);
        
        document.getElementById('file-count').textContent = "Đã chọn 1 ảnh Shopee";
        
        const redirectToggle = document.getElementById('post-redirect-toggle');
        if (redirectToggle) {
          redirectToggle.checked = true;
          toggleRedirectFields();
        }
        
        const rUrl = document.getElementById('post-redirect-url');
        if (rUrl) rUrl.value = shopeeUrl;
        
        const rTitle = document.getElementById('post-redirect-title');
        if (rTitle) rTitle.value = res.product_title || '';
        
        const rDesc = document.getElementById('post-redirect-desc');
        if (rDesc) rDesc.value = 'Giá cực tốt - Mua ngay trên Shopee!';
      }
    }
  } catch (err) {
    alert("Lỗi kết nối server: " + err);
  } finally {
    btn.disabled = false;
    btn.innerHTML = btn._original;
  }
}

async function generateAIImage() {
  const prompt = document.getElementById('ai-prompt-image').value.trim();
  if (!prompt) {
    alert("Vui lòng cung cấp mô tả hình ảnh muốn tạo.");
    return;
  }
  const btn = document.getElementById('btn-ai-image');
  
  btn._original = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang vẽ ảnh AI...`;
  
  try {
    const res = await post(`${API}/ai/generate-image`, { prompt: prompt });
    if (res.error) {
      alert("Lỗi: " + res.error);
    } else if (res.filename) {
      aiGeneratedImages.push(res.filename);
      
      const con = document.getElementById('media-preview-container');
      const wrap = document.createElement('div');
      wrap.className = 'media-preview-item';
      wrap.innerHTML = `<img src="${API}/uploads/${res.filename}"><button class="remove-btn" onclick="clearFiles()">&times;</button>`;
      con.appendChild(wrap);
      
      document.getElementById('file-count').textContent = `Đã chọn ${aiGeneratedImages.length} file AI`;
    }
  } catch (err) {
    alert("Lỗi kết nối server: " + err);
  } finally {
    btn.disabled = false;
    btn.innerHTML = btn._original;
  }
}

// ─── Auto-Comment form toggles ────────────────
window.toggleCommentStyleGroup = function() {
  const toggle = document.getElementById('autolike-comment-toggle');
  const group = document.getElementById('autolike-comment-style-group');
  if (toggle && group) {
    if (toggle.checked) {
      group.style.display = 'block';
      window.toggleSpintaxTextGroup();
    } else {
      group.style.display = 'none';
      const textGroup = document.getElementById('autolike-comment-text-group');
      if (textGroup) textGroup.style.display = 'none';
    }
  }
};

window.toggleSpintaxTextGroup = function() {
  const style = document.getElementById('autolike-comment-style')?.value || 'AI';
  const textGroup = document.getElementById('autolike-comment-text-group');
  if (textGroup) {
    textGroup.style.display = (style === 'spintax') ? 'block' : 'none';
  }
};

window.toggleCookiePlaceholder = function() {
  const platform = document.getElementById('acc-platform')?.value || 'facebook';
  const label = document.getElementById('acc-cookie-label');
  const textarea = document.getElementById('acc-cookie');
  const hint = document.getElementById('acc-cookie-hint');
  if (platform === 'threads') {
    if (label) label.textContent = 'Cookie Threads (Meta)';
    if (textarea) textarea.placeholder = 'Dán cookie JSON từ EditThisCookie hoặc chuỗi token threads.net...';
    if (hint) hint.innerHTML = '💡 Dùng EditThisCookie trên trang <b>threads.net</b> → Export → dán ở đây.';
  } else {
    if (label) label.textContent = 'Cookie Facebook';
    if (textarea) textarea.placeholder = 'Dán cookie JSON từ EditThisCookie hoặc chuỗi c_user=...; xs=...';
    if (hint) hint.innerHTML = '💡 Dùng EditThisCookie trên trang <b>facebook.com</b> → Export → dán ở đây.';
  }
};

window.cleanTargetIdInput = function(inputId) {
  const el = document.getElementById(inputId);
  if (!el) return;
  el.addEventListener('input', (e) => {
    let val = e.target.value.trim();
    if (val.includes('facebook.com') || val.includes('fb.com')) {
      if (val.includes('/groups/')) {
        const match = val.match(/\/groups\/([^/?#\s]+)/);
        if (match) {
          e.target.value = match[1];
        }
      } else {
        if (val.includes('profile.php')) {
          try {
            const urlObj = new URL(val);
            const id = urlObj.searchParams.get('id');
            if (id) {
              e.target.value = id;
              return;
            }
          } catch(err) {}
        }
        const cleanUrl = val.split('?')[0].split('#')[0];
        const parts = cleanUrl.replace(/\/+$/, '').split('/');
        const lastPart = parts[parts.length - 1];
        if (lastPart && lastPart !== 'facebook.com' && lastPart !== 'fb.com') {
          e.target.value = lastPart;
        }
      }
    }
  });
};

// ─── API: Link Analyzer ─────────────────────
async function handleLinkAnalysis(e) {
  e.preventDefault();
  const url = v('analyzer-url');
  const accountId = v('analyzer-account');
  if (!url || !accountId) {
    alert('Vui lòng chọn tài khoản và điền liên kết cần phân tích.');
    return;
  }
  
  const btnSubmit = document.getElementById('btn-analyzer-submit');
  const originalHtml = btnSubmit.innerHTML;
  btnSubmit.disabled = true;
  btnSubmit.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang phân tích...';
  
  try {
    const res = await fetch(`${API}/analyze-link`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, account_id: accountId })
    });
    
    let data;
    const text = await res.text();
    try {
      data = JSON.parse(text);
    } catch (e) {
      throw new Error(`Phản hồi từ máy chủ không phải là JSON hợp lệ (Mã HTTP: ${res.status}).`);
    }

    if (!res.ok) {
      throw new Error(data.error || 'Lỗi không xác định từ máy chủ.');
    }
    
    // Display results
    document.getElementById('analyzer-result-card').style.display = 'block';
    document.getElementById('analyzer-link-type').textContent = data.link_type_vi;
    
    // Render Actors
    const actorsList = document.getElementById('analyzer-actors-list');
    actorsList.innerHTML = data.actors.map(actor => `
      <li>
        <strong>${esc(actor.name)}</strong>: ${esc(actor.description)} 
        <span class="badge ${actor.role === 'lead' ? 'badge-active' : 'badge-posting'}" style="font-size:0.68rem; margin-left:5px;">
          ${actor.role === 'lead' ? 'Target Lead' : 'Chủ thể'}
        </span>
      </li>
    `).join('');
    
    // Render Proposals
    const proposalsContainer = document.getElementById('analyzer-proposals-container');
    proposalsContainer.innerHTML = data.proposals.map((prop, idx) => {
      // Escape JSON safely for onclick
      const dataStr = encodeURIComponent(JSON.stringify(prop.action_data));
      return `
        <div class="proposal-card">
          <div class="proposal-card-header">
            <div class="proposal-card-title">
              <i class="fa-solid fa-square-poll-horizontal" style="color:var(--accent); margin-right:6px;"></i> ${esc(prop.title)}
            </div>
          </div>
          <div class="proposal-card-desc">${esc(prop.description)}</div>
          <div class="proposal-card-footer">
            <button class="btn btn-secondary btn-sm" onclick="activateProposal('${prop.action_type}', '${dataStr}')">
              <i class="fa-solid fa-circle-play" style="margin-right:4px;"></i> ${esc(prop.btn_text)}
            </button>
          </div>
        </div>
      `;
    }).join('');
    
  } catch (err) {
    alert('Lỗi khi phân tích: ' + err.message);
  } finally {
    btnSubmit.disabled = false;
    btnSubmit.innerHTML = originalHtml;
  }
}

// Function to activate proposal action and auto-fill forms
function activateProposal(actionType, encodedData) {
  const data = JSON.parse(decodeURIComponent(encodedData));
  
  if (actionType === 'autolike') {
    switchTab('autolike');
    setVal('autolike-url', data.target_url);
    setVal('autolike-name', data.target_name);
    // Focus the target input
    document.getElementById('autolike-url').focus();
    
    // If auto_comment option is specified, check it
    if (data.auto_comment) {
      const checkbox = document.getElementById('autolike-comment-toggle');
      if (checkbox) {
        checkbox.checked = true;
        if (window.toggleCommentStyleGroup) window.toggleCommentStyleGroup();
      }
      if (data.comment_style) {
        setVal('autolike-comment-style', data.comment_style);
        if (window.toggleSpintaxTextGroup) window.toggleSpintaxTextGroup();
      }
      if (data.comment_text) {
        setVal('autolike-comment-text', data.comment_text);
      }
    }
  } 
  else if (actionType === 'post') {
    switchTab('create-post');
    setVal('post-type', data.type);
    setVal('post-target-id', data.target_id);
    if (data.content) {
      setVal('post-content', data.content);
    }
    // Check if platform is threads
    const accountId = v('analyzer-account');
    if (accountId) {
      setVal('post-account', accountId);
    }
    document.getElementById('post-content').focus();
  } 
  else if (actionType === 'auto_reply') {
    switchTab('engage');
    setVal('scan-post-url', data.post_url);
    const accountId = v('analyzer-account');
    if (accountId) {
      setVal('scan-account', accountId);
    }
    document.getElementById('scan-post-url').focus();
  }
}

// ─── Target Lists ────────────────────────────
async function fetchTargetLists() {
  const r = await fetch(`${API}/target-lists`);
  if (r.ok) {
    state.targetLists = await r.json();
    renderTargetLists();
    populateTargetListsDropdown();
  }
}

function renderTargetLists() {
  const el = document.getElementById('target-lists-table-body');
  if (!el) return;
  if (!state.targetLists || !state.targetLists.length) {
    el.innerHTML = '<tr><td colspan="3" class="text-center text-muted">Chưa có danh sách nào.</td></tr>';
    return;
  }
  el.innerHTML = state.targetLists.map(tl => {
    const lineCount = tl.targets.trim().split('\n').filter(Boolean).length;
    return `<tr>
      <td><strong>${esc(tl.name)}</strong></td>
      <td>${lineCount} mục tiêu</td>
      <td>
        <button class="btn btn-danger btn-xs" onclick="deleteTargetList('${tl.id}')"><i class="fa-solid fa-trash"></i> Xóa</button>
      </td>
    </tr>`;
  }).join('');
}

function populateTargetListsDropdown() {
  const select = document.getElementById('bulk-apply-target-list');
  if (select) {
    const currentVal = select.value;
    select.innerHTML = '<option value="">-- Chọn danh sách mục tiêu --</option>' +
      state.targetLists.map(tl => `<option value="${tl.id}">${esc(tl.name)} (${tl.targets.trim().split('\n').filter(Boolean).length} mục tiêu)</option>`).join('');
    select.value = currentVal;
  }
  
  const selectAutolike = document.getElementById('autolike-apply-target-list');
  if (selectAutolike) {
    const currentVal = selectAutolike.value;
    selectAutolike.innerHTML = '<option value="">-- Chọn danh sách mục tiêu --</option>' +
      state.targetLists.map(tl => `<option value="${tl.id}">${esc(tl.name)} (${tl.targets.trim().split('\n').filter(Boolean).length} mục tiêu)</option>`).join('');
    selectAutolike.value = currentVal;
  }

  const selectPost = document.getElementById('post-target-list');
  if (selectPost) {
    const currentVal = selectPost.value;
    selectPost.innerHTML = '<option value="">-- Chọn danh sách mục tiêu --</option>' +
      state.targetLists.map(tl => `<option value="${tl.id}">${esc(tl.name)} (${tl.targets.trim().split('\n').filter(Boolean).length} mục tiêu)</option>`).join('');
    selectPost.value = currentVal;
  }
}

function applySavedTargetList(listId) {
  if (!listId) {
    document.getElementById('bulk-targets').value = '';
    return;
  }
  const tl = state.targetLists.find(x => x.id === listId);
  if (tl) {
    document.getElementById('bulk-targets').value = tl.targets;
  }
}

function applySavedTargetListToAutolike(listId) {
  if (!listId) {
    document.getElementById('autolike-url').value = '';
    return;
  }
  const tl = state.targetLists.find(x => x.id === listId);
  if (tl) {
    document.getElementById('autolike-url').value = tl.targets;
  }
}

function togglePostTargetListSelection(listId) {
  const postType = document.getElementById('post-type');
  const postTargetId = document.getElementById('post-target-id');
  const hint = document.getElementById('target-id-hint');
  if (!postType || !postTargetId) return;

  if (listId) {
    postType.disabled = true;
    postTargetId.disabled = true;
    postTargetId.removeAttribute('required');
    postTargetId.value = '';
    if (hint) hint.textContent = '⚠️ Bị vô hiệu hóa do đã chọn đăng lên nhóm mục tiêu.';
  } else {
    postType.disabled = false;
    postTargetId.disabled = false;
    postTargetId.setAttribute('required', 'required');
    toggleTargetIdPlaceholder();
  }
}

function toggleRedirectFields() {
  const toggle = document.getElementById('post-redirect-toggle');
  const group = document.getElementById('redirect-fields-group');
  if (!toggle || !group) return;

  if (toggle.checked) {
    group.style.display = 'block';
  } else {
    group.style.display = 'none';
    document.getElementById('post-redirect-url').value = '';
    document.getElementById('post-redirect-title').value = '';
    document.getElementById('post-redirect-desc').value = '';
  }
}

async function showSaveTargetListModal() {
  const targets = document.getElementById('bulk-targets').value.trim();
  if (!targets) {
    alert("Vui lòng nhập danh sách mục tiêu vào ô trước khi lưu!");
    return;
  }
  const name = prompt("Nhập tên cho danh sách mục tiêu mới này (Ví dụ: Nhóm Chợ Online):");
  if (!name) return; // User cancelled
  
  try {
    const r = await post(`${API}/target-lists`, { name, targets });
    alert(`Đã lưu danh sách mục tiêu "${name}" thành công!`);
    await fetchTargetLists();
  } catch (err) {
    alert("Có lỗi xảy ra: " + err.message);
  }
}

async function deleteTargetList(id) {
  if (!confirm("Bạn có chắc chắn muốn xóa danh sách mục tiêu này không?")) return;
  try {
    const r = await fetch(`${API}/target-lists/${id}`, { method: 'DELETE' });
    if (r.ok) {
      await fetchTargetLists();
    }
  } catch (err) {
    alert("Có lỗi xảy ra khi xóa: " + err.message);
  }
}

// ─── Auto-Join Groups ────────────────────────
window.toggleAutojoinInputs = function() {
  const type = document.getElementById('autojoin-source-type').value;
  const urlsGroup = document.getElementById('autojoin-urls-group');
  const keywordGroup = document.getElementById('autojoin-keyword-group');
  
  if (type === 'urls') {
    if (urlsGroup) urlsGroup.style.display = 'block';
    if (keywordGroup) keywordGroup.style.display = 'none';
  } else {
    if (urlsGroup) urlsGroup.style.display = 'none';
    if (keywordGroup) keywordGroup.style.display = 'block';
  }
};

async function fetchAutojoinLogs() {
  try {
    const res = await fetch(`${API}/autojoin/logs`);
    if (!res.ok) return;
    const logs = await res.json();
    const tbody = document.getElementById('autojoin-logs-list');
    if (!tbody) return;
    
    if (logs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">Chưa có nhật ký tham gia nhóm nào.</td></tr>`;
      return;
    }
    
    tbody.innerHTML = logs.map(log => {
      let statusBadge = '';
      if (log.status === 'success') {
        statusBadge = '<span class="badge badge-success">Thành công</span>';
      } else if (log.status === 'pending_approval') {
        statusBadge = '<span class="badge badge-warning">Chờ duyệt</span>';
      } else if (log.status === 'already_member') {
        statusBadge = '<span class="badge badge-info">Đã tham gia</span>';
      } else {
        statusBadge = '<span class="badge badge-danger">Thất bại</span>';
      }
      
      const timeStr = log.created_at ? new Date(log.created_at).toLocaleString('vi-VN') : '';
      return `
        <tr>
          <td class="text-truncate" style="max-width: 250px;" title="${log.target_name_or_url}">${log.target_name_or_url}</td>
          <td>${timeStr}</td>
          <td>${statusBadge}</td>
          <td class="text-wrap" style="max-width: 300px;">${log.details || ''}</td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error("Lỗi tải nhật ký tham gia nhóm:", err);
  }
}

async function handleStartAutojoin(e) {
  e.preventDefault();
  const accountId = document.getElementById('autojoin-account').value;
  const sourceType = document.getElementById('autojoin-source-type').value;
  const urls = document.getElementById('autojoin-urls').value.trim();
  const keyword = document.getElementById('autojoin-keyword').value.trim();
  const limit = parseInt(document.getElementById('autojoin-limit').value) || 5;
  const delay = parseInt(document.getElementById('autojoin-delay').value) || 15;
  const answerQuestions = document.getElementById('autojoin-answer-questions').checked;
  
  if (!accountId) {
    alert("Vui lòng chọn tài khoản.");
    return;
  }
  if (sourceType === 'urls' && !urls) {
    alert("Vui lòng nhập danh sách URL / ID nhóm.");
    return;
  }
  if (sourceType === 'keyword' && !keyword) {
    alert("Vui lòng nhập từ khóa tìm kiếm.");
    return;
  }
  
  const form = e.target;
  const btn = setLoading(form, 'Đang chuẩn bị...');
  
  try {
    const r = await fetch(`${API}/autojoin/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        account_id: accountId,
        source_type: sourceType,
        urls: urls,
        keyword: keyword,
        limit: limit,
        delay: delay,
        answer_questions: answerQuestions
      })
    });
    
    const res = await r.json();
    if (r.ok && res.success) {
      alert("Đã bắt đầu tiến trình tham gia nhóm chạy ngầm! Bạn có thể theo dõi kết quả ở bảng Nhật ký.");
      document.getElementById('autojoin-urls').value = '';
      document.getElementById('autojoin-keyword').value = '';
      fetchAutojoinLogs();
    } else {
      alert("Lỗi: " + (res.error || "Không khởi động được tiến trình."));
    }
  } catch (err) {
    alert("Lỗi kết nối máy chủ: " + err.message);
  } finally {
    resetLoading(form, btn, '<i class="fa-solid fa-user-plus"></i> Bắt đầu tự động tham gia');
  }
}

async function handleStartTopicCampaign(e) {
  e.preventDefault();
  const accountId = document.getElementById('autojoin-topic-account').value;
  const topics = document.getElementById('autojoin-topics').value.trim();
  const limit = parseInt(document.getElementById('autojoin-topic-limit').value) || 50;
  const delay = parseInt(document.getElementById('autojoin-topic-delay').value) || 15;
  const prioritize = document.getElementById('autojoin-topic-prioritize') ? document.getElementById('autojoin-topic-prioritize').checked : true;
  
  if (!accountId) {
    alert("Vui lòng chọn tài khoản.");
    return;
  }
  if (!topics) {
    alert("Vui lòng nhập danh sách chủ đề.");
    return;
  }
  
  const form = e.target;
  const btn = setLoading(form, 'Đang khởi chạy chiến dịch...');
  
  try {
    const r = await fetch(`${API}/autojoin/topic-campaign`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        account_id: accountId,
        topics: topics,
        limit_per_topic: limit,
        delay: delay,
        answer_questions: true,
        prioritize: prioritize
      })
    });
    
    const res = await r.json();
    if (r.ok && res.success) {
      alert("Chiến dịch tham gia nhóm theo chủ đề đã được kích hoạt chạy ngầm thành công! Theo dõi nhật ký ở bảng bên cạnh.");
      document.getElementById('autojoin-topics').value = '';
      fetchAutojoinLogs();
    } else {
      alert("Lỗi: " + (res.error || "Không khởi động được chiến dịch."));
    }
  } catch (err) {
    alert("Lỗi kết nối máy chủ: " + err.message);
  } finally {
    resetLoading(form, btn, '<i class="fa-solid fa-bullhorn"></i> Bắt đầu chiến dịch chủ đề');
  }
}

window.clearAutojoinLogs = async function() {
  if (!confirm("Bạn có chắc chắn muốn xóa toàn bộ nhật ký tham gia nhóm không?")) return;
  try {
    const r = await fetch(`${API}/autojoin/logs`, { method: 'DELETE' });
    if (r.ok) {
      fetchAutojoinLogs();
    } else {
      alert("Lỗi khi xóa nhật ký.");
    }
  } catch (err) {
    alert("Lỗi kết nối: " + err.message);
  }
};

window.syncPublicGroups = async function() {
  const accountId = document.getElementById('autojoin-account').value;
  if (!accountId) {
    alert("Vui lòng chọn tài khoản để đồng bộ nhóm công khai.");
    return;
  }
  
  if (!confirm("Bắt đầu đồng bộ nhóm công khai của tài khoản này? Quá trình sẽ chạy ngầm, bạn có thể theo dõi tiến trình trong bảng Nhật ký.")) {
    return;
  }
  
  try {
    const r = await fetch(`${API}/autojoin/sync-public-groups`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account_id: accountId, limit: 30 })
    });
    
    const res = await r.json();
    if (r.ok && res.success) {
      alert("Đã khởi chạy tiến trình quét nhóm công khai chạy ngầm!");
      fetchAutojoinLogs();
    } else {
      alert("Lỗi: " + (res.error || "Không khởi động được tiến trình."));
    }
  } catch (err) {
    alert("Lỗi kết nối máy chủ: " + err.message);
  }
};

async function handleShopeeBulkImport(e) {
  e.preventDefault();
  const urls = document.getElementById('shopee-bulk-urls').value.trim();
  if (!urls) {
    alert("Vui lòng nhập ít nhất một link Shopee.");
    return;
  }
  
  const topic = document.getElementById('shopee-bulk-topic').value;
  if (!topic) {
    alert("Vui lòng chọn chủ đề bài đăng.");
    return;
  }
  
  const form = e.target;
  const btn = setLoading(form, 'Đang chuẩn bị...');
  
  try {
    const r = await fetch(`${API}/shopee/bulk-import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls: urls, topic: topic })
    });
    
    const res = await r.json();
    if (r.ok && res.success) {
      alert("Đã bắt đầu cào và lên lịch đăng Shopee hàng loạt chạy ngầm! Bạn có thể xem danh sách bài đăng ở tab Lịch sử & Hẹn giờ.");
      document.getElementById('shopee-bulk-urls').value = '';
      await fetchPosts();
    } else {
      alert("Lỗi: " + (res.error || "Không thể thực hiện tác vụ."));
    }
  } catch (err) {
    alert("Lỗi kết nối máy chủ: " + err.message);
  } finally {
    resetLoading(form, btn, '<i class="fa-solid fa-cloud-arrow-up"></i> Tự động cào & Lên lịch');
  }
}

// ─── Claude Schedule Import ───────────────────────────
async function handleClaudeScheduleImport(e) {
  e.preventDefault();
  const form = e.target;
  const btn = form.querySelector('[type=submit]');
  const originalText = btn.innerHTML;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xử lý...';
  btn.disabled = true;

  const jsonRaw = document.getElementById('claude-schedule-json').value.trim();
  const shopeeLink = document.getElementById('claude-shopee-link').value.trim();
  const accountId = document.getElementById('claude-schedule-account').value.trim();

  // Parse JSON
  let items;
  try {
    items = JSON.parse(jsonRaw);
    if (!Array.isArray(items)) throw new Error('Dữ liệu phải là mảng JSON.');
  } catch (err) {
    alert('JSON không hợp lệ: ' + err.message);
    btn.innerHTML = originalText;
    btn.disabled = false;
    return;
  }

  try {
    const res = await post('/api/import-claude-schedule', {
      items,
      shopee_link: shopeeLink,
      account_id: accountId
    });

    const resultDiv = document.getElementById('claude-schedule-result');
    const resultContent = document.getElementById('claude-schedule-result-content');
    resultDiv.style.display = 'block';

    if (res.success) {
      let html = `<div style="color:var(--green);font-size:1rem;margin-bottom:.75rem;"><i class="fa-solid fa-circle-check"></i> <b>${res.created}/${items.length}</b> bài đăng đã được lên lịch thành công!</div>`;
      if (shopeeLink) {
        html += `<p style="font-size:.85rem;color:var(--text-muted);">Link Shopee <code>${shopeeLink}</code> sẽ tự động bình luận dưới mỗi bài sau khi đăng.</p>`;
      }
      if (res.errors && res.errors.length > 0) {
        html += `<div style="margin-top:.5rem;"><b style="color:var(--yellow);">Cảnh báo (${res.errors.length}):</b><ul style="font-size:.8rem;margin:.25rem 0 0 1rem;">${res.errors.map(e => `<li>${e}</li>`).join('')}</ul></div>`;
      }
      html += `<div style="margin-top:1rem;"><button class="btn btn-secondary btn-sm" onclick="switchTab('posts')"><i class="fa-solid fa-clock-rotate-left"></i> Xem lịch sử bài đăng</button></div>`;
      resultContent.innerHTML = html;
    } else {
      resultContent.innerHTML = `<div style="color:var(--red);"><i class="fa-solid fa-circle-xmark"></i> Lỗi: ${res.error || 'Không thể import.'}</div>`;
    }
  } catch (err) {
    alert('Lỗi kết nối máy chủ: ' + err.message);
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

// Load accounts vào dropdown claude-schedule khi chuyển tab
const _origSwitchTab = typeof switchTab === 'function' ? switchTab : null;
function populateClaudeScheduleAccounts() {
  const sel = document.getElementById('claude-schedule-account');
  if (!sel) return;
  sel.innerHTML = '<option value="auto_route">-- Tự động phân luồng theo chủ đề --</option>';
  (state.accounts || []).filter(a => a.status === 'active').forEach(a => {
    const opt = document.createElement('option');
    opt.value = a.id;
    opt.textContent = a.name || a.id;
    sel.appendChild(opt);
  });
}

// ─── Load JSON file into textarea ─────────────────────
function loadJsonFile(input) {
  const file = input.files[0];
  if (!file) return;

  const nameSpan = document.getElementById('claude-json-filename');
  nameSpan.textContent = '⏳ Đang đọc...';

  const reader = new FileReader();
  reader.onload = function(e) {
    const text = e.target.result;
    try {
      // Validate JSON
      const parsed = JSON.parse(text);
      const pretty = JSON.stringify(parsed, null, 2);
      document.getElementById('claude-schedule-json').value = pretty;
      nameSpan.textContent = `✅ ${file.name} (${parsed.length} bài)`;
      nameSpan.style.color = 'var(--green)';
    } catch (err) {
      nameSpan.textContent = `❌ File không hợp lệ: ${err.message}`;
      nameSpan.style.color = 'var(--red)';
    }
    // Reset input để có thể chọn lại cùng file
    input.value = '';
  };
  reader.onerror = function() {
    nameSpan.textContent = '❌ Không thể đọc file.';
    nameSpan.style.color = 'var(--red)';
  };
  reader.readAsText(file, 'utf-8');
}

// ─── Edit Post Modal ───────────────────────────────────
function openEditPost(postId) {
  const p = state.posts.find(x => x.id === postId);
  if (!p) { alert('Không tìm thấy bài đăng.'); return; }

  // Populate modal fields
  document.getElementById('edit-post-id').value = p.id;
  document.getElementById('edit-post-original-content').value = p.content || '';
  document.getElementById('edit-post-content').value = p.content || '';
  document.getElementById('edit-post-target').value = p.target_id || '';
  document.getElementById('edit-post-type').value = p.type || 'group';
  const dt = p.scheduled_at ? p.scheduled_at.replace(' ', 'T').slice(0, 16) : '';
  document.getElementById('edit-post-scheduled').value = dt;
  document.getElementById('edit-post-comment').value = p.first_comment || '';
  // Reset checkbox
  document.getElementById('edit-apply-similar').checked = false;

  // Show count of similar pending posts
  const similarCount = state.posts.filter(x => x.content === p.content && x.status === 'pending' && x.id !== p.id).length;
  const chkLabel = document.querySelector('#edit-apply-similar + span b');
  if (chkLabel) chkLabel.textContent = `Áp dụng thay đổi cho tất cả bài có nội dung giống (${similarCount} bài khác)`;

  document.getElementById('edit-post-modal').classList.add('active');
}

function closeEditModal() {
  document.getElementById('edit-post-modal').classList.remove('active');
}

async function handleSaveEditPost() {
  const postId = document.getElementById('edit-post-id').value;
  const originalContent = document.getElementById('edit-post-original-content').value;
  const content = document.getElementById('edit-post-content').value.trim();
  const target = document.getElementById('edit-post-target').value.trim();
  const type = document.getElementById('edit-post-type').value;
  const scheduled = document.getElementById('edit-post-scheduled').value;
  const comment = document.getElementById('edit-post-comment').value.trim();
  const applyToSimilar = document.getElementById('edit-apply-similar').checked;

  if (!content) { alert('Nội dung bài đăng không được để trống.'); return; }

  const btn = document.getElementById('edit-save-btn');
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang lưu...';

  try {
    const res = await fetch(`${API}/posts/${postId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content, target_id: target, type, scheduled_at: scheduled,
        first_comment: comment,
        apply_to_similar: applyToSimilar,
        original_content: originalContent
      })
    });
    const data = await res.json();
    if (data.success) {
      closeEditModal();
      await fetchPosts();
      renderDashboard();
      if (data.updated_similar > 0) {
        alert(`✅ Đã cập nhật bài này và ${data.updated_similar} bài đăng khác có nội dung giống.`);
      }
    } else {
      alert('Lỗi: ' + (data.error || 'Không thể lưu.'));
    }
  } catch (err) {
    alert('Lỗi kết nối: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Lưu thay đổi';
  }
}

// Close modal when clicking backdrop
document.addEventListener('click', e => {
  if (e.target.id === 'edit-post-modal') closeEditModal();
});

