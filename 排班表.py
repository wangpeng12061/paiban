import streamlit as st
import random

# 1. 页面配置
st.set_page_config(page_title="直播间 16H 智能排班系统", layout="wide")

# 2. 颜色配置 (莫兰迪清爽色系)
color_config = {
    "丁泳池": {"bg": "#E1F5FE", "text": "#01579B"}, "一一": {"bg": "#F3E5F5", "text": "#4A148C"},
    "刘文": {"bg": "#E8F5E9", "text": "#1B5E20"}, "泽文": {"bg": "#FFFDE7", "text": "#F57F17"},
    "思涵": {"bg": "#FCE4EC", "text": "#880E4F"}, "雷雷": {"bg": "#E0F2F1", "text": "#004D40"},
    "周志北": {"bg": "#F1F8E9", "text": "#33691E"}, "陈曦": {"bg": "#FFF3E0", "text": "#E65100"},
    "马邦君": {"bg": "#ECEFF1", "text": "#263238"}, "焦斌": {"bg": "#EFEBE9", "text": "#3E2723"},
    "——": {"bg": "#FFFFFF", "text": "#DFDFDF"}
}

# 3. 初始名单
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

# --- 核心算法逻辑：加入“晚接早”规避 ---
def get_optimized_order(avail_list, last_evening_person=None, morning_pref=None, evening_pref=None):
    if not avail_list: return []
    
    # 规避晚接早：如果某人昨天是末班，从今天的早班候选（即列表第一个位置）中剔除
    can_be_first = [p for p in avail_list if p != last_evening_person]
    # 如果没得选（只有一个人），那就只能是他；如果有得选，就从候选人里挑第一个
    first_person = random.choice(can_be_first) if can_be_first else avail_list[0]
    
    # 确定剩余的人
    remaining = [p for p in avail_list if p != first_person]
    
    # 晚班优先处理
    final_evening = [p for p in remaining if p in (evening_pref or [])]
    others = [p for p in remaining if p not in final_evening]
    random.shuffle(others)
    
    return [first_person] + others + final_evening

def get_grid_data(ordered_list):
    if not ordered_list: return ["——"] * 16
    grid = []
    duration = 16 / len(ordered_list)
    for i in range(16):
        idx = min(int(i // duration), len(ordered_list) - 1)
        grid.append(ordered_list[idx])
    return grid

# 第二步：生成看板
if st.button("✨ 生成直观排班看板", use_container_width=True):
    time_index = [f"{h:02d}:00-{(h+1):02d}:00" for h in range(8, 24)]
    weekly_data = {}
    
    # 记录前一天的末班人员
    last_h_evening = None
    last_s_evening = None
    
    for day in days:
        avail_h = [h for h in all_hosts if h not in off_data[day]["h"]]
        avail_s = [s for s in all_staffs if s not in off_data[day]["s"]]
        
        # 应用逻辑：刘文优先晚班，丁泳池优先早班，且规避晚接早
        ordered_h = get_optimized_order(avail_h, last_evening_person=last_h_evening, evening_pref=["刘文"])
        ordered_s = get_optimized_order(avail_s, last_evening_person=last_s_evening, morning_pref=["丁泳池"], evening_pref=["焦斌"])
        
        # 记录今天谁排了最后一名，给明天参考
        last_h_evening = ordered_h[-1] if ordered_h else None
        last_s_evening = ordered_s[-1] if ordered_s else None
        
        weekly_data[day] = {"主播": get_grid_data(ordered_h), "场控": get_grid_data(ordered_s)}

    # --- HTML 渲染 ---
    html = """<style>
        .table-container { font-family: sans-serif; }
        .schedule-table { width: 100%; border-collapse: collapse; text-align: center; border: 1px solid #ddd; }
        .schedule-table th, .schedule-table td { border: 1px solid #ddd; padding: 6px; font-size: 13px; }
        .header-day { background-color: #f4f4f4; font-weight: bold; }
        .name-col { background-color: #fafafa; width: 100px; font-weight: bold; }
    </style><div class='table-container'><table class='schedule-table'>"""

    # 1. 顶部休息公示矩阵
    html += "<tr><th class='name-col'>休假安排</th>"
    for day in days: html += f"<th colspan='2' class='header-day'>{day}</th>"
    html += "</tr>"
    for person in all_members:
        style = color_config.get(person, {"bg": "#fff", "text": "#000"})
        html += f"<tr><td class='name-col' style='background:{style['bg']}; color:{style['text']};'>{person}</td>"
        for day in days:
            is_off = person in off_data[day]["h"] or person in off_data[day]["s"]
            if is_off:
                html += f"<td colspan='2' style='background:{style['bg']}; color:{style['text']}; font-weight:bold;'>{person}</td>"
            else:
                html += "<td colspan='2'></td>"
        html += "</tr>"

    html += "<tr><td colspan='15' style='background:#f0f0f0; height:10px;'></td></tr>"

    # 2. 排班表岗位头
    html += "<tr><th class='name-col'>时间</th>"
    for _ in days: html += "<th>主播</th><th>场控</th>"
    html += "</tr>"

    # 3. 排班表详细内容 (带自动合并)
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

    html += "</table></div>"
    st.markdown(html, unsafe_allow_html=True)
    st.info("💡 系统已自动开启“晚接早”保护：前一天最后班次人员不会排在次日首班。")
