// --- SUBSISTEMA: Autenticación RBAC y Sesión DSN ---
async function loginOperator() {
    const email = document.getElementById("auth-email").value;
    const password = document.getElementById("auth-pass").value;
    try {
        let res = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        let data = await res.json();
        if (res.ok) {
            localStorage.setItem("odyssey_token", data.access_token);
            document.getElementById("login-form").style.display = "none";
            document.getElementById("auth-status").style.display = "block";
            document.getElementById("auth-role-text").innerText = `Rol: ${data.role} (${data.clearance})`;
            console.log("[AUTH] Operador autenticado correctamente.");
        } else {
            alert(data.detail || "Error de autenticación DSN.");
        }
    } catch (e) {
        console.error("Error de red en autenticación:", e);
    }
}

function logoutOperator() {
    localStorage.removeItem("odyssey_token");
    document.getElementById("login-form").style.display = "block";
    document.getElementById("auth-status").style.display = "none";
    document.getElementById("auth-email").value = "";
    document.getElementById("auth-pass").value = "";
    console.log("[AUTH] Sesión finalizada.");
}
