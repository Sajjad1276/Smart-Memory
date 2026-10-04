from aiogram import Router

from app.bot.handlers import privacy, save, search, start, storage


def build_router() -> Router:
    router = Router(name="root")
    router.include_router(start.router)
    router.include_router(search.router)
    router.include_router(storage.router)
    router.include_router(privacy.router)
    router.include_router(save.router)
    return router
