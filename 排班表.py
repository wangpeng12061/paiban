import streamlit as st
import random

# 1. 页面配置
st.set_page_config(page_title="王巨帅智能排班后台", layout="wide")

# 2. 颜色配置 (莫兰迪清爽色系)
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
all_members = all_hosts + all_staffs
days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# --- 顶栏设置 ---
st.title("🤵‍♂️ 王巨帅智能排班后台")
st.markdown("<p style='color: #666; font-size: 0.9em;'>核心逻辑：丁泳池首班固定 | 刘文/焦斌末班固定 | 一一/思涵/陈曦避开晚班 | 强制规避晚接早</p>", unsafe_allow_html=True)

# 第一步：设置休息
st.subheader("⚙️ 第一步：人员休假同步")
off_data = {}
cols_off = st.columns(7)
for i, day in enumerate(days):
    with cols_off[i]:
        st.markdown(f"**{day}**")
        h_off = st.multiselect(f"主播休", all_hosts, key=f"h_{day}")
        s_off = st.multiselect(f"场控休", all_staffs, key=f"s_{day}")
        off_data[day] = {"h": h_off, "s": s_off}

st.divider()

# --- 核心算法逻辑 ---
def get_optimized_order(avail_list, last_evening_person=None, morning_pref=None, evening_pref=None, never_evening=None):
    if not avail_list: return []
    
    # 挑选晚班（避开限制名单）
    evening_candidates = [p for p in avail_list if p not in (never_evening or [])]
    target_evening = [p for p in evening_candidates if p in (evening_pref or [])]
    
    if target_evening:
        final_eve = target_evening[0]
    elif evening_candidates:
        final_eve = random.choice(evening_candidates)
    else:
        final_eve = avail_list[-1]

    # 挑选早班（规避晚接早，优先指定人）
    rem_for_morning = [p for p in avail_list if p != final_eve]
    if not rem_for_morning: return [final_eve]
    
    morn_candidates = [p for p in rem_for_morning if p != last_evening_person]
    if not morn_candidates: morn_candidates = rem_for_morning
    
    morn_pref_list = [p for p in morn_candidates if p in (morning_pref or [])]
    final_morn = morn_pref_list[0] if morn_pref_list else random.choice(morn_candidates)

    # 填充中间
    mid = [p for p in avail_list if p != final_morn and p != final_eve]
    random.shuffle(mid)
    return [final_morn] + mid + [final_eve]

def get_grid_data(ordered_list):
    if not ordered_list: return ["——"] * 16
    grid = []
    duration = 16 / len(ordered_list)
    for i in range(16):
        idx = min(int(i // duration), len(ordered_list) - 1)
        grid.append(ordered_list[idx])
    return grid

# 第二步：生成可视化看板
if st.button("🚀 开启智能排班并生成看板", use_container_width=True):
    time_index = [f"{h:02d}:00-{(h+1):02d}:00" for h in range(8, 24)]
    weekly_data = {}
    last_h, last_s = None, None
    
    for day in days:
        avail_h = [h for h in all_hosts if h not in off_data[day]["h"]]
        avail_s = [s for s in all_staffs if s not in off_data[day]["s"]]
        
        ord_h = get_optimized_order(avail_h, last_h, evening_pref=["刘文"], never_evening=["一一", "思涵"])
        ord_s = get_optimized_order(avail_s, last_s, morning_pref=["丁泳池"], evening_pref=["焦斌"], never_evening=["陈曦"])
        
        last_h, last_s = ord_h[-1], ord_s[-1]
        weekly_data[day] = {"主播": get_grid_data(ord_h), "场控": get_grid_data(ord_s)}

    # --- HTML 排版渲染 ---
    html = """<style>
        .schedule-table { width: 100%; border-collapse: collapse; text-align: center; border: 1px solid #eee; }
        .schedule-table th, .schedule-table td { border: 1px solid #eee; padding: 10px; font-size: 13px; }
        .header-day { background-color: #fcfcfc; font-weight: bold; color: #333; }
        .name-col { background-color: #ffffff; width: 90px; font-weight: bold; }
    </style><table class='schedule-table'>"""

    # 1. 休息区 (紧凑型)
    html += "<tr><th class='name-col'>休假状态</th>"
    for day in days: html += f"<th colspan='2' class='header-day'>{day}</th>"
    html += "</tr>"
    for p in all_members:
        s = color_config.get(p, {"bg": "#fff", "text": "#000"})
        html += f"<tr><td class='name-col' style='background:{s['bg']}; color:{s['text']};'>{p}</td>"
        for day in days:
            is_off = p in off_data[day]["h"] or p in off_data[day]["s"]
            bg, txt, content = (s['bg'], s['text'], f"<b>{p}</b>") if is_off else ("#fff", "#fff", "")
            html += f"<td colspan='2' style='background:{bg}; color:{txt}; border-bottom: 1px solid #f9f9f9;'>{content}</td>"
        html += "</tr>"

    html += "<tr><td colspan='15' style='background:#f7f7f7; height:12px; border:none;'></td></tr>"

    # 2. 排班区
    html += "<tr><th class='name-col'>时间</th>"
    for _ in days: html += "<th>主播</th><th>场控</th>"
    html += "</tr>"

    skip = {day: {"主播": 0, "场控": 0} for day in days}
    for i in range(16):
        html += f"<tr><td class='name-col' style='color:#bbb; font-weight: normal;'>{time_index[i]}</td>"
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
                c = color_config.get(name, {"bg": "#fff", "text": "#000"})
                html += f"<td rowspan='{rs}' style='background:{c['bg']}; color:{c['text']}; font-weight:bold;'>{name}</td>"
        html += "</tr>"
    st.markdown(html + "</table>", unsafe_allow_html=True)
