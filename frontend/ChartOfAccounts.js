(function(){
  async function fetchAccounts(){
    const q = document.getElementById('search').value || '';
    const res = await fetch(`/api/accounts?search=${encodeURIComponent(q)}`);
    const body = await res.json();
    const tbody = document.querySelector('#accountsTable tbody');
    tbody.innerHTML = '';
    if(body.success){
      body.accounts.forEach(a => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><a href="/ledger/${a.AccountNumber}">${a.AccountNumber}</a></td>
          <td>${a.AccountName}</td>
          <td>${a.Category||''}</td>
          <td>${a.Subcategory||''}</td>
            <td style="text-align:right">${a.BalanceFormatted || a.Balance || ''}</td>
          <td><button data-id="${a.AccountID}" class="editBtn">Edit</button></td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    document.getElementById('searchBtn').addEventListener('click', fetchAccounts);
    document.getElementById('newAccountBtn').addEventListener('click', ()=>{
      document.getElementById('accountModal').style.display = 'block';
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
      alert(body.message || (body.success? 'Account created':'Error'));
      if(body.success){
        document.getElementById('accountModal').style.display = 'none';
        fetchAccounts();
      }
    });

    fetchAccounts();
  });
})();