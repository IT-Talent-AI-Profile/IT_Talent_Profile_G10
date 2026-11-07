const MENUS = {
  candidate: [
    { href: "profile.html", label: "Hồ sơ cá nhân" },
    { href: "cv-upload.html", label: "Tải lên CV" },
    { href: "evaluation.html", label: "Đánh giá năng lực" }
  ],
  recruiter: [
    { href: "jobs.html", label: "Tin tuyển dụng" },
    { href: "candidates.html", label: "Tìm kiếm ứng viên" }
  ]
};
let skillList = null;

function esc(text) {
  return String(text ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  location.href = "login.html";
}

function showMenu(role) {
  // Tránh tạo nhiều navbar nếu đã có
  const existingNav = document.querySelector("nav.navbar");
  if (existingNav) existingNav.remove();

  const nav = document.createElement("nav");
  nav.className = "navbar";

  // Logo thương hiệu
  const brand = document.createElement("a");
  brand.className = "nav-brand";
  brand.href = role === "candidate" ? "profile.html" : "jobs.html";
  brand.innerHTML = `<span class="logo-icon">⚡</span><span>IT Talent AI</span>`;
  nav.appendChild(brand);

  // Menu items
  if (MENUS[role]) {
    MENUS[role].forEach(item => {
      const link = document.createElement("a");
      link.href = item.href;
      link.textContent = item.label;
      if (location.pathname.endsWith(item.href)) link.className = "active";
      nav.appendChild(link);
    });
  }

  // Chuông thông báo dành riêng cho Ứng viên & Nhà tuyển dụng
  const notifyBtn = document.createElement("button");
  notifyBtn.type = "button";
  notifyBtn.className = "nav-notify-btn";
  notifyBtn.style.marginLeft = "auto";
  notifyBtn.style.marginRight = "10px";
  notifyBtn.title = "Thông báo & Lời mời ứng tuyển";
  notifyBtn.innerHTML = `
    <span>🔔</span>
    <span class="nav-notify-badge" id="navNotifyBadge">1</span>
  `;

  // Dropdown thông báo 3D
  const dropdown = document.createElement("div");
  dropdown.className = "nav-notify-dropdown";
  dropdown.id = "navNotifyDropdown";
  dropdown.innerHTML = `
    <div class="notify-header">
      <h4>📬 Hộp Thư & Lời Mời Ứng Tuyển</h4>
      <span style="font-size: 11px; color: #6366f1; font-weight: 700; cursor: pointer;" onclick="markAllNotificationsRead()">Đánh dấu đã đọc</span>
    </div>
    <div id="notifyListContainer">
      <div class="notify-item unread" onclick="location.href='profile.html#invitationsSection'">
        <div class="notify-item-icon">🏢</div>
        <div>
          <div style="font-weight: 700; font-size: 13px; color: #0f172a;">Lời mời phỏng vấn từ TechCorp Vietnam</div>
          <div style="font-size: 12px; color: #475569; margin-top: 2px;">Vị trí: <strong>Senior Python Backend Engineer</strong> (Khớp 96%)</div>
          <div style="font-size: 11px; color: #16a34a; font-weight: 700; margin-top: 4px;">10 phút trước • Cần phản hồi</div>
        </div>
      </div>
      <div class="notify-item" onclick="location.href='profile.html'">
        <div class="notify-item-icon">✨</div>
        <div>
          <div style="font-weight: 700; font-size: 13px; color: #0f172a;">AI đã hoàn tất đánh giá hồ sơ</div>
          <div style="font-size: 12px; color: #475569; margin-top: 2px;">Điểm năng lực của bạn đạt mức xếp hạng Senior (85.0/100).</div>
          <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Hôm nay</div>
        </div>
      </div>
    </div>
  `;

  notifyBtn.onclick = (e) => {
    e.stopPropagation();
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
  };

  document.addEventListener("click", () => {
    dropdown.style.display = "none";
  });
  dropdown.onclick = (e) => e.stopPropagation();

  nav.appendChild(notifyBtn);
  nav.appendChild(dropdown);

  // Vai trò người dùng badge
  const roleBadge = document.createElement("span");
  roleBadge.className = `badge ${role === "candidate" ? "badge-junior" : "badge-middle"}`;
  roleBadge.style.marginRight = "12px";
  roleBadge.textContent = role === "candidate" ? "Ứng viên" : "Nhà tuyển dụng";
  nav.appendChild(roleBadge);

  // Nút đăng xuất
  const button = document.createElement("button");
  button.className = "logout";
  button.textContent = "Đăng xuất";
  button.onclick = logout;
  nav.appendChild(button);

  document.body.prepend(nav);
}

function guard(role) {
  const token = localStorage.getItem("token");
  const current = localStorage.getItem("role");
  if (!token || current !== role) {
    location.href = "login.html";
    return false;
  }
  showMenu(current);
  return true;
}

async function skillOptions(select) {
  if (typeof select === "string") select = document.getElementById(select);
  if (!select) return [];
  if (skillList === null) skillList = await api("/skills");
  if (skillList === null) return [];
  select.innerHTML = "";
  if (!select.multiple) {
    const first = document.createElement("option");
    first.value = "";
    first.textContent = "-- Chọn kỹ năng --";
    select.appendChild(first);
  }
  let group = null;
  let box = select;
  skillList.forEach(skill => {
    if (skill.group !== group) {
      group = skill.group;
      box = document.createElement("optgroup");
      box.label = group;
      select.appendChild(box);
    }
    const option = document.createElement("option");
    option.value = skill.id;
    option.textContent = skill.name;
    box.appendChild(option);
  });
  return skillList;
}

function markAllNotificationsRead() {
  const badge = document.getElementById("navNotifyBadge");
  if (badge) badge.style.display = "none";
  document.querySelectorAll(".notify-item.unread").forEach(el => el.classList.remove("unread"));
}
