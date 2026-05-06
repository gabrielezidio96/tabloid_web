function formatCurrency(v) {
  return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function updateBtn() {
  var row = document.querySelector('.price-row[data-selected]');
  var label = document.getElementById('btn-label');
  if (!label) return;
  if (!row) { label.textContent = 'Adicionar a Lista'; return; }
  var price = parseFloat(row.dataset.priceAmount);
  var qty = Math.max(1, parseInt(document.getElementById('qty-input').value) || 1);
  label.textContent = 'Adicionar • R$ ' + formatCurrency(price * qty);
}

function selectPrice(el) {
  document.querySelectorAll('.price-row').forEach(function (r) {
    delete r.dataset.selected;
    r.style.outline = '';
  });
  el.dataset.selected = '1';
  el.style.outline = '2px solid #f97316';
  document.getElementById('selected-price-key').value = el.dataset.priceKey;
  updateBtn();
}

(function () {
  var rows = document.querySelectorAll('.price-row');

  rows.forEach(function (row) {
    row.addEventListener('click', function () { selectPrice(row); });
  });

  var qtyInput = document.getElementById('qty-input');
  if (qtyInput) {
    qtyInput.addEventListener('input', updateBtn);
  }

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

  var best = Array.from(rows).find(function (r) { return r.dataset.isBest === 'true'; }) || rows[0];
  if (best) selectPrice(best);
})();
