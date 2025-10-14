import json
from ChartOfAccounts import add_account, update_account, deactivate_account, list_accounts
from decimal import Decimal

class FakeResp:
    def __init__(self, data=None, count=None):
        self.data = data
        self.count = count

class FakeSB:
    def __init__(self):
        self.storage = {'chart_of_accounts': [], 'event_logs': []}
        self.next_id = 1
        self._table = None
        self._single = False
    def table(self, name):
        self._table = name
        return self
    def select(self, *args, **kwargs):
        return self
    def or_(self, *a, **k):
        return self
    def eq(self, *a, **k):
        return self
    def single(self):
        self._single = True
        return self
    def order(self, *a, **k):
        return self
    def range(self, *a, **k):
        return self
    def execute(self):
        if self._table == 'chart_of_accounts':
            data = self.storage['chart_of_accounts']
            if self._single:
                self._single = False
                return FakeResp(data=data[0] if data else None)
            return FakeResp(data=data)
        if self._table == 'event_logs':
            data = self.storage['event_logs']
            if self._single:
                self._single = False
                return FakeResp(data=data[0] if data else None)
            return FakeResp(data=data)
        return FakeResp()
    def insert(self, payload):
        if self._table == 'chart_of_accounts':
            entry = dict(payload)
            entry['AccountID'] = self.next_id
            self.next_id += 1
            self.storage['chart_of_accounts'].append(entry)
            return FakeResp(data=[entry])
        if self._table == 'event_logs':
            entry = dict(payload)
            entry['EventID'] = self.next_id
            self.next_id += 1
            self.storage['event_logs'].append(entry)
            return FakeResp(data=[entry])
        return FakeResp()
    def update(self, payload):
        # naive update: replace first matching
        if self._table == 'chart_of_accounts':
            if not self.storage['chart_of_accounts']:
                return FakeResp(data=None)
            self.storage['chart_of_accounts'][0].update(payload)
            return FakeResp(data=[self.storage['chart_of_accounts'][0]])
        return FakeResp()


def test_add_and_deactivate_account():
    sb = FakeSB()
    # add account
    payload = {
        'AccountName': 'Cash',
        'AccountNumber': '01',
        'InitialBalance': '0',
        'Debit': '0',
        'Credit': '0',
        'Balance': '0'
    }
    res = add_account(payload, sb=sb)
    assert res['success']
    acc_id = res['account_id']
    # try deactivate (balance 0 -> allowed)
    dres = deactivate_account(acc_id, sb=sb)
    assert dres['success']


def test_prevent_deactivate_with_balance():
    sb = FakeSB()
    payload = {
        'AccountName': 'AR',
        'AccountNumber': '02',
        'InitialBalance': '100.00',
        'Debit': '0',
        'Credit': '0',
        'Balance': '100.00'
    }
    res = add_account(payload, sb=sb)
    assert res['success']
    acc_id = res['account_id']
    dres = deactivate_account(acc_id, sb=sb)
    assert not dres['success']
