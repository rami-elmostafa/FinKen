from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
import json
import re
from SupabaseClient import _sb, get_current_user

ACCOUNT_NUMBER_RE = re.compile(r'^\d+$')  # only digits, leading zeros allowed

def _format_money(value: Decimal) -> str:
    return f"{value:,.2f}"

def _parse_money(value) -> Decimal:
    if value is None or value == '':
        return Decimal('0.00')
    if isinstance(value, Decimal):
        return value.quantize(Decimal('0.01'))
    # strip commas and whitespace
    s = str(value).replace(',', '').strip()
    try:
        d = Decimal(s)
    except InvalidOperation:
        raise ValueError('Invalid monetary value')
    return d.quantize(Decimal('0.01'))

def _log_event(sb, tablename, recordid, actiontype, before, after):
    try:
        # event_logs schema (DBSchema.sql) expects: userid, timestamp, actiontype, tablename, recordid, beforevalue, aftervalue
        payload = {
            'userid': get_current_user(),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'actiontype': actiontype,
            'tablename': tablename,
            'recordid': int(recordid) if recordid is not None else None,
            'beforevalue': json.dumps(before) if before is not None else None,
            'aftervalue': json.dumps(after) if after is not None else None
        }
        sb.table('event_logs').insert(payload).execute()
    except Exception:
        # best-effort logging; do not fail primary operation
        pass


def _category_prefix_rules():
    """Return a mapping of category -> required starting prefix for account numbers.
    If a category is present in this map, newly created account numbers must start with the prefix.
    These are simple defaults; update if you have a different scheme.
    """
    return {
        'Asset': '01',
        'Liability': '02',
        'Equity': '03',
        'Revenue': '04',
        'Expense': '05'
    }

def add_account(account: dict, sb=None):
    """Create a new account. account is a dict with required keys described in UI."""
    try:
        sb = sb or _sb()

        # Validate required fields
        name = (account.get('AccountName') or '').strip()
        number = (account.get('AccountNumber') or '').strip()
        if not name:
            return {'success': False, 'message': 'Account name is required'}
        if not number:
            return {'success': False, 'message': 'Account number is required'}
        if not ACCOUNT_NUMBER_RE.match(number):
            return {'success': False, 'message': 'Account number must be digits only'}

        # Check duplicates (number & name)
        resp = sb.table('chart_of_accounts').select('*').or_(
            f"accountnumber.eq.{number},accountname.eq.{name}"
        ).execute()
        if resp.data:
            return {'success': False, 'message': 'Duplicate account number or name not allowed'}

        # Enforce category-based starting prefix if provided
        category = account.get('Category')
        if category:
            rules = _category_prefix_rules()
            required = rules.get(category)
            if required and not number.startswith(required):
                return {'success': False, 'message': f'Account number for category {category} must start with {required}'}

        # Parse monetary fields
        initial = _parse_money(account.get('InitialBalance', 0))

        row = {
            'accountname': name,
            'accountnumber': number,
            'accountdescription': account.get('Description'),
            'normalside': account.get('NormalSide') or 'Debit',  # Default to Debit if not provided
            'category': account.get('Category'),
            'subcategory': account.get('Subcategory'),
            'initialbalance': str(initial),
            'displayorder': account.get('Order'),
            'statementtype': account.get('Statement'),
            'isactive': True,
            'datecreated': datetime.now(timezone.utc).isoformat(),
            'createdbyuserid': account.get('UserID'),
            'comment': account.get('Comment')
        }

        insert_resp = sb.table('chart_of_accounts').insert(row).execute()
        if not insert_resp.data:
            return {'success': False, 'message': 'Failed to create account'}

        created = insert_resp.data[0] if isinstance(insert_resp.data, list) else insert_resp.data
        account_id = created.get('accountid') or created.get('id')

        # log event
        _log_event(sb, 'chart_of_accounts', account_id, 'INSERT', None, row)

        # return formatted data
        row['InitialBalanceFormatted'] = _format_money(initial)

        return {'success': True, 'account': row, 'account_id': account_id}

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        # return error with traceback for debugging (developer only)
        return {'success': False, 'message': str(e), 'traceback': tb}

def get_account_by_id(account_id, sb=None):
    try:
        sb = sb or _sb()
        resp = sb.table('chart_of_accounts').select('*').eq('accountid', account_id).single().execute()
        if not resp.data:
            return {'success': False, 'message': 'Account not found'}
        a = resp.data
        # format money fields if present
        for k in ['initialbalance']:
            if a.get(k) is not None:
                try:
                    a[k+'_formatted'] = _format_money(_parse_money(a.get(k)))
                except Exception:
                    a[k+'_formatted'] = a.get(k)
        return {'success': True, 'account': a}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def update_account(account_id, changes: dict, sb=None):
    try:
        sb = sb or _sb()
        # fetch existing
        before_resp = sb.table('chart_of_accounts').select('*').eq('accountid', account_id).single().execute()
        if not before_resp.data:
            return {'success': False, 'message': 'Account not found'}
        before = dict(before_resp.data)

        # Convert any PascalCase keys to lowercase for database compatibility
        normalized_changes = {}
        key_mapping = {
            'AccountNumber': 'accountnumber',
            'AccountName': 'accountname',
            'Description': 'accountdescription',
            'NormalSide': 'normalside',
            'Category': 'category',
            'Subcategory': 'subcategory',
            'InitialBalance': 'initialbalance',
            'Order': 'displayorder',
            'Statement': 'statementtype',
            'Comment': 'comment',
            'IsActive': 'isactive'
        }
        
        for key, value in changes.items():
            normalized_key = key_mapping.get(key, key.lower())
            normalized_changes[normalized_key] = value

        # apply validations
        if 'accountnumber' in normalized_changes:
            number = str(normalized_changes['accountnumber']).strip()
            if not ACCOUNT_NUMBER_RE.match(number):
                return {'success': False, 'message': 'Account number must be digits only'}
            # check duplicates
            dup = sb.table('chart_of_accounts').select('*').or_(
                f"accountnumber.eq.{number},accountname.eq.{normalized_changes.get('accountname', before.get('accountname'))}"
            ).execute()
            if dup.data and any(d.get('accountid') != account_id for d in (dup.data if isinstance(dup.data, list) else [dup.data])):
                return {'success': False, 'message': 'Duplicate account number or name not allowed'}

        # parse monetary fields
        for money_field in ('initialbalance',):
            if money_field in normalized_changes:
                try:
                    normalized_changes[money_field] = str(_parse_money(normalized_changes[money_field]))
                except Exception as e:
                    return {'success': False, 'message': str(e)}

        # perform update
        update_resp = sb.table('chart_of_accounts').update(normalized_changes).eq('accountid', account_id).execute()
        if not update_resp.data:
            return {'success': False, 'message': 'Update failed'}

        after = update_resp.data[0] if isinstance(update_resp.data, list) else update_resp.data

        _log_event(sb, 'chart_of_accounts', account_id, 'UPDATE', before, after)

        return {'success': True, 'account': after}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def deactivate_account(account_id, sb=None):
    try:
        sb = sb or _sb()
        resp = sb.table('chart_of_accounts').select('*').eq('accountid', account_id).single().execute()
        if not resp.data:
            return {'success': False, 'message': 'Account not found'}
        acc = resp.data
        # parse balance - check initialbalance
        bal = _parse_money(acc.get('initialbalance', 0))
        if bal > Decimal('0.00'):
            return {'success': False, 'message': 'Accounts with positive balance cannot be deactivated'}

        before = dict(acc)
        update = {'isactive': False}
        update_resp = sb.table('chart_of_accounts').update(update).eq('accountid', account_id).execute()
        if not update_resp.data:
            return {'success': False, 'message': 'Failed to deactivate account'}
        after = update_resp.data[0] if isinstance(update_resp.data, list) else update_resp.data
        _log_event(sb, 'chart_of_accounts', account_id, 'DEACTIVATE', before, after)
        return {'success': True, 'message': 'Account deactivated'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def list_accounts(page=1, per_page=50, search_term='', filters=None, sb=None):
    sb = sb or _sb()
    filters = filters or {}
    query = sb.table('chart_of_accounts').select('*')

    if search_term:
        query = query.or_(
            f'accountname.ilike.%{search_term}%,accountnumber.ilike.%{search_term}%'
        )

    # apply filters
    if filters.get('category'):
        query = query.eq('category', filters['category'])
    if filters.get('subcategory'):
        query = query.eq('subcategory', filters['subcategory'])
    if filters.get('is_active') is not None:
        query = query.eq('isactive', filters['is_active'])

    # count
    count_query = sb.table('chart_of_accounts').select('accountid', count='exact')
    if search_term:
        count_query = count_query.or_(
            f'accountname.ilike.%{search_term}%,accountnumber.ilike.%{search_term}%'
        )
    if filters.get('category'):
        count_query = count_query.eq('category', filters['category'])
    if filters.get('subcategory'):
        count_query = count_query.eq('subcategory', filters['subcategory'])

    count_resp = count_query.execute()
    total = count_resp.count if hasattr(count_resp, 'count') else (len(count_resp.data) if count_resp.data else 0)

    total_pages = (total // per_page) + (1 if total % per_page else 0) if total > 0 else 1
    offset = (page - 1) * per_page

    query = query.order('accountnumber', desc=False).range(offset, offset + per_page - 1)
    resp = query.execute()
    accounts = resp.data or []

    # format money fields for display
    for a in accounts:
        for k in ['initialbalance']:
            if a.get(k) is not None:
                try:
                    a[k+'_formatted'] = _format_money(_parse_money(a.get(k)))
                except Exception:
                    a[k+'_formatted'] = a.get(k)

    pagination = {
        'current_page': page,
        'per_page': per_page,
        'total_accounts': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None
    }

    return {'success': True, 'accounts': accounts, 'pagination': pagination}


def get_ledger_entries(account_number, sb=None, limit=200):
    """Best-effort ledger lookup. Tries common table names for transactions and returns rows related to account_number.
    If your DB uses a different table, adapt this function.
    Returns list of dicts with at least: date, description, debit, credit, running_balance
    """
    sb = sb or _sb()
    candidates = ['transactions', 'journal_entries', 'general_ledger', 'ledger_entries']
    results = []
    for table in candidates:
        try:
            # Try to select common columns
            resp = sb.table(table).select('*').or_(f"AccountNumber.eq.{account_number},Account.eq.{account_number}").order('Date', desc=False).limit(limit).execute()
            if resp and resp.data:
                # normalize minimal fields
                for r in (resp.data if isinstance(resp.data, list) else [resp.data]):
                    results.append({
                        'date': r.get('Date') or r.get('TransactionDate') or r.get('date'),
                        'description': r.get('Description') or r.get('Memo') or '',
                        'debit': r.get('Debit') or r.get('Amount') if r.get('Amount') and (r.get('Type')=='debit' if r.get('Type') else True) else None,
                        'credit': r.get('Credit') or (r.get('Amount') if r.get('Amount') and (r.get('Type')=='credit' if r.get('Type') else False) else None),
                        'raw': r
                    })
                break
        except Exception:
            continue
    return results
