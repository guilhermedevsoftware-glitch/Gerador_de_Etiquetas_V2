document.addEventListener('DOMContentLoaded', function () {
    // Alterna a sidebar em telas pequenas
    const btnToggle = document.getElementById('btnToggleSidebar');
    const sidebar = document.getElementById('sidebar');
    if (btnToggle && sidebar) {
        btnToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }

    // Fecha alertas automaticamente após alguns segundos
    document.querySelectorAll('.alert').forEach(function (alerta) {
        setTimeout(function () {
            const instancia = bootstrap.Alert.getOrCreateInstance(alerta);
            if (instancia) {
                instancia.close();
            }
        }, 5000);
    });
});
