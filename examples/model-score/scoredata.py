import asyncio
import datetime
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

here = Path(__file__).parent
auc_scores = pd.read_csv(here / "fake_auc_scores.csv")
auc_scores.set_index("second", inplace=True)
(here / "data").mkdir(exist_ok=True)

SQLITE_DB_URI = f"file:{here / 'data' / 'auc_scores.sqlite'}"


async def async_main():
    with sqlite3.connect(SQLITE_DB_URI, uri=True, timeout=30) as con:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("drop table if exists auc_scores")

        now = datetime.datetime.utcnow()
        position = now.minute * 60 + now.second + 1

        # Simulate 100 seconds of historical data
        offset_secs = -np.arange(100) - 1
        abs_secs = (position + offset_secs) % (60 * 60) + 1
        initial_scores = auc_scores.loc[abs_secs]
        timestamps = pd.DataFrame(
            {
                "timestamp": now + pd.to_timedelta(offset_secs, unit="s"),
                "second": abs_secs,
            }
        ).set_index("second", inplace=False)
        initial_scores = initial_scores.join(timestamps, how="left")
        initial_scores.to_sql("auc_scores", con, index=False, if_exists="append")

        while True:
            new_data = auc_scores.loc[position].copy()
            # del new_data["second"]
            new_data["timestamp"] = datetime.datetime.utcnow()
            new_data.to_sql("auc_scores", con, index=False, if_exists="append")
            position = (position % (60 * 60)) + 1
            await asyncio.sleep(1)


def begin():
    asyncio.create_task(async_main())
