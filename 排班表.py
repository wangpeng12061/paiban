import streamlit as st
import random

# 1. 页面配置
st.set_page_config(page_title="王巨帅智能排班后台", layout="wide")

# 2. 颜色配置 (背景色保留，文字颜色在下方渲染时强制转黑)
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

# --- 核心算法（保持哥原来的逻辑不变） ---
def get_optimized_order(avail_list, last_evening_person=None, morning_pref=None, evening_pref=None, never_evening=None):
    if not avail_list: return []
    eve_cands = [p for p in avail_list if p not in (never_evening or [])]
    target_eve = [p for p in eve_cands if p in (evening_pref or [])]
    final_eve = target_eve[0] if target_eve else (random.choice(eve_cands) if eve_cands else avail_list[-1])
    
    rem_morn = [p for p in avail_list if p != final_eve]
    if not rem_morn: return [final_eve]
    morn_cands = [p for p in rem_morn if p != last_evening_person]
    if not morn_cands: morn_cands = rem_morn
    morn_pref_list = [p for p in morn_cands if p in (morning_pref or [])]
    final_morn = morn_pref_list[0] if morn_pref_list else random.choice(morn_cands)
    
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

# 第二步：生成看板
if st.button("🚀 生成智能排班看板", use_container_width=True):
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

    # --- HTML 渲染 (重点优化：人名全黑、加大、加粗) ---
    html = """<style>
        .main-table { width: 100%; border-collapse: collapse; text-align: center; color: #333; }
        .main-table th, .main-table td { border: 2px solid #444; padding: 10px; }
        .header-row { background-color: #f2f2f2; font-weight: bold; }
        .time-col { background-color: #ffffff; width: 100px; font-weight: bold; border-right: 3px solid #000; font-size: 14px; }
        .side-name { width: 90px; font-weight: 900; font-size: 16px; color: #000 !important; }
        /* 核心样式：强制名字黑、大、粗 */
        .name-cell { color: #000000 !important; font-weight: 900 !important; font-size: 18px !important; }
    </style><table class='main-table'>"""

    # 1. 休息区
    html += "<tr class='header-row'><th class='side-name'>人员状态</th>"
    for day in days: html += f"<th colspan='2'>{day}</th>"
    html += "</tr>"
    for p in all_members:
        s = color_config.get(p, {"bg": "#fff"})
        html += f"<tr><td class='side-name' style='background:{s['bg']};'>{p}</td>"
        for day in days:
            is_off = p in off_data[day]["h"] or p in off_data[day]["s"]
            bg, content = (s['bg'], f"<span class='name-cell'>{p}</span>") if is_off else ("#fff", "")
            html += f"<td colspan='2' style='background:{bg};'>{content}</td>"
        html += "</tr>"

    # 黑色分割隔离带
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
                # 应用强制加粗加黑样式
                html += f"<td rowspan='{rs}' style='background:{c['bg']};'><span class='name-cell'>{name}</span></td>"
        html += "</tr>"
    st.markdown(html + "</table>", unsafe_allow_html=True)
