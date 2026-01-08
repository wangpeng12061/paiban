import streamlit as st
import pandas as pd
import random

# 1. 页面配置
st.set_page_config(page_title="王巨帅智能排班后台-编辑版", layout="wide")

# 2. 颜色配置 (精准配色方案)
color_config = {
    "丁泳池": "#90CAF9", "一一": "#E3F2FD", "刘文": "#A5D6A7",
    "泽文": "#CE93D8", "思涵": "#F48FB1", "雷雷": "#F3E5F5",
    "周志北": "#C5E1A5", "陈曦": "#FFCC80", "马邦君": "#B0BEC5",
    "焦斌": "#66BB6A", "——": "#FFFFFF"
}

all_hosts = ["一一", "思涵", "刘文", "雷雷", "泽文"]
all_staffs = ["马邦君", "丁泳池", "陈曦", "周志北", "焦斌"]
all_members = all_hosts + all_staffs
days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

st.title("🤵‍♂️ 王巨帅智能排班后台 (可编辑版)")

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

# --- 核心算法 (逻辑不变) ---
def get_optimized_order(avail_list, last_evening_person=None, super_fixed_morn=None, super_fixed_eve=None, never_evening=None):
    if not avail_list: return []
    final_eve = None
    fixed_eve_cands = [p for p in avail_list if p in (super_fixed_eve or [])]
    if fixed_eve_cands:
        final_eve = fixed_eve_cands[0]
    else:
        eve_cands = [p for p in avail_list if p not in (never_evening or [])]
        final_eve = random.choice(eve_cands) if eve_cands else avail_list[-1]
    
    remaining = [p for p in avail_list if p != final_eve]
    if not remaining: return [final_eve]
    
    final_morn = None
    fixed_morn_cands = [p for p in remaining if p in (super_fixed_morn or [])]
    morn_pool = [p for p in fixed_morn_cands if p != last_evening_person]
    if morn_pool:
        final_morn = morn_pool[0]
    else:
        morn_cands = [p for p in remaining if p != last_evening_person]
        final_morn = random.choice(morn_cands) if morn_cands else remaining[0]
        
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
if st.button("🚀 生成并编辑智能排班", use_container_width=True):
    time_index = [f"{h:02d}:00-{(h+1):02d}:00" for h in range(8, 24)]
    
    # 构建 DataFrame
    df_data = {"时间": time_index}
    last_h_eve, last_s_eve = None, None
    
    for day in days:
        avail_h = [h for h in all_hosts if h not in off_data[day]["h"]]
        avail_s = [s for s in all_staffs if s not in off_data[day]["s"]]
        
        ord_h = get_optimized_order(avail_h, last_h_eve, ["刘文"], None, ["一一", "思涵"])
        ord_s = get_optimized_order(avail_s, last_s_eve, ["丁泳池"], ["焦斌"], ["陈曦"])
        
        if ord_h: last_h_eve = ord_h[-1]
        if ord_s: last_s_eve = ord_s[-1]
        
        df_data[f"{day}(主播)"] = get_grid_data(ord_h)
        df_data[f"{day}(场控)"] = get_grid_data(ord_s)

    df = pd.DataFrame(df_data)

    st.subheader("📝 交互式排班表（点击单元格直接修改，名字加粗已内建）")
    st.info("💡 提示：双击名字可以修改，右侧有搜索和下载按钮。")

    # 使用 st.data_editor 实现编辑和自动上色
    def apply_color(val):
        color = color_config.get(val, "#FFFFFF")
        # 这里的 CSS 确保名字黑、大、粗
        return f'background-color: {color}; color: black; font-weight: 900; font-size: 18px;'

    styled_df = df.style.applymap(apply_color)

    edited_df = st.data_editor(
        styled_df,
        use_container_width=True,
        height=600,
        num_rows="fixed",
        column_config={
            "时间": st.column_config.TextColumn(width="medium", disabled=True),
        }
    )
    
    st.success("✅ 修改完成后，你可以直接截图或复制表格内容。")

# 休息状态展示区 (保持不可编辑，作为参考)
with st.expander("查看当前人员颜色对照"):
    cols = st.columns(len(all_members))
    for i, p in enumerate(all_members):
        cols[i].markdown(f"<div style='background:{color_config[p]}; padding:10px; border-radius:5px; text-align:center; color:black; font-weight:bold;'>{p}</div>", unsafe_allow_html=True)
