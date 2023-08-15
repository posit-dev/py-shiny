import asyncio
import datetime
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

here = Path(__file__).parent
accuracy_scores = pd.read_csv(here / "fake_accuracy_scores.csv")
accuracy_scores.set_index("second", inplace=True)
(here / "data").mkdir(exist_ok=True)

SQLITE_DB_URI = f"file:{here / 'data' / 'accuracy_scores.sqlite'}"


def init_db():
    with sqlite3.connect(SQLITE_DB_URI, uri=True, timeout=30) as con:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("drop table if exists accuracy_scores")

        now = datetime.datetime.utcnow()
        position = now.minute * 60 + now.second + 1

        # Simulate 100 seconds of historical data
        offset_secs = -np.arange(100) - 1
        abs_secs = (position + offset_secs) % (60 * 60) + 1
        initial_scores = accuracy_scores.loc[abs_secs]
        timestamps = pd.DataFrame(
            {
                "timestamp": now + pd.to_timedelta(offset_secs, unit="s"),
                "second": abs_secs,
            }
        ).set_index("second", inplace=False)
        initial_scores = initial_scores.join(timestamps, how="left")
        initial_scores.to_sql("accuracy_scores", con, index=False, if_exists="append")

        con.execute(
            "create index idx_accuracy_scores_timestamp on accuracy_scores(timestamp)"
        )

        return position


async def update_db(position):
    with sqlite3.connect(SQLITE_DB_URI, uri=True, timeout=30) as con:
        while True:
            new_data = accuracy_scores.loc[position].copy()
            # del new_data["second"]
            new_data["timestamp"] = datetime.datetime.utcnow()
            new_data.to_sql("accuracy_scores", con, index=False, if_exists="append")
            position = (position % (60 * 60)) + 1
            await asyncio.sleep(1)


def begin():
    position = init_db()

    # After initializing the database, we need to start a non-blocking task to update it
    # every second or so. If an event loop is already running, we can use an asyncio
    # task. (This is the case when running via `shiny run` and shinylive.) Otherwise, we
    # need to launch a background thread and run an asyncio event loop there. (This is
    # the case when running via shinyapps.io or Posit Connect.)

    if asyncio.get_event_loop().is_running():
        asyncio.create_task(update_db(position))
    else:
        from threading import Thread

        Thread(target=lambda: asyncio.run(update_db(position)), daemon=True).start()
