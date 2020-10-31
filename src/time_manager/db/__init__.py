from typing import Generic, Optional, Protocol, Sequence, TypeVar

T = TypeVar("T")


class Dao(Protocol, Generic[T]):
    def post(self, item: T) -> T:
        ...

    def put(self, id: int, instance: T, partial: Optional[bool] = False) -> T:
        ...

    def delete(self, id: int) -> T:
        ...

    def filter(
        self, skip: Optional[int] = 0, limit: Optional[int] = -1, **kwargs
    ) -> Sequence[T]:
        ...
