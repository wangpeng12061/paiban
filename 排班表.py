import streamlit as st
import random

# 1. 页面基础配置
st.set_page_config(page_title="直播间 16H 智能排班", layout="wide")

# 2. 莫兰迪清爽配色配置
color_config = {
    "丁泳池": {"bg": "#E1F5FE", "text": "#01579B"}, "一一": {"bg": "#F3E5F5", "text": "#4A148C"},
    "刘文": {"bg": "#E8F5E9", "text": "#1B5E20"}, "泽文": {"bg": "#FFFDE7", "text": "#F57F17"},
    "思涵": {"bg": "#FCE4EC", "text": "#880E4F"}, "雷雷": {"bg": "#E0F2F1", "text": "#004D40"},
    "周志北": {"bg": "#F1F8E9", "text": "#33691E"}, "陈曦": {"bg": "#FFF3E0", "text": "#E65100"},
    "马邦君": {"bg": "#ECEFF1", "text": "#263238"}, "焦斌": {"bg": "#EFEBE9", "text": "#3E2723"},
    "——": {"bg": "#FFFFFF", "text": "#DFDFDF"}
}

all_hosts = ["一一", "思涵", "刘文", "雷雷", "泽文"]
all_staffs = ["马邦君", "丁泳池", "陈曦", "周志北", "焦斌"]
days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

st.title("🌿 直播间 16H 智能排班系统")

# --- 新增优化：今日休息名单展示区 ---
st.markdown("### 🛌 今日休息人员公示")
off_container = st.container() # 创建一个容器，稍后填入内容

st.divider()

# 第一步：设置休息
st.subheader("⚙️ 第一步：设置人员休息")
off_data = {}
cols_off = st.columns(7)
all_off_names = {day: [] for day in days} # 记录每天休息的人

for i, day in enumerate(days):
    with cols_off[i]:
        st.markdown(f"**{day}**")
        h_off = st.multiselect(f"主播休", all_hosts, key=f"h_{day}")
        s_off = st.multiselect(f"场控休", all_staffs, key=f"s_{day}")
        off_data[day] = {"h": h_off, "s": s_off}
        all_off_names[day] = h_off + s_off

# 在最顶部的容器中显示今日休息人员（以当前排班表选中的第一天为例，或您可以手动切换）
with off_container:
    # 这里我们显示一周内所有有休息安排的人员
    for day in days:
        if all_off_names[day]:
            names_str = " | ".join([f"**{n}**" for n in all_off_names[day]])
            st.info(f"📅 **{day} 休息：** {names_str}")
    if not any(all_off_names.values()):
        st.write("✨ 今日全员勤奋工作中，无人休息！")

st.divider()

# 排班核心逻辑
def get_grid_data(ordered_list):
    if not ordered_list: return ["——"] * 16
    grid = []
    duration = 16 / len(ordered_list)
    for i in range(16):
        idx = min(int(i // duration), len(ordered_list) - 1)
        grid.append(ordered_list[idx])
    return grid

# 第二步：生成可视化看板
if st.button("✨ 生成清爽排班看板", use_container_width=True):
    time_index = [f"{h:02d}:00-{(h+1):02d}:00" for h in range(8, 24)]
    weekly_data = {}
    for day in days:
        avail_h = [h for h in all_hosts if h not in off_data[day]["h"]]
        avail_s = [s for s in all_staffs if s not in off_data[day]["s"]]
        random.shuffle(avail_h)
        random.shuffle(avail_s)
        weekly_data[day] = {"主播": get_grid_data(avail_h), "场控": get_grid_data(avail_s)}

    # HTML 渲染逻辑
    html = """<style>
        .schedule-table { width: 100%; border-collapse: collapse; text-align: center; border: 1px solid #E0E0E0; }
        .schedule-table th { background-color: #F8F9FA; border: 1px solid #E0E0E0; padding: 10px; font-size: 14px; }
        .schedule-table td { border: 1px solid #E0E0E0; padding: 8px; font-size: 14px; }
    </style><table class='schedule-table'>"""
    
    # 表头
    html += "<tr><th rowspan='2'>时间</th>"
    for day in days: html += f"<th colspan='2'>{day}</th>"
    html += "</tr><tr>"
    for _ in days: html += "<th>主播</th><th>场控</th>"
    html += "</tr>"

    # 表身（合并单元格逻辑）
    skip = {day: {"主播": 0, "场控": 0} for day in days}
    for i in range(16):
        html += f"<tr><td style='background:#f9f9f9;'>{time_index[i]}</td>"
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
                html += f"<td rowspan='{rs}' style='background:{style['bg']}; color:{style['text']}; font-weight:bold;'>{name}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)
