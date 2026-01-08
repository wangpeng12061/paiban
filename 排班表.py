import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="清爽版智能排班系统", layout="wide")

# 1. 精心调制的“清爽莫兰迪”配色方案 (去掉了原本沉重的深色)
color_config = {
    "丁泳池": {"bg": "#E1F5FE", "text": "#01579B"}, # 清透蓝
    "一一": {"bg": "#F3E5F5", "text": "#4A148C"},   # 柔和紫
    "刘文": {"bg": "#E8F5E9", "text": "#1B5E20"},   # 薄荷绿
    "泽文": {"bg": "#FFFDE7", "text": "#F57F17"},   # 奶油黄
    "思涵": {"bg": "#FCE4EC", "text": "#880E4F"},   # 樱花粉
    "雷雷": {"bg": "#E0F2F1", "text": "#004D40"},   # 湖水绿
    "周志北": {"bg": "#F1F8E9", "text": "#33691E"}, # 抹茶绿
    "陈曦": {"bg": "#FFF3E0", "text": "#E65100"},   # 晚霞橙
    "马邦君": {"bg": "#ECEFF1", "text": "#263238"}, # 奶灰色
    "焦斌": {"bg": "#EFEBE9", "text": "#3E2723"},   # 亚麻色
    "——": {"bg": "#FFFFFF", "text": "#DFDFDF"},     # 纯白留空
    "无人上班": {"bg": "#FFFFFF", "text": "#DFDFDF"}
}

all_hosts = ["一一", "思涵", "刘文", "雷雷", "泽文"]
all_staffs = ["马邦君", "丁泳池", "陈曦", "周志北", "焦斌"]
days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

st.title("🌿 直播间 16H 排班 (清爽高级版)")

# --- 第一步：设置休息名单 ---
st.subheader("🛌 第一步：设置人员休息")
off_data = {}
cols_off = st.columns(7)
for i, day in enumerate(days):
    with cols_off[i]:
        st.markdown(f"**{day}**")
        h_off = st.multiselect(f"主播休", all_hosts, key=f"h_{day}")
        s_off = st.multiselect(f"场控休", all_staffs, key=f"s_{day}")
        off_data[day] = {"h": h_off, "s": s_off}

st.divider()

# --- 核心逻辑 ---
def get_optimized_order(avail_list, morning_pref=None, evening_pref=None):
    if not avail_list: return []
    mornings = [p for p in avail_list if p in (morning_pref or [])]
    evenings = [p for p in avail_list if p in (evening_pref or [])]
    others = [p for p in avail_list if p not in mornings and p not in evenings]
    random.shuffle(others)
    return mornings + others + evenings

def get_grid_data(ordered_list):
    if not ordered_list: return ["——"] * 16
    grid = []
    duration = 16 / len(ordered_list)
    for i in range(16):
        idx = int(i // duration)
        if idx >= len(ordered_list): idx = len(ordered_list) - 1
        grid.append(ordered_list[idx])
    return grid

# --- 第二步：生成排班 ---
if st.button("✨ 生成清爽排班看板", use_container_width=True):
    time_index = [f"{h:02d}:00-{(h+1):02d}:00" for h in range(8, 24)]
    weekly_data = {}

    for day in days:
        avail_h = [h for h in all_hosts if h not in off_data[day]["h"]]
        avail_s = [s for s in all_staffs if s not in off_data[day]["s"]]
        
        ordered_h = get_optimized_order(avail_h, morning_pref=[], evening_pref=["刘文"])
        ordered_s = get_optimized_order(avail_s, morning_pref=["丁泳池"], evening_pref=["焦斌"])
        
        weekly_data[day] = {
            "主播": get_grid_data(ordered_h),
            "场控": get_grid_data(ordered_s)
        }

    # --- HTML 渲染 ---
    html = """
    <style>
        .schedule-table { width: 100%; border-collapse: collapse; text-align: center; border: 1px solid #E0E0E0; }
        .schedule-table th { background-color: #F5F5F5; border: 1px solid #E0E0E0; padding: 10px; color: #616161; font-size: 14px; }
        .schedule-table td { border: 1px solid #E0E0E0; padding: 8px; font-size: 14px; }
        .time-col { background-color: #FFFFFF; color: #9E9E9E; width: 110px; font-family: monospace; }
    </style>
    <table class="schedule-table">
    """
    
    html += "<tr><th rowspan='2' class='time-col'>时间</th>"
    for day in days: html += f"<th colspan='2'>{day}</th>"
    html += "</tr><tr>"
    for _ in days: html += "<th>主播</th><th>场控</th>"
    html += "</tr>"

    skip = {day: {"主播": 0, "场控": 0} for day in days}
    for i in range(16):
        html += f"<tr><td class='time-col'>{time_index[i]}</td>"
        for day in days:
            for role in ["主播", "场控"]:
                if skip[day][role] > 0:
                    skip[day][role] -= 1
                    continue
                
                name = weekly_data[day][role][i]
                rs = 1
                for j in range(i + 1, 16):
                    if weekly_data[day][role][j] == name: rs += 1
                    else: break
                skip[day][role] = rs - 1
                
                style = color_config.get(name, {"bg": "#FFFFFF", "text": "#000000"})
                html += f"<td rowspan='{rs}' style='background-color: {style['bg']}; color: {style['text']}; font-weight: 500;'>{name}</td>"
        html += "</tr>"
    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)
    st.balloons()