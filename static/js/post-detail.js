(function () {
  var rows = document.querySelectorAll('.price-row');
  var btnText = document.getElementById('add-btn-text');
  var qtyInput = document.querySelector('input[name="qty"]');
  if (!rows.length) return;

  var selectedRow = null;

  function formatCurrency(v) {
    return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function updateBtn() {
    if (!btnText || !selectedRow) return;
    var price = parseFloat(selectedRow.dataset.priceAmount);
    var qty = Math.max(1, parseInt((qtyInput && qtyInput.value) || '1') || 1);
    btnText.textContent = 'Adicionar — R$ ' + formatCurrency(price * qty);
  }

  function select(row) {
    rows.forEach(function (r) {
      r.querySelector('.price-check').classList.add('hidden');
      r.style.outline = '';
      r.style.outlineOffset = '';
    });
    row.querySelector('.price-check').classList.remove('hidden');
    var color = row.dataset.color;
    row.style.outline = '2.5px solid ' + color;
    row.style.outlineOffset = '2px';
    selectedRow = row;
    updateBtn();
  }

  rows.forEach(function (row) {
    row.addEventListener('click', function () { select(row); });
  });

  var normal = Array.from(rows).find(function (r) { return r.dataset.label === 'Preço Normal'; });
  select(normal || rows[0]);

  document.querySelectorAll('.qty-dec').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (qtyInput) { qtyInput.value = Math.max(1, parseInt(qtyInput.value || '1') - 1); updateBtn(); }
    });
  });
  document.querySelectorAll('.qty-inc').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (qtyInput) { qtyInput.value = parseInt(qtyInput.value || '1') + 1; updateBtn(); }
    });
  });

  if (qtyInput) qtyInput.addEventListener('input', updateBtn);
})();
