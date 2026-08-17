from __future__ import annotations

import pandas as pd

from shiny.express import input, render, ui

ui.page_opts(title="Healthcare Logistics & Capacity Simulation", fillable=True)

with ui.sidebar(title="Simulation Parameters"):
    ui.input_select(
        "facility_type",
        "Facility Classification",
        choices=["Regional Trauma", "Metropolitan General", "Community Clinic"],
        selected="Regional Trauma",
    )
    ui.input_slider(
        "bed_capacity", "Available Inpatient Beds", min=50, max=500, value=200
    )
    ui.input_numeric(
        "patient_volume", "Daily Expected Influx", value=150, min=10, max=2000
    )
    ui.input_slider(
        "staff_ratio", "Nurse-to-Patient Ratio", min=0.1, max=1.0, value=0.25, step=0.05
    )
    ui.input_numeric(
        "surge_multiplier", "Surge Risk Factor", value=1.2, min=1.0, max=3.0, step=0.1
    )

    with ui.accordion(open=False):
        with ui.accordion_panel("Advanced Configuration"):
            ui.input_checkbox("include_icu", "Include ICU Wing", value=True)
            ui.input_select(
                "referral_route",
                "Secondary Referral Route",
                choices=["Direct Transfer", "Hub & Spoke", "Diverted"],
                selected="Direct Transfer",
            )
            ui.input_numeric(
                "fixed_overhead", "Daily Fixed Overhead ($k)", value=45, min=10, max=500
            )

with ui.layout_columns():
    with ui.value_box(showcase=ui.span("🏥")):
        "Occupancy Rate"

        @render.text
        def occupancy_kpi():
            beds = input.bed_capacity()
            patients = input.patient_volume()
            rate = (patients / beds) * 100
            return f"{rate:.1f}%"

    with ui.value_box(showcase=ui.span("👩‍⚕️")):
        "Staffing Capacity"

        @render.text
        def staffing_kpi():
            nurses_needed = input.patient_volume() * input.staff_ratio()
            available_shift_slots = input.bed_capacity() * 0.4
            coverage = (available_shift_slots / nurses_needed) * 100
            return f"{coverage:.0f}% Coverage"

    with ui.value_box(showcase=ui.span("💵")):
        "Daily Operational Cost"

        @render.text
        def cost_kpi():
            patients = input.patient_volume()
            fixed = input.fixed_overhead()
            cost = (patients * 1.85 * input.surge_multiplier()) + (fixed * 1000)
            return f"${cost:,.0f}"


with ui.layout_columns(col_widths=(6, 6)):
    with ui.card():
        ui.card_header("Departmental Load Breakdown")

        @render.data_frame
        def load_table():
            depts = ["Emergency", "Critical Care", "General Ward", "Step-Down"]
            patients = input.patient_volume()
            beds = input.bed_capacity()

            allocations = [0.35, 0.20, 0.30, 0.15]
            dept_patients = [int(patients * a) for a in allocations]
            dept_beds = [int(beds * a) for a in allocations]
            occupancies = [
                f"{(p / b) * 100:.1f}%" if b > 0 else "N/A"
                for p, b in zip(dept_patients, dept_beds)
            ]

            df = pd.DataFrame(
                {
                    "Department": depts,
                    "Current Load": dept_patients,
                    "Bed Allocation": dept_beds,
                    "Occupancy": occupancies,
                }
            )
            return render.DataGrid(df, width="100%")

    with ui.card():
        ui.card_header("Risk Assessment & Triage Directives")

        @render.text
        def triage_alert():
            patients = input.patient_volume()
            beds = input.bed_capacity()
            surge = input.surge_multiplier()

            projected_peak = patients * surge
            if projected_peak > beds * 1.25:
                return "CRITICAL SURGE: Inpatient capacity exceeded by over 25%. Initiate emergency overflow protocol."
            elif projected_peak > beds:
                return "WARNING: Peak projections exceed standard bed count. Restrict elective admissions."
            else:
                return "NORMAL: Facility operating within safe capacity limits."
