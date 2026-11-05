const MENUS = {
  candidate: [
    { href: "profile.html", label: "Hồ sơ" },
    { href: "upload_cv.html", label: "Tải CV" },
    { href: "evaluation.html", label: "Đánh giá" }
  ],
  recruiter: [
    { href: "jobs.html", label: "Tin tuyển dụng" },
    { href: "candidates.html", label: "Tìm ứng viên" }
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
  const nav = document.createElement("nav");
  nav.className = "navbar";
  MENUS[role].forEach(item => {
    const link = document.createElement("a");
    link.href = item.href;
    link.textContent = item.label;
    if (location.pathname.endsWith(item.href)) link.className = "active";
    nav.appendChild(link);
  });
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
