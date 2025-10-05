import types
import pytest

#This file is to fake a supabase client for testing purposes

class FakeQuery:
    """Fakes supabase chain queries to prevent breaking the functions being tested."""
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
    
    #Returns fake supabase object with .data attribute
    def execute(self):
        result = self._result
        # If the result is a list, return next item each time execute is called
        if isinstance(result, list):
            next_item = result.pop(0) if result else None
            return types.SimpleNamespace(data=next_item)
        # Otherwise return the single result
        return types.SimpleNamespace(data=self._result)

class FakeTableRouter:
    """Returns a predefined FakeQuery for each table and operation."""
    def __init__(self, responses):
        self.responses = responses  #dict like {('users','select'): ..., ('users','update'): ...}
        self.current_table = None
        self.current_op = None
        self.pending_update = False

    def table(self, name):
        self.current_table = name
        self.current_op = 'select'
        self.pending_update = False
        return self

    def select(self, *_a, **_k):
        return FakeQuery(self.responses.get((self.current_table, 'select')))
    def insert(self, *_a, **_k):
        return FakeQuery(self.responses.get((self.current_table, 'insert')))
    def update(self, *_a, **_k):
        return FakeQuery(self.responses.get((self.current_table, 'update')))
    def delete(self, *_a, **_k):
        return FakeQuery(self.responses.get((self.current_table, 'delete')))

@pytest.fixture
def fake_sb_factory():
    def _make(responses):
        return FakeTableRouter(responses)
    return _make
