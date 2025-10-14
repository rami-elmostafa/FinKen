(function(){
  let accountsCache = [];
  let currentSort = { field: 'accountnumber', asc: true };

  let currentPage = 1;
  const perPage = 20;

  async function fetchAccounts(page = 1){
    currentPage = page;
    const q = document.getElementById('search-input').value || '';
    const res = await fetch(`/api/accounts?search=${encodeURIComponent(q)}&page=${page}&per_page=${perPage}`);
    const body = await res.json();
    const tbody = document.getElementById('accounts-table-body');
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
    const tbody = document.getElementById('accounts-table-body');
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
      const dateCreated = a.datecreated ? new Date(a.datecreated).toISOString().slice(0,10) : '';
      const statusBadge = a.isactive === false ? '<span style="color:#ff4444;font-weight:bold;"> (Inactive)</span>' : '';
      tr.innerHTML = `
        <td><a href="/ledger/${a.accountnumber}">${a.accountnumber}</a></td>
        <td>${a.accountname || ''}${statusBadge}</td>
        <td>${a.category || ''}</td>
        <td>${a.normalside || ''}</td>
        <td>${a.initialbalance_formatted || a.initialbalance || ''}</td>
        <td>${a.createdby_username || ''}</td>
        <td>${dateCreated}</td>
        <td>${a.comment || ''}</td>
        <td>
          <button data-id="${a.accountid}" class="editBtn">Edit</button>
          ${a.isactive !== false ? `<button data-id="${a.accountid}" class="deactivateBtn" style="background-color:#ff4444;margin-left:4px;">Deactivate</button>` : ''}
        </td>
      `;
      tbody.appendChild(tr);
    });

    // Attach event listeners for edit buttons
    document.querySelectorAll('.editBtn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const accountId = e.target.getAttribute('data-id');
        await openEditModal(accountId);
      });
    });

    // Attach event listeners for deactivate buttons
    document.querySelectorAll('.deactivateBtn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const accountId = e.target.getAttribute('data-id');
        await deactivateAccount(accountId);
      });
    });
  }

  async function openEditModal(accountId) {
    try {
      const res = await fetch(`/api/accounts/${accountId}`);
      const body = await res.json();
      if (!body.success) {
        alert(body.message || 'Failed to load account');
        return;
      }
      
      const account = body.account;
      const form = document.getElementById('accountForm');
      const modal = document.getElementById('accountModal');
      
      // Change modal title
      document.getElementById('modalTitle').innerText = 'Edit Account';
      
      // Populate form fields with null checks
      const setFieldValue = (name, value) => {
        const field = form.querySelector(`[name="${name}"]`);
        if (field) {
          field.value = value || '';
        }
      };
      
      setFieldValue('AccountNumber', account.accountnumber);
      setFieldValue('AccountName', account.accountname);
      setFieldValue('Description', account.accountdescription);
      setFieldValue('NormalSide', account.normalside || 'Debit');
      setFieldValue('Category', account.category);
      setFieldValue('Subcategory', account.subcategory);
      setFieldValue('InitialBalance', account.initialbalance || '0.00');
      setFieldValue('Debit', account.debit || '0.00');
      setFieldValue('Credit', account.credit || '0.00');
      setFieldValue('Balance', account.balance || '0.00');
      setFieldValue('Statement', account.statementtype || 'BS');
      setFieldValue('Order', account.displayorder);
      setFieldValue('Comment', account.comment);
      
      // Store account ID for update
      form.setAttribute('data-account-id', accountId);
      
      modal.style.display = 'block';
    } catch (err) {
      alert('Error loading account: ' + err.message);
      console.error('Error in openEditModal:', err);
    }
  }

  async function deactivateAccount(accountId) {
    if (!confirm('Are you sure you want to deactivate this account? Accounts with positive balances cannot be deactivated.')) {
      return;
    }
    
    try {
      const res = await fetch(`/api/accounts/${accountId}/deactivate`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
      });
      const body = await res.json();
      alert(body.message || (body.success ? 'Account deactivated successfully' : 'Failed to deactivate account'));
      if (body.success) {
        fetchAccounts(currentPage);
      }
    } catch (err) {
      alert('Error deactivating account: ' + err.message);
    }
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    document.getElementById('search-btn').addEventListener('click', ()=>fetchAccounts(1));
    document.getElementById('new-account-btn').addEventListener('click', ()=>{
      // Reset form for new account
      const form = document.getElementById('accountForm');
      form.reset();
      form.removeAttribute('data-account-id');
      document.getElementById('modalTitle').innerText = 'Add Account';
      document.getElementById('accountModal').style.display = 'block';
    });

    document.getElementById('prev-page').addEventListener('click', ()=>{ if(currentPage>1) fetchAccounts(currentPage-1) });
    document.getElementById('next-page').addEventListener('click', ()=>{ fetchAccounts(currentPage+1) });

    // header sorting
    document.querySelectorAll('#accounts-table thead th').forEach(th=>{
      th.style.cursor='pointer';
      th.addEventListener('click', ()=>{
        // find the first class that starts with 'col-'
        const cl = Array.from(th.classList).find(c=>c.startsWith('col-')) || '';
        const key = cl.replace('col-','') || 'number';
        // map class to field names (lowercase to match database)
        const map = { number: 'accountnumber', name: 'accountname', type: 'category', term:'normalside', balance:'initialbalance', createdby:'createdby_username', date:'datecreated' };
        const field = map[key] || 'accountnumber';
        if(currentSort.field===field) currentSort.asc=!currentSort.asc; else { currentSort.field=field; currentSort.asc=true }
        renderAccounts();
      });
    });
      // Top-left container for widgets
      const topLeftContainer = document.createElement('div');
      topLeftContainer.className = 'top-left-container';

      // calendar widget
      const cal = document.createElement('div');
      cal.className = 'calendar-widget';
      cal.innerText = new Date().toLocaleDateString();
      topLeftContainer.appendChild(cal);

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
      topLeftContainer.appendChild(helpBtn);

      document.body.appendChild(topLeftContainer);

    document.getElementById('cancelModal').addEventListener('click', ()=>{
      document.getElementById('accountModal').style.display = 'none';
    });
    document.getElementById('accountForm').addEventListener('submit', async (e)=>{
      e.preventDefault();
      const form = e.target;
      const data = {};
      new FormData(form).forEach((v,k)=>data[k]=v);
      
      // Filter out fields that don't exist in the database table
      // Debit, Credit, and Balance are UI-only fields for display purposes
      const fieldsToExclude = ['Debit', 'Credit', 'Balance'];
      fieldsToExclude.forEach(field => delete data[field]);
      
      const accountId = form.getAttribute('data-account-id');
      const isEdit = !!accountId;
      
      const url = isEdit ? `/api/accounts/${accountId}` : '/api/accounts';
      const method = isEdit ? 'PUT' : 'POST';
      
      const res = await fetch(url, {
        method: method, 
        headers:{'Content-Type':'application/json'}, 
        body: JSON.stringify(data)
      });
      const body = await res.json();
      console.log(isEdit ? 'update account response' : 'create account response', body);
      alert(body.message || (body.success? (isEdit ? 'Account updated' : 'Account created'):'Error'));
      if(body.success){
        document.getElementById('accountModal').style.display = 'none';
        fetchAccounts(currentPage);
      }
    });

    fetchAccounts();
  });
})();