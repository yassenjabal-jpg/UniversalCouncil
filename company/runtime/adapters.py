class MockAdapter:
    def __init__(self, mode='success'): self.mode=mode; self.calls=0
    def dispatch(self, action):
        self.calls+=1
        if self.mode=='reject': raise RuntimeError('provider rejected')
        if self.mode=='unknown_after_accept': return {'accepted':True,'provider_ref':'mock-accepted','unknown_after_accept':True}
        return {'accepted':True,'provider_ref':f'mock-{self.calls}','postcondition':True}

class UnsupportedAdapter:
    def dispatch(self, action): raise RuntimeError('unsupported capability')
