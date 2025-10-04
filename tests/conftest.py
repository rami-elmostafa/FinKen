import types
import pytest

class FakeQuery:
    """Mimics a chain like .select(...).eq(...).single().execute()."""
    def __init__(self, result):
        self._result = result
    def select(self, *_args, **_kwargs): 
        return self
    def eq(self, *_args, **_kwargs): 
        return self
    def single(self): 
        return self
    def order(self, *_a, **_k): 
        return self
    def limit(self, *_a, **_k): 
        return self
    def update(self, *_a, **_k): 
        return self
    def insert(self, *_a, **_k): 
        return self
    #Fake supabase object with .data attribute
    def execute(self):
        return types.SimpleNamespace(data=self._result)

class FakeTableRouter:
    """Returns a predefined FakeQuery for each table and operation."""
    def __init__(self, responses):
        self.responses = responses  # dict like {('users','select'): ..., ('users','update'): ...}
        self._current_table = None
        self._current_op = None
        self._pending_update = False

    def table(self, name):
        self._current_table = name
        self._current_op = 'select'
        self._pending_update = False
        return self

    # Methods used in your code path:
    def select(self, *_a, **_k):
        self._current_op = 'select'
        return FakeQuery(self.responses.get((self._current_table, 'select')))
    def update(self, *_a, **_k):
        self._current_op = 'update'
        return FakeQuery(self.responses.get((self._current_table, 'update')))
    
    # If you need history or other ops in other tests:
    def insert(self, *_a, **_k):
        return FakeQuery(self.responses.get((self._current_table, 'insert')))

@pytest.fixture
def fake_sb_factory():
    def _make(responses):
        return FakeTableRouter(responses)
    return _make
