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

  // Vai trò người dùng badge
  const roleBadge = document.createElement("span");
  roleBadge.className = `badge ${role === "candidate" ? "badge-junior" : "badge-middle"}`;
  roleBadge.style.marginLeft = "auto";
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
