import asyncio
import random
import sqlite3
from datetime import datetime
from typing import Any, Awaitable

import pandas as pd

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

SYMBOLS = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF"]


def timestamp() -> str:
    return datetime.now().strftime("%x %X")


def rand_price() -> float:
    return round(random.random() * 250, 2)


# === Initialize the database =========================================


def init_db(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    try:
        cur.executescript(
            """
            CREATE TABLE stock_quotes (timestamp text, symbol text, price real);
            CREATE INDEX idx_timestamp ON stock_quotes (timestamp);
            """
        )
        cur.executemany(
            "INSERT INTO stock_quotes (timestamp, symbol, price) VALUES (?, ?, ?)",
            [(timestamp(), symbol, rand_price()) for symbol in SYMBOLS],
        )
        con.commit()
    finally:
        cur.close()


conn = sqlite3.connect(":memory:")
init_db(conn)


# === Randomly update the database with an asyncio.task ==============


def update_db(con: sqlite3.Connection) -> None:
    """Update a single stock price entry at random"""

    cur = con.cursor()
    try:
        sym = SYMBOLS[random.randint(0, len(SYMBOLS) - 1)]
        print(f"Updating {sym}")
        cur.execute(
            "UPDATE stock_quotes SET timestamp = ?, price = ? WHERE symbol = ?",
            (timestamp(), rand_price(), sym),
        )
        con.commit()
    finally:
        cur.close()


async def update_db_task(con: sqlite3.Connection) -> Awaitable[None]:
    """Task that alternates between sleeping and updating prices"""
    while True:
        await asyncio.sleep(random.random() * 1.5)
        update_db(con)


asyncio.create_task(update_db_task(conn))


# === Create the reactive.poll object ===============================


def tbl_last_modified() -> Any:
    df = pd.read_sql_query("SELECT MAX(timestamp) AS timestamp FROM stock_quotes", conn)
    return df["timestamp"].to_list()


@reactive.poll(tbl_last_modified, 0.5)
def stock_quotes() -> pd.DataFrame:
    return pd.read_sql_query("SELECT timestamp, symbol, price FROM stock_quotes", conn)


# === Define the Shiny UI and server ===============================

app_ui = ui.page_fluid(
    ui.row(
        ui.column(
            8,
            ui.markdown(
                """
                # `shiny.reactive.poll` demo

                This example app shows how to stream results from a database (in this
                case, an in-memory sqlite3) with the help of `shiny.reactive.poll`.
                """
            ),
            class_="mb-3",
        ),
    ),
    ui.input_selectize("symbols", "Filter by symbol", [""] + SYMBOLS, multiple=True),
    ui.output_ui("table"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    def filtered_quotes():
        df = stock_quotes()
        if input.symbols():
            df = df[df["symbol"].isin(input.symbols())]
        return df

    @output
    @render.ui
    def table():
        return ui.HTML(
            filtered_quotes().to_html(
                index=False, classes="table font-monospace w-auto"
            )
        )


app = App(app_ui, server)
