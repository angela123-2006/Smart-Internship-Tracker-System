/* ══════════════════════════════════════════════════════════
   Smart Internship Tracker — Frontend Application
   LinkedIn-Inspired Multi-User SPA with Real-Time Updates
   ══════════════════════════════════════════════════════════ */

const API = window.location.origin;
const POLL_INTERVAL_MS = 8000;

/* ── State ───────────────────────────────────── */
let currentUser = null;
let authToken = null;
let currentPage = 'feed';
let pollTimer = null;
let authRole = 'student'; // Default toggle on auth screen

/* ══════════════════════════════════════════════
   AUTH — Token Management & Role Toggles
   ══════════════════════════════════════════════ */
function setAuthRole(role) {
  authRole = role;
  const isStudent = role === 'student';
  
  // Toggle Buttons
  document.getElementById('btn-role-student').className = isStudent ? 'btn btn-primary' : 'btn';
  document.getElementById('btn-role-student').style.background = isStudent ? '' : 'transparent';
  document.getElementById('btn-role-student').style.color = isStudent ? '' : '#666';
  
  document.getElementById('btn-role-company').className = !isStudent ? 'btn btn-primary' : 'btn';
  document.getElementById('btn-role-company').style.background = !isStudent ? '' : 'transparent';
  document.getElementById('btn-role-company').style.color = !isStudent ? '' : '#666';

  // Form Fields
  document.getElementById('form-student-fields').style.display = isStudent ? 'block' : 'none';
  document.getElementById('form-company-fields').style.display = !isStudent ? 'block' : 'none';

  // Text Updates
  document.getElementById('login-title').textContent = isStudent ? 'Student Sign in' : 'Employer Sign in';
  document.getElementById('reg-title').textContent = isStudent ? 'Join as Student' : 'Join as Employer';
}

function saveAuth(data) {
  authToken = data.token;
  currentUser = {
    user_id: data.user_id,
    role: data.role,
    name: data.name,
    email: data.email,
    department: data.department || '',
    cgpa: data.cgpa || 0,
    location: data.location || '',
    industry_type: data.industry_type || '',
    resume_path: data.resume_path || null,
  };
  localStorage.setItem('sit_token', authToken);
  localStorage.setItem('sit_user', JSON.stringify(currentUser));
}

function loadAuth() {
  authToken = localStorage.getItem('sit_token');
  const u = localStorage.getItem('sit_user');
  if (u) {
    try { currentUser = JSON.parse(u); } catch (_e) { currentUser = null; }
  }
  return !!(authToken && currentUser);
}

function clearAuth() {
  authToken = null;
  currentUser = null;
  localStorage.removeItem('sit_token');
  localStorage.removeItem('sit_user');
}

function getInitials(name) {
  if (!name) return '?';
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
}

/* ══════════════════════════════════════════════
   API Helper
   ══════════════════════════════════════════════ */
async function api(method, path, body, isFormData = false) {
  const opts = { method };
  if (authToken) {
    opts.headers = { 'Authorization': `Bearer ${authToken}` };
  } else {
    opts.headers = {};
  }
  
  if (isFormData) {
    opts.body = body;
  } else if (body) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }

  try {
    const res = await fetch(API + path, opts);
    if (res.status === 401) {
      clearAuth();
      showAuthScreen();
      toast('Session expired. Please log in again.', 'warn');
      return { success: false, error: 'Unauthorized' };
    }
    return await res.json();
  } catch (err) {
    toast('Network error. Please check your connection.', 'error');
    return { success: false, error: err.message };
  }
}

/* ══════════════════════════════════════════════
   Toast Notifications
   ══════════════════════════════════════════════ */
function toast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = 'toast ' + type;
  const icons = { success: '✅', error: '❌', warn: '⚠️', info: 'ℹ️' };
  t.innerHTML = `<span>${icons[type] || ''}</span><span>${escapeHtml(msg)}</span>`;
  document.getElementById('toast-container').appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/* ══════════════════════════════════════════════
   Screen Switching
   ══════════════════════════════════════════════ */
function showAuthScreen() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
  document.getElementById('auth-screen').style.display = 'flex';
  document.getElementById('app-screen').style.display = 'none';
  showLoginForm();
}

function showApp() {
  document.getElementById('auth-screen').style.display = 'none';
  document.getElementById('app-screen').style.display = 'block';
  
  buildNavigation();
  renderProfile();
  
  if (currentUser.role === 'company') {
    showPage('emp-postings');
  } else {
    showPage('feed');
  }
  startPolling();
}

function showLoginForm() {
  document.getElementById('login-form').style.display = 'block';
  document.getElementById('register-form').style.display = 'none';
}

function showRegisterForm() {
  document.getElementById('login-form').style.display = 'none';
  document.getElementById('register-form').style.display = 'block';
}

/* ══════════════════════════════════════════════
   AUTH — Login & Register
   ══════════════════════════════════════════════ */
async function handleLogin() {
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  if (!email || !password) return toast('Please fill in all fields', 'error');

  const btn = document.getElementById('login-btn');
  btn.disabled = true;
  btn.textContent = 'Signing in...';

  const res = await api('POST', '/api/auth/login', { email, password });

  btn.disabled = false;
  btn.textContent = 'Sign in';

  if (res.success) {
    saveAuth(res.data);
    toast('Welcome back, ' + currentUser.name + '!');
    showApp();
  } else {
    toast(res.error || 'Login failed', 'error');
  }
}

async function handleRegister() {
  const email = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  
  let payload = { role: authRole, email, password };

  if (authRole === 'student') {
    payload.name = document.getElementById('reg-name').value.trim();
    payload.department = document.getElementById('reg-dept').value.trim();
    payload.cgpa = parseFloat(document.getElementById('reg-cgpa').value);
    
    if (!payload.name || !payload.department || isNaN(payload.cgpa)) {
      return toast('Please fill in all student fields', 'error');
    }
  } else {
    payload.company_name = document.getElementById('reg-company-name').value.trim();
    payload.location = document.getElementById('reg-location').value.trim();
    payload.industry_type = document.getElementById('reg-industry').value.trim();
    
    if (!payload.company_name || !payload.location || !payload.industry_type) {
      return toast('Please fill in all employer fields', 'error');
    }
  }

  if (!email || !password) return toast('Email and password required', 'error');
  if (password.length < 6) return toast('Password must be at least 6 characters', 'error');

  const btn = document.getElementById('register-btn');
  btn.disabled = true;
  btn.textContent = 'Creating account...';

  const res = await api('POST', '/api/auth/register', payload);

  btn.disabled = false;
  btn.textContent = 'Join now';

  if (res.success) {
    saveAuth(res.data);
    toast('Welcome to Smart Internship Tracker!');
    showApp();
  } else {
    toast(res.error || (res.errors || []).join(', '), 'error');
  }
}

function handleLogout() {
  clearAuth();
  showAuthScreen();
  toast('Logged out successfully', 'info');
  closeDropdown();
}

/* ══════════════════════════════════════════════
   Navigation & Role Management
   ══════════════════════════════════════════════ */
const pageConfig = {
  // Common
  'feed':          { loader: loadFeed },
  'internships':   { loader: loadInternships },
  'applications':  { loader: loadMyApplications },
  // Student
  'skills':        { loader: loadMySkills },
  'notifications': { loader: loadMyNotifications },
  'recommend':     { loader: loadRecommendations },
  // Employer
  'emp-postings':  { loader: loadEmployerPostings },
  'emp-applicants':{ loader: loadEmployerApplicants },
};

function buildNavigation() {
  const topNav = document.getElementById('topbar-nav-links');
  const sideNav = document.getElementById('sidebar-nav-links');
  
  if (currentUser.role === 'student') {
    topNav.innerHTML = `
      <button class="nav-item" id="nav-feed" onclick="showPage('feed')"><span class="nav-icon">🏠</span>Home</button>
      <button class="nav-item" id="nav-internships" onclick="showPage('internships')"><span class="nav-icon">💼</span>Jobs</button>
      <button class="nav-item" id="nav-applications" onclick="showPage('applications')"><span class="nav-icon">📝</span>Applied</button>
      <button class="nav-item" id="nav-notifications" onclick="showPage('notifications')" style="position:relative">
         <span class="nav-icon">🔔</span>Alerts<span class="notification-badge" id="notif-badge" style="display:none">0</span>
      </button>
    `;
    sideNav.innerHTML = `
      <button class="sidebar-nav-item" id="snav-feed" onclick="showPage('feed')"><span class="sn-icon">🏠</span> Feed</button>
      <button class="sidebar-nav-item" id="snav-internships" onclick="showPage('internships')"><span class="sn-icon">💼</span> Internships</button>
      <button class="sidebar-nav-item" id="snav-applications" onclick="showPage('applications')"><span class="sn-icon">📝</span> My Applications</button>
      <button class="sidebar-nav-item" id="snav-skills" onclick="showPage('skills')"><span class="sn-icon">⚡</span> My Skills</button>
      <button class="sidebar-nav-item" id="snav-notifications" onclick="showPage('notifications')"><span class="sn-icon">🔔</span> Notifications</button>
      <button class="sidebar-nav-item" id="snav-recommend" onclick="showPage('recommend')"><span class="sn-icon">🎯</span> Recommendations</button>
    `;
    document.querySelectorAll('.student-only').forEach(e => e.style.display = 'block');
  } else {
    topNav.innerHTML = `
      <button class="nav-item" id="nav-emp-postings" onclick="showPage('emp-postings')"><span class="nav-icon">💼</span>My Postings</button>
      <button class="nav-item" id="nav-emp-applicants" onclick="showPage('emp-applicants')"><span class="nav-icon">📥</span>Applicants</button>
      <button class="nav-item" id="nav-feed" onclick="showPage('feed')"><span class="nav-icon">📊</span>Dashboard</button>
    `;
    sideNav.innerHTML = `
      <button class="sidebar-nav-item" id="snav-emp-postings" onclick="showPage('emp-postings')"><span class="sn-icon">💼</span> My Postings</button>
      <button class="sidebar-nav-item" id="snav-emp-applicants" onclick="showPage('emp-applicants')"><span class="sn-icon">📥</span> Applicants</button>
      <button class="sidebar-nav-item" id="snav-feed" onclick="showPage('feed')"><span class="sn-icon">📊</span> Global Dashboard</button>
    `;
    document.querySelectorAll('.student-only').forEach(e => e.style.display = 'none');
  }
}

function showPage(id) {
  currentPage = id;
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.sidebar-nav-item').forEach(b => b.classList.remove('active'));

  const pg = document.getElementById('page-' + id);
  if (pg) pg.classList.add('active');
  const nb = document.getElementById('nav-' + id);
  if (nb) nb.classList.add('active');
  const sb = document.getElementById('snav-' + id);
  if (sb) sb.classList.add('active');

  const cfg = pageConfig[id];
  if (cfg && cfg.loader) cfg.loader();
}

/* ══════════════════════════════════════════════
   Profile Sidebar
   ══════════════════════════════════════════════ */
function renderProfile() {
  if (!currentUser) return;
  const ini = getInitials(currentUser.name);
  document.getElementById('profile-initials').textContent = ini;
  document.getElementById('profile-name').textContent = currentUser.name;
  document.getElementById('topbar-initials').textContent = ini;
  document.getElementById('topbar-username').textContent = currentUser.name.split(' ')[0];

  const sub = currentUser.role === 'student' ? currentUser.department : currentUser.industry_type;
  document.getElementById('profile-sub').textContent = sub;

  if (currentUser.role === 'student') {
    document.getElementById('stat-label-1').textContent = 'Applications';
    document.getElementById('stat-label-2').textContent = 'Internships';
    
    // Resume UI
    document.getElementById('resume-container').style.display = 'block';
    const resumeInfo = document.getElementById('resume-info');
    if (currentUser.resume_path) {
      resumeInfo.innerHTML = `<a href="${currentUser.resume_path}" target="_blank" style="color:#0a66c2; font-weight:600">📄 View My Resume</a>`;
    } else {
      resumeInfo.textContent = 'No resume uploaded';
    }
  } else {
    document.getElementById('stat-label-1').textContent = 'Active Postings';
    document.getElementById('stat-label-2').textContent = 'Total Applicants';
    document.getElementById('resume-container').style.display = 'none';
  }
}

async function uploadResume(input) {
  const file = input.files[0];
  if (!file) return;
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    return toast('Only PDF files are allowed', 'error');
  }

  const formData = new FormData();
  formData.append('resume', file);

  toast('Uploading resume...', 'info');
  const res = await api('POST', '/api/students/resume', formData, true);
  
  if (res.success) {
    toast('Resume uploaded successfully!');
    currentUser.resume_path = res.data.resume_path;
    localStorage.setItem('sit_user', JSON.stringify(currentUser));
    renderProfile();
  } else {
    toast(res.error || 'Upload failed', 'error');
  }
  input.value = ''; // reset
}

/* ══════════════════════════════════════════════
   Dropdown
   ══════════════════════════════════════════════ */
function toggleDropdown() {
  document.getElementById('user-dropdown').classList.toggle('show');
}

function closeDropdown() {
  document.getElementById('user-dropdown').classList.remove('show');
}

document.addEventListener('click', function(e) {
  if (!e.target.closest('.topbar-dropdown')) closeDropdown();
});

function badgeStatus(s) {
  const map = {
    'Applied': 'badge-applied',
    'Interview Scheduled': 'badge-interview',
    'Selected': 'badge-selected',
    'Rejected': 'badge-rejected',
  };
  return `<span class="badge ${map[s] || ''}">${escapeHtml(s)}</span>`;
}

/* ══════════════════════════════════════════════
   FEED — Activity Feed (Shared Dashboard)
   ══════════════════════════════════════════════ */
async function loadFeed() {
  const el = document.getElementById('feed-content');
  el.innerHTML = '<div class="loading"><div class="spinner"></div><br>Loading feed...</div>';

  const results = await Promise.all([
    api('GET', '/api/internships'),
    api('GET', '/api/applications'),
    api('GET', '/api/applications/statistics'),
    api('GET', '/api/students'),
    api('GET', '/api/companies'),
  ]);

  const internships = results[0];
  const applications = results[1];
  const stats = results[2];
  const students = results[3];
  const companies = results[4];

  let html = '<div class="stats-row">';
  html += `<div class="stat-box"><div class="sv">${students.count || 0}</div><div class="sl">Students</div></div>`;
  html += `<div class="stat-box"><div class="sv">${companies.count || 0}</div><div class="sl">Companies</div></div>`;
  html += `<div class="stat-box"><div class="sv">${internships.count || 0}</div><div class="sl">Internships</div></div>`;
  html += `<div class="stat-box"><div class="sv">${applications.count || 0}</div><div class="sl">Applications</div></div></div>`;

  const statusData = (stats.data || []);
  if (statusData.length > 0) {
    html += '<div class="card" style="margin-bottom:8px">';
    html += '<div class="card-header"><h3>📊 Application Tracker</h3></div>';
    html += '<div class="card-body"><div style="display:flex;flex-wrap:wrap;gap:12px">';
    statusData.forEach(s => {
      html += `<div style="flex:1;min-width:120px;text-align:center;padding:12px;background:#fafafa;border-radius:8px">
        ${badgeStatus(s.status)}
        <div style="font-size:24px;font-weight:800;margin-top:6px;color:#0a66c2">${s.count}</div>
      </div>`;
    });
    html += '</div></div></div>';
  }

  const apps = (applications.data || []).slice(0, 8);
  if (apps.length > 0) {
    html += `<div class="card"><div class="card-header"><h3>📝 Recent Activity</h3></div><div class="card-body">
      <div class="table-wrap"><table><thead><tr><th>Student</th><th>Role</th><th>Company</th><th>Date</th><th>Status</th></tr></thead><tbody>`;
    apps.forEach(a => {
      html += `<tr>
        <td><strong>${escapeHtml(a.Student_Name)}</strong></td>
        <td>${escapeHtml(a.Role)}</td>
        <td>${escapeHtml(a.Company_Name)}</td>
        <td>${escapeHtml(a.Application_Date)}</td>
        <td>${badgeStatus(a.Application_Status)}</td>
      </tr>`;
    });
    html += '</tbody></table></div></div></div>';
  }

  if (!apps.length) {
    html += '<div class="empty">No recent activity.</div>';
  }

  el.innerHTML = html;

  if (currentUser.role === 'student') {
    document.getElementById('profile-stat-count-1').textContent = apps.length; // rough stat
    document.getElementById('profile-stat-count-2').textContent = internships.count || 0;
  }
}

/* ══════════════════════════════════════════════
   STUDENT VIEWS
   ══════════════════════════════════════════════ */
async function loadInternships() {
  const el = document.getElementById('internships-list');
  el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  const res = await api('GET', '/api/internships');
  const list = res.data || [];

  if (!list.length) {
    el.innerHTML = '<div class="empty">No internships posted yet.</div>';
    return;
  }

  let html = '';
  list.forEach(i => {
    const skills = (i.Required_Skills || '').split(',').map(s => s.trim()).filter(Boolean);
    html += `<div class="internship-card">
      <div class="ic-header">
        <div class="ic-logo">💼</div>
        <div style="flex:1">
          <div class="ic-title">${escapeHtml(i.Role)}</div>
          <div class="ic-company">${escapeHtml(i.Company_Name)}</div>
          <div class="ic-location">📍 ${escapeHtml(i.Location || '')}</div>
        </div>
        <button class="btn btn-primary btn-sm" onclick="applyToInternship(${i.Internship_ID}, '${escapeHtml(i.Role).replace(/'/g, "\\'")}')">Apply</button>
      </div>
      <div class="ic-details">
        <span class="ic-tag">⏱ ${escapeHtml(i.Duration)}</span>
        <span class="ic-tag green">₹${Number(i.Stipend).toLocaleString()}/mo</span>
        <span class="ic-tag orange">📅 Deadline: ${escapeHtml(i.Application_Deadline)}</span>
      </div>`;
    
    if (skills.length > 0) {
      html += '<div class="ic-skills">';
      skills.forEach(s => html += `<span class="skill-chip">${escapeHtml(s)}</span>`);
      html += '</div>';
    }
    html += '</div>';
  });
  el.innerHTML = html;
}

async function applyToInternship(internshipId, roleName) {
  const today = new Date().toISOString().split('T')[0];
  const res = await api('POST', '/api/applications', {
    internship_id: internshipId,
    application_date: today,
  });

  if (res.success) {
    toast(`Applied for ${roleName}!`);
    loadInternships();
  } else {
    toast(res.error || 'Application failed', 'error');
  }
}

async function loadMyApplications() {
  if (!currentUser) return;
  const el = document.getElementById('my-applications-content');
  el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  const res = await api('GET', '/api/applications/student/' + currentUser.user_id);
  const apps = res.data || [];

  if (!apps.length) {
    el.innerHTML = '<div class="empty">You haven\'t applied to any internships yet.</div>';
    return;
  }

  let html = `<div class="table-wrap"><table><thead><tr><th>Role</th><th>Company</th><th>Stipend</th><th>Date</th><th>Status</th></tr></thead><tbody>`;
  apps.forEach(a => {
    html += `<tr>
      <td><strong>${escapeHtml(a.Role)}</strong></td>
      <td>${escapeHtml(a.Company_Name)}</td>
      <td>₹${Number(a.Stipend || 0).toLocaleString()}</td>
      <td>${escapeHtml(a.Application_Date)}</td>
      <td>${badgeStatus(a.Application_Status)}</td>
    </tr>`;
  });
  html += '</tbody></table></div>';
  el.innerHTML = html;
}

async function loadMySkills() {
  if (!currentUser) return;
  const el = document.getElementById('skills-list');
  el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  const res = await api('GET', '/api/skills/student/' + currentUser.user_id);
  const skills = res.data || [];

  if (!skills.length) {
    el.innerHTML = '<div class="empty" style="margin-bottom:16px">No skills added yet.</div>';
    return;
  }

  let html = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px">';
  skills.forEach(s => {
    const color = s.Proficiency_Level === 'Advanced' ? '#057642' : s.Proficiency_Level === 'Intermediate' ? '#0a66c2' : '#666';
    html += `<span class="badge" style="background:${color}22;color:${color};padding:6px 14px;font-size:13px">
      ${escapeHtml(s.Skill_Name)} · ${escapeHtml(s.Proficiency_Level)}
    </span>`;
  });
  html += '</div>';
  el.innerHTML = html;
}

async function addMySkill() {
  const name = document.getElementById('new-skill-name').value.trim();
  const level = document.getElementById('new-skill-level').value;

  if (!name) return toast('Please enter a skill name', 'error');

  const res = await api('POST', '/api/skills', { skill_name: name, proficiency_level: level });

  if (res.success) {
    toast(`Skill "${name}" added!`);
    document.getElementById('new-skill-name').value = '';
    loadMySkills();
  } else {
    toast(res.error || 'Failed to add skill', 'error');
  }
}

async function loadMyNotifications() {
  if (!currentUser) return;
  const el = document.getElementById('notifications-list');
  el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  const res = await api('GET', '/api/notifications/student/' + currentUser.user_id);
  const notes = res.data || [];

  if (!notes.length) {
    el.innerHTML = '<div class="empty">No notifications yet.</div>';
    return;
  }

  let html = '';
  notes.forEach(n => {
    html += `<div style="padding:14px 0;border-bottom:1px solid #eee;display:flex;gap:12px;align-items:flex-start">
      <div style="width:40px;height:40px;border-radius:50%;background:#e8f0fe;display:flex;align-items:center;justify-content:center;font-size:18px">🔔</div>
      <div>
        <div style="font-size:14px;line-height:1.5">${escapeHtml(n.Message)}</div>
        <div style="font-size:12px;color:#666;margin-top:4px">${escapeHtml(n.Notification_Date || '')}</div>
      </div>
    </div>`;
  });
  el.innerHTML = html;
  const badge = document.getElementById('notif-badge');
  if (badge) badge.textContent = notes.length;
}

async function loadRecommendations() {
  if (!currentUser) return;
  const el = document.getElementById('recommend-content');
  el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  const res = await api('GET', '/api/internships/recommend/' + currentUser.user_id);
  const list = res.data || [];

  if (!list.length) {
    el.innerHTML = '<div class="empty">No matching internships found. Add skills to get recommendations.</div>';
    return;
  }

  let html = '';
  list.forEach(i => {
    html += `<div class="internship-card">
      <div class="ic-header">
        <div class="ic-logo">🎯</div>
        <div style="flex:1">
          <div class="ic-title">${escapeHtml(i.Role)}</div>
          <div class="ic-company">${escapeHtml(i.Company_Name)}</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:24px;font-weight:800;color:#0a66c2">${i.match_count}</div>
          <div style="font-size:11px;color:#666">skill matches</div>
        </div>
      </div>
      <div style="margin-top:12px">
        <button class="btn btn-primary btn-sm" onclick="applyToInternship(${i.Internship_ID}, '${escapeHtml(i.Role).replace(/'/g, "\\'")}')">Apply Now</button>
      </div>
    </div>`;
  });
  el.innerHTML = html;
}


/* ══════════════════════════════════════════════
   EMPLOYER VIEWS
   ══════════════════════════════════════════════ */
async function loadEmployerPostings() {
  if (currentUser.role !== 'company') return;
  const el = document.getElementById('emp-postings-list');
  el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  const res = await api('GET', '/api/internships/company/' + currentUser.user_id);
  const list = res.data || [];
  document.getElementById('profile-stat-count-1').textContent = list.length;

  if (!list.length) {
    el.innerHTML = '<div class="empty">You have no active internship postings.</div>';
    return;
  }

  let html = '';
  list.forEach(i => {
    html += `<div class="internship-card" style="border-left: 4px solid #0a66c2;">
      <div class="ic-header">
        <div style="flex:1">
          <div class="ic-title">${escapeHtml(i.Role)}</div>
          <div class="ic-location" style="margin-top:4px">⏱ ${escapeHtml(i.Duration)} | 📅 Deadline: ${escapeHtml(i.Application_Deadline)} | ₹${i.Stipend}</div>
        </div>
        <div>
           <button class="btn btn-sm" onclick="showPage('emp-applicants')">View Applicants</button>
        </div>
      </div>
    </div>`;
  });
  el.innerHTML = html;
}

function showCreateInternshipForm() {
  document.getElementById('create-internship-card').style.display = 'block';
  document.getElementById('ip-role').focus();
}

async function createInternship() {
  const role = document.getElementById('ip-role').value.trim();
  const dur = document.getElementById('ip-dur').value.trim();
  const stipend = parseFloat(document.getElementById('ip-stipend').value);
  const deadline = document.getElementById('ip-deadline').value;
  const skills = document.getElementById('ip-skills').value.trim();

  if (!role || !dur || isNaN(stipend) || !deadline) return toast('Please fill in required fields', 'error');

  const res = await api('POST', '/api/internships', {
    role, duration: dur, stipend, application_deadline: deadline, required_skills: skills
  });

  if (res.success) {
    toast('Internship posted successfully!');
    document.getElementById('create-internship-card').style.display = 'none';
    
    // Clear form
    document.getElementById('ip-role').value = '';
    document.getElementById('ip-dur').value = '';
    document.getElementById('ip-stipend').value = '';
    document.getElementById('ip-deadline').value = '';
    document.getElementById('ip-skills').value = '';

    loadEmployerPostings();
  } else {
    toast(res.error || 'Failed to post internship', 'error');
  }
}

async function loadEmployerApplicants() {
  if (currentUser.role !== 'company') return;
  const el = document.getElementById('emp-applicants-list');
  el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  // In a real app, an employer only views applicants for their internships.
  // Our current backend get_all_applications gets all, we will filter locally.
  const res = await api('GET', '/api/applications');
  let apps = res.data || [];
  
  apps = apps.filter(a => a.Company_Name === currentUser.name); // basic filter
  document.getElementById('profile-stat-count-2').textContent = apps.length;

  if (!apps.length) {
    el.innerHTML = '<div class="empty">No applications received yet.</div>';
    return;
  }

  let html = `<div class="table-wrap"><table><thead><tr><th>Applicant</th><th>Department</th><th>CGPA</th><th>Role Applied</th><th>Date</th><th>Status</th><th>Resume</th></tr></thead><tbody>`;
  apps.forEach(a => {
    // Determine resume link
    const resumeLink = a.Resume_Path ? `<a href="${a.Resume_Path}" target="_blank" class="btn btn-sm" style="background:#e8f0fe;color:#0a66c2;border:none">📄 View PDF</a>` : '<span style="color:#999;font-size:12px">Not uploaded</span>';

    html += `<tr>
      <td><strong>${escapeHtml(a.Student_Name)}</strong></td>
      <td>${escapeHtml(a.Student_Department || '')}</td>
      <td>${a.Student_CGPA || '-'}</td>
      <td>${escapeHtml(a.Role)}</td>
      <td>${escapeHtml(a.Application_Date)}</td>
      <td>
        <select onchange="updateApplicationStatus(${a.Application_ID}, this.value)" style="padding:4px; border-radius:4px; font-size:12px">
           <option value="Applied" ${a.Application_Status==='Applied'?'selected':''}>Applied</option>
           <option value="Interview Scheduled" ${a.Application_Status==='Interview Scheduled'?'selected':''}>Interview</option>
           <option value="Selected" ${a.Application_Status==='Selected'?'selected':''}>Selected</option>
           <option value="Rejected" ${a.Application_Status==='Rejected'?'selected':''}>Rejected</option>
        </select>
      </td>
      <td>${resumeLink}</td>
    </tr>`;
  });
  html += '</tbody></table></div>';
  el.innerHTML = html;
}

async function updateApplicationStatus(appId, newStatus) {
  const res = await api('PUT', `/api/applications/${appId}/status`, { status: newStatus });
  if (res.success) {
    toast(`Status updated to ${newStatus}`);
  } else {
    toast(res.error || 'Failed to update', 'error');
    // Refresh to revert
    loadEmployerApplicants();
  }
}

/* ══════════════════════════════════════════════
   Polling & SocketIO
   ══════════════════════════════════════════════ */
function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(() => {
    const cfg = pageConfig[currentPage];
    if (cfg && cfg.loader) cfg.loader();
  }, POLL_INTERVAL_MS);
}

function initSocketIO() {
  if (typeof io === 'undefined') return;
  try {
    const socket = io(API, { transports: ['websocket', 'polling'] });
    socket.on('connect', () => console.log('[RT] Connected to real-time server'));
    
    socket.on('application_created', data => {
      if (currentUser && currentUser.role === 'company') {
        toast(`New application received for ${escapeHtml(data.internship_id)}!`, 'info');
      } else {
        toast(`${escapeHtml(data.student_name)} applied for an internship!`, 'info');
      }
      if (currentPage === 'feed' || currentPage === 'emp-applicants') {
        const cfg = pageConfig[currentPage];
        if (cfg && cfg.loader) cfg.loader();
      }
    });

    socket.on('status_updated', data => {
      toast(`Application #${data.application_id} updated: ${escapeHtml(data.new_status)}`, 'info');
      if (['applications', 'feed', 'emp-applicants'].includes(currentPage)) {
        pageConfig[currentPage].loader();
      }
    });

    socket.on('internship_posted', data => {
      toast(`New internship: ${escapeHtml(data.role)}`, 'info');
      if (['internships', 'feed'].includes(currentPage)) {
        pageConfig[currentPage].loader();
      }
    });
  } catch (err) {
    console.log('[RT] SocketIO not available');
  }
}

/* ══════════════════════════════════════════════
   Init
   ══════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  if (loadAuth()) {
    showApp();
  } else {
    showAuthScreen();
  }
  initSocketIO();
});
