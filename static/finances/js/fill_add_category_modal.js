document.querySelectorAll('#addExpenseCategoryBtn, #addIncomeCategoryBtn').forEach(btn => {
  btn.addEventListener('click', () => {
    const type = btn.id === 'addExpenseCategoryBtn' ? 'EXPENSE' : 'INCOME';
    document.getElementById('modalAddCategoryType').value = type;

    const nameInput = document.getElementById('modalAddCategoryName');
    const parentSelect = document.getElementById('modalAddCategoryParent');

    nameInput.value = '';
    Array.from(parentSelect.options).forEach(opt => {
      if (!opt.value) {
        opt.hidden = false;
      } else {
        opt.hidden = opt.dataset.type !== type;
      }
    });
    parentSelect.value = '';

    const modal = new bootstrap.Modal(document.getElementById('addCategoryModal'));
    modal.show();
  });
});