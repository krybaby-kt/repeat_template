from typing import Dict, TypeVar, Callable, Any, Union, Tuple, Optional
from functools import wraps
import logging
import inspect
import asyncio
import time


logger = logging.getLogger(__name__)

# TypeVar для поддержки типизации возвращаемых значений
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


def __repeat__(
    _func: Optional[F] = None,
    *,
    tries: int = 5,
    delay: float = 0.0,
    exceptions: Union[Exception, Tuple[Exception, ...]] = Exception,
    backoff: float = 1.0
) -> Union[F, Callable[[F], F]]:
    """
    Универсальный декоратор для повторения выполнения функций.
    
    Args:
        tries: Количество попыток выполнения
        delay: Задержка между попытками в секундах
        exceptions: Типы исключений для обработки
        backoff: Множитель увеличения задержки (экспоненциальный backoff)
    """
    def decorator_repeat(func: F) -> F:
        if inspect.iscoroutinefunction(func):
            return _create_async_wrapper(func, tries, delay, exceptions, backoff)
        else:
            return _create_sync_wrapper(func, tries, delay, exceptions, backoff)
    
    if _func is None:
        return decorator_repeat
    else:
        return decorator_repeat(_func)



def _create_sync_wrapper(func: Callable[..., T], tries: int, delay: float, 
                        exceptions: Union[Exception, Tuple[Exception, ...]], 
                        backoff: float) -> Callable[..., T]:
    """Создает wrapper для синхронных функций"""
    @wraps(func)
    def wrapper_sync(*args: Any, **kwargs: Any) -> T:
        last_exception = None
        current_delay = delay
        
        for attempt in range(tries):
            try:
                return func(*args, **kwargs)
            except exceptions as ex:
                last_exception = ex
                
                if attempt < tries - 1:
                    logger.warning(
                        f"Attempt {attempt + 1}/{tries} failed: {ex}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    
                    if current_delay > 0:
                        time.sleep(current_delay)
                    
                    current_delay *= backoff
                else:
                    logger.error(f"All {tries} attempts failed. Last error: {ex}")
        
        raise last_exception
    
    return wrapper_sync


def _create_async_wrapper(func: Callable[..., Any], tries: int, delay: float,
                         exceptions: Union[Exception, Tuple[Exception, ...]], 
                         backoff: float) -> Callable[..., Any]:
    """Создает wrapper для асинхронных функций"""
    @wraps(func)
    async def wrapper_async(*args: Any, **kwargs: Any) -> Any:
        async def executor() -> Any:
            return await func(*args, **kwargs)
        
        last_exception = None
        current_delay = delay
        
        for attempt in range(tries):
            try:
                return await executor()
            except exceptions as ex:
                last_exception = ex
                
                if attempt < tries - 1:
                    logger.warning(
                        f"Attempt {attempt + 1}/{tries} failed: {ex}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    
                    if current_delay > 0:
                        await asyncio.sleep(current_delay)
                    
                    current_delay *= backoff
                else:
                    logger.error(f"All {tries} attempts failed. Last error: {ex}")
        
        raise last_exception
    
    return wrapper_async


if __name__ == "__main__":
    # Настройка логирования для демонстрации
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
    
    print("=== Тест базовой функциональности ===")
    
    # Тест синхронной функции
    @__repeat__(tries=3)
    def test_sync():
        print("Sync function test")
        raise Exception("Sync test exception")
    
    # Тест асинхронной функции
    @__repeat__(tries=3)
    async def test_async():
        print("Async function test")
        raise Exception("Async test exception")
    
    try:
        test_sync()
    except Exception:
        print("✓ Sync test completed\n")
    
    try:
        asyncio.run(test_async())
    except Exception:
        print("✓ Async test completed\n")
    
    print("=== Тест с задержкой и экспоненциальным backoff ===")
    
    @__repeat__(tries=3, delay=0.5, backoff=2.0)
    def test_with_delay():
        print("Function with delay called")
        raise ConnectionError("Network error")
    
    try:
        test_with_delay()
    except Exception:
        print("✓ Delay test completed\n")
    
    print("=== Тест фильтрации исключений ===")
    
    @__repeat__(tries=3, exceptions=ValueError)
    def test_specific_exception():
        print("Testing specific exception handling")
        raise RuntimeError("This won't be retried")
    
    try:
        test_specific_exception()
    except RuntimeError:
        print("✓ RuntimeError passed through without retry\n")
    
    @__repeat__(tries=3, exceptions=(ValueError, TypeError))
    def test_multiple_exceptions():
        print("Testing multiple exceptions")
        raise ValueError("This will be retried")
    
    try:
        test_multiple_exceptions()
    except ValueError:
        print("✓ Multiple exceptions test completed")