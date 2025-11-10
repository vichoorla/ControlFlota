// static/js/custom.js
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-coreui-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new coreui.Tooltip(tooltipTriggerEl);
    });
    
    // Sidebar toggle functionality
    const sidebar = document.querySelector('#sidebar');
    const sidebarInstance = new coreui.Sidebar(sidebar);
});