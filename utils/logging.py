import functools

import logging
from datetime import datetime
from typing import Callable

logger = logging.getLogger()


def log_route(route_name: str = None):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = logging.getLogger()
            route = route_name or f"{func.__module__}.{func.__name__}"
            
            # Извлекаем информацию о запросе
            request_info = ""
            if args and hasattr(args[0], 'request'):
                request = args[0].request
                request_info = f" | {request.method} {request.url.path}"
            
            logger.info(f"📥 Запрос: {route}{request_info}")
            
            start_time = datetime.now()
            
            db = kwargs.get("db")

            try:
                result = await func(*args, **kwargs)
                
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"�� Ответ: {route} | {execution_time:.3f}с | Успех")
                async with db() as session:
                    log_data = {
                        "log_type": "response",
                        "log_data": {
                            "route": route,
                            "request_info": request_info
                        },
                        "log_message": f"Ответ: {route}{request_info} | {execution_time:.3f}с | Успех"
                    }
                    print(log_data["log_message"]) # TODO: add logging to the database
                return result
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"💥 Ошибка: {route} | {execution_time:.3f}с | {str(e)}")
                async with db() as session:
                    log_data = {
                        "log_type": "error",
                        "log_data": {
                            "route": route,
                            "request_info": request_info
                        },
                        "log_message": f"Ошибка: {route}{request_info} | {execution_time:.3f}с | {str(e)}"
                    }
                    print(log_data["log_message"]) # TODO: add logging to the database
                raise
        
        return wrapper
    return decorator