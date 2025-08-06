document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('addWalletGroupBtn');
  if (!btn) return console.error('Кнопка addWalletGroupBtn не найдена');
  btn.addEventListener('click', () => {
    const url = btn.dataset.createUrl;
    const form = document.getElementById('walletGroupForm');
    if (!form) return console.error('Форма walletGroupForm не найдена');
    form.action = url;
    form.querySelector('input[name="name"]').value = '';
    new bootstrap.Modal(document.getElementById('addWalletGroupModal')).show();
  });
});