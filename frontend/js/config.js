const API_BASE = "http://localhost:8000";
const API_BASE_URL = API_BASE;

function getToken() {
  return localStorage.getItem("token");
}

function authHeaders() {
  const token = getToken();
  return token ? { "Authorization": "Bearer " + token } : {};
}

