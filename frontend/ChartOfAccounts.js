(function(){
  let accountsCache = [];
  let currentSort = { field: 'AccountNumber', asc: true };

  let currentPage = 1;
  const perPage = 20;

  async function fetchAccounts(page = 1){
    currentPage = page;
    const q = document.getElementById('search').value || '';
    const res = await fetch(`/api/accounts?search=${encodeURIComponent(q)}&page=${page}&per_page=${perPage}`);
    const body = await res.json();
    const tbody = document.querySelector('#accountsTable tbody');
    tbody.innerHTML = '';
    if(body.success){
      accountsCache = body.accounts || [];
      renderAccounts();
      // update pagination UI
      const info = document.getElementById('paginationInfo');
      const prev = document.getElementById('prevPage');
      const next = document.getElementById('nextPage');
      const pagination = body.pagination || {};
      info.innerText = `Page ${pagination.current_page || currentPage} of ${pagination.total_pages || 1} — ${pagination.total_accounts || 0} accounts`;
      prev.disabled = !(pagination.has_prev);
      next.disabled = !(pagination.has_next);
    }
  }

  function renderAccounts(){
    const tbody = document.querySelector('#accountsTable tbody');
    tbody.innerHTML = '';
    const list = accountsCache.slice();
    list.sort((a,b)=>{
      const f = currentSort.field;
      const av = (a[f]||'').toString();
      const bv = (b[f]||'').toString();
      if(av === bv) return 0;
      return currentSort.asc ? (av>bv?1:-1) : (av>bv?-1:1);
    });
    list.forEach(a => {
      const tr = document.createElement('tr');
      const dateCreated = a.DateCreated ? new Date(a.DateCreated).toISOString().slice(0,10) : '';
      tr.innerHTML = `
        <td class="col-number"><a href="/ledger/${a.AccountNumber}">${a.AccountNumber}</a></td>
        <td class="col-name">${a.AccountName || ''}</td>
        <td class="col-type">${a.Category || ''}</td>
        <td class="col-term">${a.Term || ''}</td>
        <td class="col-balance">${a.BalanceFormatted || a.Balance || ''}</td>
        <td class="col-createdby">${a.CreatedBy || a.UserID || ''}</td>
        <td class="col-date">${dateCreated}</td>
        <td class="col-comments">${a.Comment || ''}</td>
        <td class="col-actions"><button data-id="${a.AccountID}" class="editBtn">Edit</button></td>
      `;
      tbody.appendChild(tr);
    });
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    document.getElementById('searchBtn').addEventListener('click', ()=>fetchAccounts(1));
    document.getElementById('newAccountBtn').addEventListener('click', ()=>{
      document.getElementById('accountModal').style.display = 'block';
    });

    document.getElementById('prevPage').addEventListener('click', ()=>{ if(currentPage>1) fetchAccounts(currentPage-1) });
    document.getElementById('nextPage').addEventListener('click', ()=>{ fetchAccounts(currentPage+1) });

    // header sorting
    document.querySelectorAll('#accountsTable thead th').forEach(th=>{
      th.style.cursor='pointer';
      th.addEventListener('click', ()=>{
        // find the first class that starts with 'col-'
        const cl = Array.from(th.classList).find(c=>c.startsWith('col-')) || '';
        const key = cl.replace('col-','') || 'number';
        // map class to field names
        const map = { number: 'AccountNumber', name: 'AccountName', type: 'Category', term:'Term', balance:'Balance', createdby:'CreatedBy', date:'DateCreated' };
        const field = map[key] || 'AccountNumber';
        if(currentSort.field===field) currentSort.asc=!currentSort.asc; else { currentSort.field=field; currentSort.asc=true }
        renderAccounts();
      });
    });
      // calendar widget
      const cal = document.createElement('div');
      cal.className = 'calendar-widget';
      cal.innerText = new Date().toLocaleDateString();
      document.body.appendChild(cal);
      // help button
      const helpBtn = document.createElement('button');
      helpBtn.className = 'help-btn';
      helpBtn.innerText = 'Help';
      helpBtn.addEventListener('click', ()=>{
        let m = document.querySelector('.help-modal');
        if(!m){
          m = document.createElement('div'); m.className='help-modal';
          m.innerHTML = '<h2>Help - Chart of Accounts</h2><p>Use this page to add, edit, search and deactivate accounts. Admins can create and modify accounts. Click an account number to view its ledger.</p><button id="closeHelp">Close</button>';
          document.body.appendChild(m);
          m.querySelector('#closeHelp').addEventListener('click', ()=>m.style.display='none');
        }
        m.style.display = 'block';
      });
      document.body.appendChild(helpBtn);
    document.getElementById('cancelModal').addEventListener('click', ()=>{
      document.getElementById('accountModal').style.display = 'none';
    });
    document.getElementById('accountForm').addEventListener('submit', async (e)=>{
      e.preventDefault();
      const form = e.target;
      const data = {};
      new FormData(form).forEach((v,k)=>data[k]=v);
      const res = await fetch('/api/accounts', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data)});
  const body = await res.json();
  console.log('create account response', body);
  alert(body.message || (body.success? 'Account created':'Error'));
      if(body.success){
        document.getElementById('accountModal').style.display = 'none';
        fetchAccounts();
      }
    });

    fetchAccounts();
  });
})();