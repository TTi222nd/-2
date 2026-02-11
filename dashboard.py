from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=3000, key="refresh")
import os
import json
import pandas as pd
import streamlit as st
from PIL import Image


LOG_PATH = "events.jsonl"

st.set_page_config(page_title="Gate Vehicle Dashboard", layout="wide")
st.title("Gate Vehicle Dashboard (A→S = IN, S→A = OUT + Speed)")

rows = []
if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass

if not rows:
    st.info("ยังไม่มีข้อมูล — รัน counter_two_lines.py ให้เกิด event อย่างน้อย 1 ครั้งก่อน")
    st.stop()

df = pd.DataFrame(rows)

# แปลง speed_kmh ให้เป็นตัวเลข (ถ้ามี)
if "speed_kmh" in df.columns:
    df["speed_kmh"] = pd.to_numeric(df["speed_kmh"], errors="coerce")

# เรียงล่าสุดก่อน
df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)
latest = df.iloc[0]

# Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("IN", int(latest.get("count_in", 0)))
c2.metric("OUT", int(latest.get("count_out", 0)))
c3.metric("NET (IN-OUT)", int(latest.get("count_in", 0)) - int(latest.get("count_out", 0)))

# ความเร็วล่าสุด (ถ้ามี)
latest_speed = latest.get("speed_kmh", None)
if pd.notna(latest_speed):
    c4.metric("Latest Speed (km/h)", f"{float(latest_speed):.1f}")
else:
    c4.metric("Latest Speed (km/h)", "-")

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Latest Events")

    cols = ["timestamp", "direction", "track_id", "first_line", "second_line"]
    if "speed_kmh" in df.columns:
        cols.append("speed_kmh")

    # ปรับรูปแบบ speed ให้ดูง่าย
    view = df[cols].copy()
    if "speed_kmh" in view.columns:
        view["speed_kmh"] = view["speed_kmh"].map(lambda x: f"{x:.1f}" if pd.notna(x) else "")

    st.dataframe(view.head(100), use_container_width=True)

with right:
    st.subheader("Latest Captures (ล่าสุดก่อน)")

    shown = 0
    for i in range(len(df)):
        if shown >= 12:
            break

        img_path = df.loc[i].get("image", None)
        ts = df.loc[i].get("timestamp", "")
        direction = df.loc[i].get("direction", "")
        tid = df.loc[i].get("track_id", "")
        sp = df.loc[i].get("speed_kmh", None)

        caption = f"{ts} | {direction} | ID {tid}"
        if pd.notna(sp):
            caption += f" | {float(sp):.1f} km/h"

        st.caption(caption)

        if isinstance(img_path, str) and img_path and os.path.exists(img_path):
            st.image(Image.open(img_path), use_container_width=True)
            shown += 1
        else:
            st.write("(no image)")
            shown += 1
