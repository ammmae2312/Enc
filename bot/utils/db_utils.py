from pymongo.errors import ServerSelectionTimeoutError

from bot import asyncio, bot_id
from bot.config import _bot, conf
from bot.startup.before import ffmpegdb, filterdb, pickle, queuedb, rssdb, userdb

from .bot_utils import list_to_str, sync_to_async
from .local_db_utils import save2db_lcl, save2db_lcl2

# i suck at using database -_-'
# But hey if it works don't touch it
# wanna fix this?
# PRs are welcome

_filter = {"_id": bot_id}

database = conf.DATABASE_URL


async def _update_db_with_retries(collection, update_data, retries=3):
    while retries:
        try:
            await sync_to_async(
                collection.update_one, _filter, {"$set": update_data}, upsert=True
            )
            break
        except ServerSelectionTimeoutError as e:
            retries -= 1
            if not retries:
                raise e
            await asyncio.sleep(0.5)


async def save2db(db="queue", retries=3):
    if not database:
        return await sync_to_async(save2db_lcl)
    d = {"queue": _bot.queue, "batches": _bot.batch_queue}
    data = pickle.dumps(d.get(db))
    _update = {db: data}
    await _update_db_with_retries(queuedb, _update, retries)


async def save2db2(data: dict | str = False, db: str = None, retries: int = 3):
    if not database:
        if data is False or db == "rss":
            await sync_to_async(save2db_lcl2, db)
        return
    if data is False:
        tusers = list_to_str(_bot.temp_users)
        data = pickle.dumps(tusers)
        _update = {"t_users": data}
        await _update_db_with_retries(userdb, _update, retries)
        return

    p_data = pickle.dumps(data)
    _update = {db: p_data}

    db_mapping = {
        "ffmpeg": ffmpegdb,
        "mux_args": ffmpegdb,
        "ffmpeg2": ffmpegdb,
        "ffmpeg3": ffmpegdb,
        "ffmpeg4": ffmpegdb,
        "autoname": filterdb,
        "cus_rename": filterdb,
        "filter": filterdb,
        "rss": rssdb,
    }

    collection = db_mapping.get(db)
    if collection:
        await _update_db_with_retries(collection, _update, retries)
