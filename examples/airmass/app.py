import datetime
from typing import Dict, List, Optional, Tuple

import astropy.units as u
import matplotlib.dates as mpldates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytz
import suntime
import timezonefinder
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from location import location_server, location_ui

from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

app_ui = ui.page_fixed(
    ui.tags.h3("Air mass calculator"),
    ui.div(
        ui.markdown(
            """This Shiny app uses [Astropy](https://www.astropy.org/) to calculate the
            altitude (degrees above the horizon) and airmass (the amount of atmospheric
            air along your line of sight to an object) of one or more astronomical
            objects, over a given evening, at a given geographic location.
            """
        ),
        class_="mb-5",
    ),
    ui.row(
        ui.column(
            8,
            ui.output_ui("timeinfo"),
            ui.output_plot("plot", height="800px"),
            # For debugging
            # ui.output_table("table"),
            class_="order-2 order-sm-1",
        ),
        ui.column(
            4,
            ui.panel_well(
                ui.input_date("date", "Date"),
                class_="pb-1 mb-3",
            ),
            ui.panel_well(
                ui.input_text_area(
                    "objects", "Target object(s)", "M1, NGC35, PLX299", rows=3
                ),
                class_="pb-1 mb-3",
            ),
            ui.panel_well(
                location_ui("location"),
                class_="mb-3",
            ),
            class_="order-1 order-sm-2",
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    loc = location_server("location")
    time_padding = datetime.timedelta(hours=1.5)

    @reactive.calc
    def obj_names() -> List[str]:
        """Returns a split and *slightly* cleaned-up list of object names"""
        req(input.objects())
        return [x.strip() for x in input.objects().split(",") if x.strip() != ""]

    @reactive.calc
    def obj_coords() -> List[SkyCoord]:
        return [SkyCoord.from_name(name) for name in obj_names()]

    @reactive.calc
    def times_utc() -> Tuple[datetime.datetime, datetime.datetime]:
        req(input.date())
        lat, long = loc()
        sun = suntime.Sun(lat, long)
        day = datetime.datetime.combine(input.date(), datetime.time())
        return (
            sun.get_sunset_time(day),
            sun.get_sunrise_time(day + datetime.timedelta(days=1)),
        )

    @reactive.calc
    def timezone() -> Optional[str]:
        lat, long = loc()
        return timezonefinder.TimezoneFinder().timezone_at(lat=lat, lng=long)

    @reactive.calc
    def times_at_loc():
        start, end = times_utc()
        tz = pytz.timezone(timezone())
        return (start.astimezone(tz), end.astimezone(tz))

    @reactive.calc
    def df() -> Dict[str, pd.DataFrame]:
        start, end = times_at_loc()
        times = pd.date_range(
            start - time_padding,
            end + time_padding,
            periods=100,
        )
        lat, long = loc()
        eloc = EarthLocation(lat=lat * u.deg, lon=long * u.deg, height=0)
        altaz_list = [
            obj.transform_to(AltAz(obstime=times, location=eloc))
            for obj in obj_coords()
        ]
        return {
            obj: pd.DataFrame(
                {
                    "obj": obj,
                    "time": times,
                    "alt": altaz.alt,
                    # Filter out discontinuity
                    "secz": np.where(altaz.alt > 0, altaz.secz, np.nan),
                }
            )
            for (altaz, obj) in zip(altaz_list, obj_names())
        }

    @render.plot
    def plot():
        fig, [ax1, ax2] = plt.subplots(nrows=2)

        sunset, sunrise = times_at_loc()

        def add_boundary(ax, xval):
            ax.axvline(x=xval, c="#888888", ls="dashed")

        ax1.set_ylabel("Altitude (deg)")
        ax1.set_xlabel("Time")
        ax1.set_ylim(-10, 90)
        ax1.set_xlim(sunset - time_padding, sunrise + time_padding)
        ax1.grid()
        add_boundary(ax1, sunset)
        add_boundary(ax1, sunrise)
        for obj_name, data in df().items():
            ax1.plot(data["time"], data["alt"], label=obj_name)
        ax1.xaxis.set_major_locator(mpldates.AutoDateLocator())
        ax1.xaxis.set_major_formatter(
            mpldates.DateFormatter("%H:%M", tz=pytz.timezone(timezone()))
        )
        ax1.legend(loc="upper right")

        ax2.set_ylabel("Air mass")
        ax2.set_xlabel("Time")
        ax2.set_ylim(4, 1)
        ax2.set_xlim(sunset - time_padding, sunrise + time_padding)
        ax2.grid()
        add_boundary(ax2, sunset)
        add_boundary(ax2, sunrise)
        for data in df().values():
            ax2.plot(data["time"], data["secz"])
        ax2.xaxis.set_major_locator(mpldates.AutoDateLocator())
        ax2.xaxis.set_major_formatter(
            mpldates.DateFormatter("%H:%M", tz=pytz.timezone(timezone()))
        )

        return fig

    @render.table
    def table() -> pd.DataFrame:
        return pd.concat(df())

    @render.ui
    def timeinfo():
        start_utc, end_utc = times_utc()
        start_at_loc, end_at_loc = times_at_loc()
        return ui.TagList(
            f"Sunset: {start_utc.strftime('%H:%M')}, ",
            f"Sunrise: {end_utc.strftime('%H:%M')} ",
            "(UTC)",
            ui.tags.br(),
            f"Sunset: {start_at_loc.strftime('%H:%M')}, ",
            f"Sunrise: {end_at_loc.strftime('%H:%M')} ",
            f"({timezone()})",
        )


# The debug=True causes it to print messages to the console.
app = App(app_ui, server, debug=False)
