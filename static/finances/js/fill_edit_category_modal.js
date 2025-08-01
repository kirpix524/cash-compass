document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.edit-category-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const editUrl = btn.dataset.editUrl;
      const guid = btn.dataset.guid;
      const name = btn.dataset.name;
      const parent = btn.dataset.parent || '';
      const type = btn.dataset.type;
      const form = document.getElementById('categoryEditForm');

      form.action = editUrl;

      document.getElementById('modalCategoryName').value = name;
      const parentSelect = document.getElementById('modalCategoryParent');

      Array.from(parentSelect.options).forEach(opt => {
        if (!opt.value) {
          opt.hidden = false;
        } else {
          opt.hidden = opt.dataset.type !== type;
        }
      });

      parentSelect.value = parent;
      new bootstrap.Modal(document.getElementById('categoryModal')).show();
    });
  });
});