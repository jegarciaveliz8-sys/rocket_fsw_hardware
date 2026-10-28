function setAiPrompt(text) {
    document.getElementById("ai-prompt").value = text;
}

async function queryAI() {
    const prompt = document.getElementById("ai-prompt").value || "Estado general de la misión";
    document.getElementById("ai-response").innerText = "Gemini AI analizando telemetría en tiempo real...";
    try {
        const res = await fetch("/ai/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt })
        });
        const data = await res.json();
        document.getElementById("ai-response").innerText = data.response || data.error;
    } catch (e) {
        document.getElementById("ai-response").innerText = "Error de enlace con el Copiloto de IA.";
    }
}
