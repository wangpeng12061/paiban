import streamlit as st
import random

# 1. 页面配置
st.set_page_config(page_title="直播间 16H 智能排班系统", layout="wide")

# 2. 颜色配置
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

st.title("🌿 直播间 16H 智能排班系统")

# 第一步：设置休息
st.subheader("⚙️ 第一步：设置人员休息")
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
    
    # 1. 确定晚班人选 (排除 never_evening 名单)
    final_evening_person = None
    evening_candidates = [p for p in avail_list if p not in (never_evening or [])]
    
    # 优先选指定晚班人 (如 刘文/焦斌)
    target_evening = [p for p in evening_candidates if p in (evening_pref or [])]
    if target_evening:
        final_evening_person = target_evening[0]
    elif evening_candidates:
        final_evening_person = random.choice(evening_candidates)
    else:
        # 兜底逻辑：如果全员都在 never_evening 名单，则从可用人员中挑最后一个
        final_evening_person = avail_list[-1]

    # 2. 确定早班人选 (规避昨晚末班 + 优先指定人选)
    remaining_for_morning = [p for p in avail_list if p != final_evening_person]
    if not remaining_for_morning: 
        return [final_evening_person]

    morning_candidates = [p for p in remaining_for_morning if p != last_evening_person]
    if not morning_candidates: 
        morning_candidates = remaining_for_morning 
    
    morning_pref_list = [p for p in morning_candidates if p in (morning_pref or [])]
    if morning_pref_list:
        final_morning_person = morning_pref_list[0]
    else:
        final_morning_person = random.choice(morning_candidates)

    # 3. 填充中间位置
    middle_people = [p for p in avail_list if p != final_morning_person and p != final_evening_person]
    random.shuffle(middle_people)
    
    return [final_morning_person] + middle_people + [final_evening_person]

def get_grid_data(ordered_list):
    if not ordered_list: return ["——"] * 16
    grid = []
    duration = 16 / len(ordered_list)
    for i in range(16):
        idx = min(int(i // duration), len(ordered_list) - 1)
        grid.append(ordered_list[idx])
    return grid

# 第二步：生成看板
if st.button("✨ 生成排班看板", use_container_width=True):
    time_index = [f"{h:02d}:00-{(h+1):02d}:00" for h in range(8, 24)]
    weekly_data = {}
    last_h_eve = None
    last_s_eve = None
    
    for day in days:
        avail_h = [h for h in all_hosts if h not in off_data[day]["h"]]
        avail_s = [s for s in all_staffs if s not in off_data[day]["s"]]
        
        # 主播排班：刘文末班优先；一一、思涵永不末班
        ordered_h = get_optimized_order(avail_h, last_evening_person=last_h_eve, 
                                        evening_pref=["刘文"], 
                                        never_evening=["一一", "思涵"])
        
        # 场控排班：丁泳池首班优先；焦斌末班优先；陈曦永不末班
        ordered_s = get_optimized_order(avail_s, last_evening_person=last_s_eve, 
                                        morning_pref=["丁泳池"], 
                                        evening_pref=["焦斌"], 
                                        never_evening=["陈曦"])
        
        last_h_eve = ordered_h[-1] if ordered_h else None
        last_s_eve = ordered_s[-1] if ordered_s else None
        weekly_data[day] = {"主播": get_grid_data(ordered_h), "场控": get_grid_data(ordered_s)}

    # --- HTML 渲染 ---
    html = """<style>
        .schedule-table { width: 100%; border-collapse: collapse; text-align: center; border: 1px solid #ddd; }
        .schedule-table th, .schedule-table td { border: 1px solid #ddd; padding: 6px; font-size: 13px; }
        .header-day { background-color: #f4f4f4; font-weight: bold; }
        .name-col { background-color: #fafafa; width: 100px; font-weight: bold; }
    </style><div class='table-container'><table class='schedule-table'>"""

    # 休息公示区
    html += "<tr><th class='name-col'>休假安排</th>"
    for day in days: html += f"<th colspan='2' class='header-day'>{day}</th>"
    html += "</tr>"
    for person in all_members:
        s = color_config.get(person, {"bg": "#fff", "text": "#000"})
        html += f"<tr><td class='name-col' style='background:{s['bg']}; color:{s['text']};'>{person}</td>"
        for day in days:
            is_off = person in off_data[day]["h"] or person in off_data[day]["s"]
            bg = s['bg'] if is_off else '#fff'
            text_color = s['text'] if is_off else '#fff'
            content = f"<b>{person}</b>" if is_off else ""
            html += f"<td colspan='2' style='background:{bg}; color:{text_color};'>{content}</td>"
        html += "</tr>"

    html += "<tr><td colspan='15' style='background:#f0f0f0; height:12px;'></td></tr>"
    html += "<tr><th class='name-col'>时间</th>"
    for _ in days: html += "<th>主播</th><th>场控</th>"
    html += "</tr>"

    skip = {day: {"主播": 0, "场控": 0} for day in days}
    for i in range(16):
        html += f"<tr><td class='name-col' style='color:#888;'>{time_index[i]}</td>"
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
                st_color = color_config.get(name, {"bg": "#FFFFFF", "text": "#000000"})
                html += f"<td rowspan='{rs}' style='background:{st_color['bg']}; color:{st_color['text']}; font-weight:600;'>{name}</td>"
        html += "</tr>"
    st.markdown(html + "</table></div>", unsafe_allow_html=True)
    st.success("✅ 逻辑已更新：一一、思涵、陈曦 均已排除在晚班之外。")
