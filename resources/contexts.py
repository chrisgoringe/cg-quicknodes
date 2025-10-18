import numpy as np
import datasets
from typing import Optional
from .formats import wrap

class Context(tuple):
    def __new__(cls, summary:str, prompt:str):
        return super().__new__(cls, (summary, prompt))

    def wrapped(self) -> str:
        return (wrap("user",self[0]) if self[0] else "") + (wrap("assistant",self[1]) if self[1] else "")
    
    @property
    def prompt(self) -> str:
        return self[1] or ""

class ContextList:
    def __init__(self, contexts:list[Context], infos:list[int]=[]):
        self.contexts:list[Context] = contexts
        self.infos:list[int]        = infos

    def __len__(self) -> int:
        return len(self.contexts)

    def add_from(self, context:Optional['ContextList']) -> 'ContextList':
        if context is not None and len(context)>0:
            self.contexts.extend(context.contexts)
            self.infos.extend(context.infos)
        return self
    
    def shuffle(self, seed:int) -> 'ContextList':
        rng = np.random.default_rng(abs(seed))
        order = list(rng.permutation(len(self.contexts)))
        self.contexts = [ self.contexts[i] for i in order ]
        self.infos    = [ self.infos[i]    for i in order ]
        return self
    
    def copy(self) -> 'ContextList':
        return ContextList(self.contexts, self.infos) 

    @property
    def info(self) -> str:
        return ",".join(str(x) for x in self.infos)
    
    @classmethod
    def from_dataset(cls, ds:datasets.Dataset, n, seed:int, weighting:Optional[float]=None) -> 'ContextList':
        rng = np.random.default_rng(abs(seed or 0))
        p = [ pow(weighting, x) for x in ds['score'] ] if (weighting and weighting!=1.0) else [1.0] * len(ds)
        p = p / np.sum(p, dtype=float)
        chosen = rng.choice(len(ds), size=n, replace=False, p=p)
        chosen = list(int(chosen[-x]) for x in range(n))  # reverse order so first chosen is last in prompt (most recent in context)
        return cls([ Context( f"{ds[x]['summary']}", f"{ds[x]['prompt']}" ) for x in chosen ], [int(ds[x]['idx'] or 0) for x in chosen])