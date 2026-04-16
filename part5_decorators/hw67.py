import json
from datetime import UTC, datetime
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime):
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        exceptions = []

        if critical_count <= 0 or not isinstance(critical_count, int):
            exceptions.append(ValueError(INVALID_CRITICAL_COUNT))

        if time_to_recover <= 0 or not isinstance(time_to_recover, int):
            exceptions.append(ValueError(INVALID_RECOVERY_TIME))

        if len(exceptions) > 0:
            raise ExceptionGroup(VALIDATIONS_FAILED, exceptions)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self.count = 0
        self.when_blocked: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        self._func_name = f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            if self.when_blocked is not None:
                if self.has_recovered():
                    self.count = 0
                    self.when_blocked = None
                else:
                    raise BreakerError(self._func_name, self.when_blocked)

            try:
                result = func(*args, **kwargs)

            except self.triggers_on as error:
                self.handle_error(error)
                raise

            else:
                self.count = 0
                return result

        return wrapper

    def has_recovered(self) -> bool:
        if self.when_blocked is None:
            return True

        current_time = datetime.now(UTC)
        when_blocked = self.when_blocked

        diff = (current_time - when_blocked).total_seconds()

        return diff >= self.time_to_recover

    def handle_error(self, error: Exception) -> None:
        self.count += 1
        if self.count >= self.critical_count:
            self.when_blocked = datetime.now(UTC)
            raise BreakerError(self._func_name, self.when_blocked) from error


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
