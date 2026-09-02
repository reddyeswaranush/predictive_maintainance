"""Records page: create the operational records that feed the platform.

Every payload sent from this page matches the existing FastAPI schemas exactly;
only the layout and validation feedback were reworked.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend import api
from frontend import components as ui
from frontend.transforms import format_table, machine_label

TELEMETRY_FIELDS: list[tuple[str, str]] = [
    ("temperature", "Temperature"),
    ("pressure", "Pressure"),
    ("vibration", "Vibration"),
    ("voltage", "Voltage"),
    ("current", "Current"),
    ("power", "Power"),
    ("rpm", "RPM"),
    ("humidity", "Humidity"),
    ("oil_level", "Oil level"),
    ("health_score", "Health score"),
    ("failure_probability", "Failure probability (0-1)"),
]


def render(collections: dict[str, pd.DataFrame]) -> None:
    machines = collections.get("machines", pd.DataFrame())
    machine_ids = machines["machine_id"].tolist() if "machine_id" in machines else []

    tabs = st.tabs(["Machine", "Telemetry", "Maintenance", "Incident", "Inventory", "Notification", "Sensor"])
    with tabs[0]:
        _machine_form()
    with tabs[1]:
        _telemetry_form(machines, machine_ids)
    with tabs[2]:
        _maintenance_form(machines, machine_ids)
    with tabs[3]:
        _incident_form(machines, machine_ids)
    with tabs[4]:
        _inventory_form()
    with tabs[5]:
        _notification_form(collections.get("notifications", pd.DataFrame()))
    with tabs[6]:
        _sensor_form()


def _submit(ok: bool, message: str) -> None:
    (st.success if ok else st.error)(message)


def _machine_select(label: str, machines: pd.DataFrame, machine_ids: list[int], key: str) -> int:
    return st.selectbox(
        label,
        machine_ids,
        format_func=lambda identifier: machine_label(identifier, machines),
        key=key,
    )


def _machine_form() -> None:
    ui.section("Register a machine")
    with st.form("create_machine", clear_on_submit=True, border=False):
        left, right = st.columns(2, gap="medium")
        name = left.text_input("Machine name", placeholder="Required")
        department = right.text_input("Department")
        location = left.text_input("Location")
        status = right.selectbox("Status", ["Running", "Idle", "Maintenance", "Stopped"])
        if st.form_submit_button("Add machine", type="primary"):
            if not name.strip():
                st.error("Machine name is required.")
            else:
                _submit(
                    *api.send_record(
                        "POST",
                        "machines",
                        {
                            "machine_name": name.strip(),
                            "department": department or None,
                            "location": location or None,
                            "status": status,
                        },
                    )
                )


def _telemetry_form(machines: pd.DataFrame, machine_ids: list[int]) -> None:
    ui.section("Record a telemetry reading")
    if not machine_ids:
        ui.empty_state("Register a machine before entering telemetry.")
        return
    with st.form("create_telemetry", clear_on_submit=True, border=False):
        machine_id = _machine_select("Machine", machines, machine_ids, "telemetry_machine")
        columns = st.columns(3, gap="medium")
        values: dict[str, float] = {}
        for index, (key, label) in enumerate(TELEMETRY_FIELDS):
            values[key] = columns[index % 3].number_input(label, min_value=0.0, value=0.0, key=f"telemetry_{key}")
        if st.form_submit_button("Record reading", type="primary"):
            _submit(*api.send_record("POST", "telemetry", {"machine_id": machine_id, **values}))


def _maintenance_form(machines: pd.DataFrame, machine_ids: list[int]) -> None:
    ui.section("Create a work order")
    if not machine_ids:
        ui.empty_state("Register a machine before creating a work order.")
        return
    with st.form("create_maintenance", clear_on_submit=True, border=False):
        left, right = st.columns(2, gap="medium")
        with left:
            machine_id = _machine_select("Machine", machines, machine_ids, "maintenance_machine")
            technician = st.text_input("Technician", placeholder="Required")
            remarks = st.text_input("Remarks", placeholder="Required")
        with right:
            maintenance_type = st.selectbox(
                "Type", ["Inspection", "Preventive", "Corrective", "Predictive", "Emergency"]
            )
            cost = st.number_input("Cost", min_value=0.0, value=0.0)
            status = st.selectbox("Status", ["Scheduled", "In Progress", "Completed"])
        if st.form_submit_button("Create work order", type="primary"):
            if not technician.strip() or not remarks.strip():
                st.error("Technician and remarks are required.")
            else:
                _submit(
                    *api.send_record(
                        "POST",
                        "maintenance",
                        {
                            "machine_id": machine_id,
                            "maintenance_type": maintenance_type,
                            "technician": technician,
                            "cost": cost,
                            "remarks": remarks,
                            "status": status,
                        },
                    )
                )


def _incident_form(machines: pd.DataFrame, machine_ids: list[int]) -> None:
    ui.section("Log an incident")
    if not machine_ids:
        ui.empty_state("Register a machine before logging an incident.")
        return
    with st.form("create_incident", clear_on_submit=True, border=False):
        left, right = st.columns(2, gap="medium")
        machine_id = left.selectbox(
            "Machine",
            machine_ids,
            format_func=lambda identifier: machine_label(identifier, machines),
            key="incident_machine",
        )
        priority = right.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        description = st.text_area("Description", placeholder="Required")
        assigned_to = left.text_input("Assigned to", placeholder="Required")
        status = right.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
        if st.form_submit_button("Log incident", type="primary"):
            if not description.strip() or not assigned_to.strip():
                st.error("Description and assignee are required.")
            else:
                _submit(
                    *api.send_record(
                        "POST",
                        "incidents",
                        {
                            "machine_id": machine_id,
                            "priority": priority,
                            "description": description,
                            "assigned_to": assigned_to,
                            "status": status,
                        },
                    )
                )


def _inventory_form() -> None:
    ui.section("Add an inventory item")
    with st.form("create_inventory", clear_on_submit=True, border=False):
        left, right = st.columns(2, gap="medium")
        item_name = left.text_input("Item name", placeholder="Required")
        quantity = right.number_input("Quantity", min_value=0, value=0, step=1)
        supplier = left.text_input("Supplier", placeholder="Required")
        status = right.selectbox("Stock status", ["Available", "Low Stock", "Out of Stock"])
        if st.form_submit_button("Add item", type="primary"):
            if not item_name.strip() or not supplier.strip():
                st.error("Item name and supplier are required.")
            else:
                _submit(
                    *api.send_record(
                        "POST",
                        "inventory",
                        {
                            "item_name": item_name,
                            "quantity": quantity,
                            "supplier": supplier,
                            "status": status,
                        },
                    )
                )


def _notification_form(notifications: pd.DataFrame) -> None:
    ui.section("Publish a notification")
    with st.form("create_notification", clear_on_submit=True, border=False):
        title = st.text_input("Title", placeholder="Required")
        message = st.text_area("Message", placeholder="Required")
        left, right = st.columns(2, gap="medium")
        notification_type = left.selectbox("Type", ["Info", "Alert", "Warning", "Critical"])
        status = right.selectbox("Status", ["Unread", "Read"])
        if st.form_submit_button("Publish", type="primary"):
            if not title.strip() or not message.strip():
                st.error("Title and message are required.")
            else:
                _submit(
                    *api.send_record(
                        "POST",
                        "notifications",
                        {
                            "title": title,
                            "message": message,
                            "notification_type": notification_type,
                            "status": status,
                        },
                    )
                )

    if not notifications.empty:
        ui.section("Recent notifications")
        recent = notifications.sort_values("id", ascending=False) if "id" in notifications else notifications
        recent = recent.rename(
            columns={
                "title": "Title",
                "message": "Message",
                "notification_type": "Type",
                "status": "Status",
            }
        )
        ui.data_table(format_table(recent, ["Title", "Message", "Type", "Status"]), height=240)


def _sensor_form() -> None:
    ui.section("Register a sensor")
    with st.form("create_sensor", clear_on_submit=True, border=False):
        left, right = st.columns(2, gap="medium")
        sensor_name = left.text_input("Sensor name", placeholder="Required")
        location = right.text_input("Location")
        status = left.selectbox("Sensor status", ["Active", "Inactive", "Maintenance"])
        if st.form_submit_button("Add sensor", type="primary"):
            if not sensor_name.strip():
                st.error("Sensor name is required.")
            else:
                _submit(
                    *api.send_record(
                        "POST",
                        "sensors",
                        {"sensor_name": sensor_name, "location": location or None, "status": status},
                    )
                )
