"""
src/analytics.py — Mixpanel product telemetry client for Product Analytics.
Tracks high-level user engagement, funnels, and session depth without polluting event properties.
"""
import os
import streamlit as st

try:
    from mixpanel import Mixpanel
except ImportError:
    Mixpanel = None


def get_mixpanel():
    token = os.getenv("MIXPANEL_PROJECT_TOKEN", "").strip().replace('"', '').replace("'", "")
    if not token and hasattr(st, "secrets") and "MIXPANEL_PROJECT_TOKEN" in st.secrets:
        token = str(st.secrets["MIXPANEL_PROJECT_TOKEN"]).strip().replace('"', '').replace("'", "")
    if token and Mixpanel:
        return Mixpanel(token)
    return None


def track_event(distinct_id: str, event_name: str, properties: dict | None = None) -> None:
    """Send a product analytics event to Mixpanel safely."""
    mp = get_mixpanel()
    if not mp or not distinct_id:
        return
    props = properties.copy() if properties else {}
    props["user"] = distinct_id
    props["product"] = "lenny-product-assistant"
    try:
        mp.track(distinct_id=distinct_id, event_name=event_name, properties=props)
    except Exception as exc:
        print(f"[Mixpanel] Failed to send event {event_name}: {exc}")
