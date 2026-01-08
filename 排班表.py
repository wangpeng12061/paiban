import streamlit as st
import random

# 1. 页面配置
st.set_page_config(page_title="王巨帅智能排班后台", layout="wide")

# 2. 颜色配置 (高饱和度、强区分度)
color_config = {
    "丁泳池": {"bg": "#90CAF9", "text": "#000"}, # 鲜亮蓝
    "一一": {"bg": "#F48FB1", "text": "#000"},   # 亮珊瑚粉
    "刘文": {"bg": "#A5D6A7", "text": "#000"},   # 翠绿
    "泽文": {"bg": "#FFF59D", "text": "#000"},   # 亮黄
    "思涵": {"bg": "#CE93D8", "text": "#000"},   # 明紫
    "雷雷": {"bg": "#80DEEA", "text": "#000"},   # 亮青
    "周志北": {"bg": "#C5E1A5", "text": "#000"}, # 嫩绿
    "陈曦": {"bg": "#FFCC80", "text": "#000"},   # 亮橙
    "马邦君": {"bg": "#BCAAA4", "text": "#000"}, # 浅褐
    "焦斌": {"bg": "#B0BEC5", "text": "#000"},   # 蓝灰
    "——": {"bg": "#FFFFFF", "text": "#DFDFDF"}
}

all_hosts = ["一一", "思涵", "刘文", "雷雷", "泽文"]
all_staffs = ["马邦君", "丁泳池", "陈曦", "周志北", "焦斌"]
all_members = all_hosts + all_staffs
days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# --- 顶栏 ---
st.title("🤵‍♂️ 王巨帅智能排班后台")

# 第一步：设置休息
st.subheader("⚙️ 第一步：同步休假安排")
off_data = {}
cols_off = st.columns(7)
for i, day in enumerate(days):
    with cols_off[i]:
        st.markdown(f"**{day}**")
        h_off = st.multiselect(f"主播休", all_hosts, key=f"h_{day}")
        s_off = st.multiselect(f"场控休", all_staffs, key=f"s_{day}")
        off_data[day] = {"h": h_off, "s": s_off}

st.divider()

# --- 核心算法：强力锁定 + 晚接早规避 ---
def get_optimized_order(avail_list, last_evening_person=None, super_fixed_morn=None, super_fixed_eve=None, never_evening=None):
    if not avail_list: return []
    
    # 1. 强行锁定晚班
    final_eve = None
    fixed_eve_cands = [p for p in avail_list if p in (super_fixed_eve or [])]
    if fixed_eve_cands:
        final_eve = fixed_eve_cands[0]
    else:
        eve_cands = [p for p in avail_list if p not in (never_evening or [])]
        final_eve = random.choice(eve_cands) if eve_cands else avail_list[-1]
    
    # 2. 强行锁定早班
    remaining = [p for p in avail_list if p != final_eve]
    if not remaining: return [final_eve]
    
    final_morn = None
    fixed_morn_cands = [p for p in remaining if p in (super_fixed_morn or [])]
    
    # 规避晚接早：如果锁定人是昨晚下班的，今天他不能排早班
    morn_pool = [p for p in fixed_morn_cands if p != last_evening_person]
    
    if morn_pool:
        final_morn = morn_pool[0]
    else:
        morn_cands = [p for p in remaining if p != last_evening_person]
        final_morn = random.choice(morn_cands) if morn_cands else remaining[0]
        
    # 3. 填充中间
    mid = [p for p in remaining if p != final_morn]
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

# 第二步：生成看板
if st.button("🚀 生成智能排班看板", use_container_width=True):
    time_index = [f"{h:02d}:00-{(h+1):02d}:00" for h in range(8, 24)]
    weekly_data = {}
    last_h_eve, last_s_eve = None, None
    
    for day in days:
        avail_h = [h for h in all_hosts if h not in off_data[day]["h"]]
        avail_s = [s for s in all_staffs if s not in off_data[day]["s"]]
        
        ord_h = get_optimized_order(avail_h, last_evening_person=last_h_eve, 
                                   super_fixed_eve=["刘文"], 
                                   never_evening=["一一", "思涵"])
        
        ord_s = get_optimized_order(avail_s, last_evening_person=last_s_eve, 
                                   super_fixed_morn=["丁泳池"], 
                                   super_fixed_eve=["焦斌"], 
                                   never_evening=["陈曦"])
        
        if ord_h: last_h_eve = ord_h[-1]
        if ord_s: last_s_eve = ord_s[-1]
        weekly_data[day] = {"主播": get_grid_data(ord_h), "场控": get_grid_data(ord_s)}

    # --- HTML 渲染 (颜色加深，名字极致黑) ---
    html = """<style>
        .main-table { width: 100%; border-collapse: collapse; text-align: center; }
        .main-table th, .main-table td { border: 2.5px solid #333; padding: 12px; }
        .header-row { background-color: #DDD; font-weight: bold; }
        .time-col { background-color: #f9f9f9; width: 100px; font-weight: 900; border-right: 4px solid #000; font-size: 15px; }
        .name-cell { color: #000000 !important; font-weight: 900 !important; font-size: 22px !important; display: block; text-shadow: 0.5px 0.5px 0px #fff; }
    </style><table class='main-table'>"""

    # 1. 休息区
    html += "<tr class='header-row'><th style='width:90px;'>人员状态</th>"
    for day in days: html += f"<th colspan='2'>{day}</th>"
    html += "</tr>"
    for p in all_members:
        s = color_config.get(p, {"bg": "#fff"})
        html += f"<tr><td style='background:{s['bg']}; font-weight:900; font-size:16px;'>{p}</td>"
        for day in days:
            is_off = p in off_data[day]["h"] or p in off_data[day]["s"]
            bg, content = (s['bg'], f"<span class='name-cell'>{p}</span>") if is_off else ("#fff", "")
            html += f"<td colspan='2' style='background:{bg};'>{content}</td>"
        html += "</tr>"

    html += "<tr><td colspan='15' style='background:#000; height:10px; border:none;'></td></tr>"

    # 2. 排班区
    html += "<tr class='header-row'><th class='time-col'>时间</th>"
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
                c = color_config.get(name, {"bg": "#fff"})
                html += f"<td rowspan='{rs}' style='background:{c['bg']};'><span class='name-cell'>{name}</span></td>"
        html += "</tr>"
    st.markdown(html + "</table>", unsafe_allow_html=True)
