document.addEventListener('click', function(e) {
    if (!e.target.matches('.toggle')) return;
    const childList = e.target.parentElement.querySelector('ul');
    if (!childList) return;
    childList.classList.toggle('d-none');
    e.target.textContent = childList.classList.contains('d-none') ? '[+]' : '[-]';
});
