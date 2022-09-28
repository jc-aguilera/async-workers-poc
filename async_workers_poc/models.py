from dataclasses import dataclass, field


@dataclass
class Job:
    id: int
    type: str = field(repr=False)
    status: str


@dataclass
class Worker:
    id: int
