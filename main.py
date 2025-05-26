import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook

import config
from handlers import common, food
from middleware.database import DataBaseSession
from storage.database import session_maker

TOKEN = config.get("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


async def main():
    logger.info("Bot started")
    dp.include_routers(common.router, food.food_router)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
