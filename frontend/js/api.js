function showError(message) {
  const box = document.getElementById("error");
  if (box) {
    box.textContent = message;
    box.style.display = "block";
  } else {
    alert(message);
  }
}

function clearError() {
  const box = document.getElementById("error");
  if (box) {
    box.textContent = "";
    box.style.display = "none";
  }
}

function errorText(data, status) {
  if (data && typeof data.detail === "string") return data.detail;
  if (data && Array.isArray(data.detail)) {
    const fields = data.detail.map(item => item.loc[item.loc.length - 1]);
    return "Dữ liệu không hợp lệ: " + fields.join(", ");
  }
  return "Có lỗi xảy ra (mã " + status + ")";
}

async function api(path, method = "GET", body = null) {
  clearError();
  const headers = {};
  const token = localStorage.getItem("token");
  if (token) headers["Authorization"] = "Bearer " + token;
  const options = { method: method, headers: headers };
  if (body instanceof FormData) {
    options.body = body;
  } else if (body !== null) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  let res;
  try {
    res = await fetch(API_BASE + path, options);
  } catch (e) {
    showError("Không kết nối được máy chủ");
    return null;
  }
  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }
  if (res.status === 401 && !location.pathname.endsWith("login.html")) {
    logout();
    return null;
  }
  if (!res.ok) {
    showError(errorText(data, res.status));
    return null;
  }
  return data;
}
