var sidebar_btn = document.querySelector('#sidebar-button');
var sidebar = document.querySelector('#sidebar');

sidebar_btn.addEventListener('click', (event) => {
    sidebar.show_sidebar();
});

console.log(sidebar);

sidebar.querySelector('[el="close"]').addEventListener('click', () => {
    sidebar.hide_sidebar();
});