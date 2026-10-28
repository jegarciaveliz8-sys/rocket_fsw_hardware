(function() {
    // 1. Tarjeta de FDIR Autónomo y Hot-Swap de OBC
    const fdirCard = document.createElement('div');
    fdirCard.className = 'card';
    fdirCard.style.border = '1px solid #e11d48';
    fdirCard.innerHTML = `
        <h3>🚨 FDIR Autónomo & Hot-Swap de Bancos OBC (Fault Isolation)</h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fb7185;">Estado Banco OBC</span><br><strong style="color: #34d399;">BANK-A (ACTIVE)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fb7185;">Umbral de Sobrecalentamiento</span><br><strong style="color: #38bdf8;">NOMINAL (&lt; 65°C)</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fb7185;">Acción FDIR Autónoma</span><br><strong style="color: #34d399;">ZERO-INTERVENTION</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #fb7185;">Watchdog Timer (WDT)</span><br><strong style="color: #34d399;">ARMED (1000ms)</strong>
            </div>
        </div>
    `;

    // 2. Tarjeta de Bitácora Criptográfica Inmutable (Caja Negra Blockchain)
    const blockchainCard = document.createElement('div');
    blockchainCard.className = 'card';
    blockchainCard.style.border = '1px solid #3b82f6';
    blockchainCard.innerHTML = `
        <h3>🔗 Caja Negra Criptográfica (Immutable SHA-256 Flight Ledger)</h3>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; text-align: center; margin-top: 8px;">
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #60a5fa;">Bloque Actual Registrado</span><br><strong id="bc-block" style="color: #38bdf8;">#004812 - MINTED</strong>
            </div>
            <div style="background: #020617; padding: 6px; border-radius: 4px;">
                <span style="font-size: 10px; color: #60a5fa;">Hash de Enlace (SHA-256)</span><br><strong id="bc-hash" style="color: #34d399;">e3b0c442...9f81</strong>
            </div>
        </div>
    `;

    const container = document.body.querySelector('.container');
    if (container) {
        container.appendChild(fdirCard);
        container.appendChild(blockchainCard);
    }
})();
