# from .parameterized import param as param, parameterized as parameterized, parameterized_class as parameterized_class

from typing import Any, Callable, Iterable

# name_func: Callable[[Any], str] | None = None,
# doc_func: Callable[[Any], str] | None = None,
# skip_on_empty: bool = False,
# namespace: dict[str, Any] | None = None) \


# noinspection PyPep8Naming
class parameterized:
  @classmethod
  def expand(cls, input: Iterable[Any]) \
      -> Callable[..., Any]:
    pass  # Implementation would go here
