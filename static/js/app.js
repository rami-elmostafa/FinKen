document.addEventListener('DOMContentLoaded', () => {
  const balanceEl = document.getElementById('balance-amount')
  const tbody = document.querySelector('#tx-table tbody')
  const form = document.getElementById('tx-form')

  async function load() {
    const res = await fetch('/api/transactions')
    const txs = await res.json()
    render(txs)
  }

  function render(txs) {
    tbody.innerHTML = ''
    let balance = 0
    txs.forEach(t => {
      balance += Number(t.amount)
      const tr = document.createElement('tr')
      tr.innerHTML = `<td>${t.date}</td><td>${escapeHtml(t.description)}</td><td>${Number(t.amount).toFixed(2)}</td>`
      tbody.appendChild(tr)
    })
    balanceEl.textContent = balance.toFixed(2)
  }

  function escapeHtml(s){
    return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    const payload = {
      date: document.getElementById('date').value,
      description: document.getElementById('description').value,
      amount: document.getElementById('amount').value,
    }
    const res = await fetch('/api/transactions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (res.ok) {
      document.getElementById('description').value = ''
      document.getElementById('amount').value = ''
      await load()
    } else {
      const err = await res.json()
      alert(err.error || 'Failed')
    }
  })

  load()
})
