import logging
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования событий бота"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        start_time = time.time()
        try:
            user = data.get("event_from_user")
            user_info = self._get_user_info(user)
            
            # Логируем входящее событие
            await self.log_incoming_event(event, user_info)
            
            result = await handler(event, data)
            
            # Логируем результат обработки
            duration = time.time() - start_time
            logger.debug(
                f"Обработка завершена за {duration:.2f}s | "
                f"User: {user_info}"
            )
            
            return result
            
        except Exception as e:
            # Логируем ошибки
            logger.error(
                f"Ошибка: {str(e)} | "
                f"User: {user_info}", 
                exc_info=True
            )
            raise

    def _get_user_info(self, user) -> str:
        """Формирует информацию о пользователе"""
        if not user:
            return "Неизвестный пользователь"
            
        return (
            f"{user.full_name} [ID: {user.id}]"
            f"{f' @{user.username}' if user.username else ''}"
        )

    async def log_incoming_event(
        self, 
        event: TelegramObject, 
        user_info: str
    ):
        """Логирует детали входящего события"""
        if isinstance(event, Message):
            logger.info(
                f"Получено сообщение: {event.text or 'без текста'} | "
                f"User: {user_info}"
            )
        elif isinstance(event, CallbackQuery):
            logger.info(
                f"Получен callback: {event.data} | "
                f"User: {user_info}"
            )
        else:
            logger.debug(
                f"Получено событие типа {type(event).__name__} | "
                f"User: {user_info}"
            )
