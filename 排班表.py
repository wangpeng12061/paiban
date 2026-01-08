import streamlit as st
import random

# 1. 页面配置
st.set_page_config(page_title="王巨帅智能排班后台", layout="wide")

# 2. 颜色配置
color_config = {
    "丁泳池": {"bg": "#E3F2FD", "text": "#000"}, 
    "一一": {"bg": "#FCE4EC", "text": "#000"},   
    "刘文": {"bg": "#E8F5E9", "text": "#000"},   
    "泽文": {"bg": "#FFF9C4", "text": "#000"},   
    "思涵": {"bg": "#F3E5F5", "text": "#000"},   
    "雷雷": {"bg": "#E0F7FA", "text": "#000"},   
    "周志北": {"bg": "#F1F8E9", "text": "#000"}, 
    "陈曦": {"bg": "#FFF3E0", "text": "#000"},   
    "马邦君": {"bg": "#EFEBE9", "text": "#000"}, 
    "焦斌": {"bg": "#ECEFF1", "text": "#000"},   
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

# --- 核心算法优化：强力锁定位置 ---
def get_optimized_order(avail_list, last_evening_person=None, super_fixed_morn=None, super_fixed_eve=None, never_evening=None):
    if not avail_list: return []
    
    # 1. 确定晚班 (刘文、焦斌只要在，就固定晚班)
    final_eve = None
    fixed_eve_cands = [p for p in avail_list if p in (super_fixed_eve or [])]
    if fixed_eve_cands:
        final_eve = fixed_eve_cands[0] # 锁定晚班
    else:
        # 没固定的人在，就选非限制名单里的
        eve_cands = [p for p in avail_list if p not in (never_evening or [])]
        final_eve = random.choice(eve_cands) if eve_cands else avail_list[-1]
    
    # 2. 确定早班 (丁泳池只要在，就固定早班，但需避开晚接早)
    remaining = [p for p in avail_list if p != final_eve]
    if not remaining: return [final_eve]
    
    final_morn = None
    fixed_morn_cands = [p for p in remaining if p in (super_fixed_morn or [])]
    
    # 这里的关键：如果固定早班的人是昨天的晚班，强制踢出早班名单
    morn_pool = [p for p in fixed_morn_cands if p != last_evening_person]
    
    if morn_pool:
        final_morn = morn_pool[0]
    else:
        # 没有固定早班或丁泳池需要避开晚接早，就在剩下人里找
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
        
        # 主播：刘文固定晚班，一一思涵不晚班
        ord_h = get_optimized_order(avail_h, last_evening_person=last_h_eve, 
                                   super_fixed_eve=["刘文"], 
                                   never_evening=["一一", "思涵"])
        
        # 场控：丁泳池固定早班，焦斌固定晚班，陈曦不晚班
        ord_s = get_optimized_order(avail_s, last_evening_person=last_s_eve, 
                                   super_fixed_morn=["丁泳池"], 
                                   super_fixed_eve=["焦斌"], 
                                   never_evening=["陈曦"])
        
        if ord_h: last_h_eve = ord_h[-1]
        if ord_s: last_s_eve = ord_s[-1]
        
        weekly_data[day] = {"主播": get_grid_data(ord_h), "场控": get_grid_data(ord_s)}

    # --- HTML 渲染 (名字黑色加粗加大) ---
    html = """<style>
        .main-table { width: 100%; border-collapse: collapse; text-align: center; color: #333; }
        .main-table th, .main-table td { border: 2px solid #444; padding: 10px; }
        .header-row { background-color: #f2f2f2; font-weight: bold; }
        .time-col { background-color: #ffffff; width: 100px; font-weight: bold; border-right: 3px solid #000; font-size: 14px; }
        .name-cell { color: #000000 !important; font-weight: 900 !important; font-size: 20px !important; display: block; }
    </style><table class='main-table'>"""

    # 1. 休息区
    html += "<tr class='header-row'><th style='width:90px;'>人员状态</th>"
    for day in days: html += f"<th colspan='2'>{day}</th>"
    html += "</tr>"
    for p in all_members:
        s = color_config.get(p, {"bg": "#fff"})
        html += f"<tr><td style='background:{s['bg']}; font-weight:bold;'>{p}</td>"
        for day in days:
            is_off = p in off_data[day]["h"] or p in off_data[day]["s"]
            bg, content = (s['bg'], f"<span class='name-cell'>{p}</span>") if is_off else ("#fff", "")
            html += f"<td colspan='2' style='background:{bg};'>{content}</td>"
        html += "</tr>"

    html += "<tr><td colspan='15' style='background:#444; height:8px; border:none;'></td></tr>"

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
