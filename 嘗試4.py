# %%
import streamlit as st
import random
import pandas as pd
import os

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="成大美食導航 NCKU Foodie", page_icon="🍱", layout="centered")

# 設定資料檔案
DATA_FILE = "restaurants_v2.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE).to_dict('records')
        except:
            return []
    # 預設初始資料
    return [
        {"name": "元味屋", "price": 150, "rating": 4.5},
        {"name": "成大館", "price": 100, "rating": 4.0},
        {"name": "麥當勞", "price": 120, "rating": 4.2},
        {"name": "活力小廚", "price": 80, "rating": 4.3}
    ]

def save_data(data):
    pd.DataFrame(data).to_csv(DATA_FILE, index=False)

# 初始化資料庫
if 'restaurant_db' not in st.session_state:
    st.session_state.restaurant_db = load_data()

# --- 2. 側邊欄：篩選與介紹 ---
with st.sidebar:
    st.title("🍔 搜尋過濾")
    budget = st.slider("💰 預算上限", 0, 500, 200, 10)
    min_rating = st.slider("⭐ 最低評分要求", 0.0, 5.0, 3.5, 0.1)
    
    st.divider()
    st.info("💡 **提示：** 這是由成大學生共同維護的美食名單。歡迎點擊下方「新增」按鈕貢獻你的口袋名單！")
    
    # 管理員隱藏後台 (只有你知道密碼)
    with st.expander("🔐 管理員入口"):
        admin_pw = st.text_input("請輸入管理密碼", type="password")
        if admin_pw == "ncku666": # 你可以自行修改此密碼
            if st.button("🚨 清空資料庫 (慎用)"):
                st.session_state.restaurant_db = []
                save_data([])
                st.success("資料已清空")
                st.rerun()

# --- 3. 主頁面標題 ---
st.title("🍴 成大生今天吃什麼？")
st.caption("專為成大校園設計的隨機餐廳挑選器")

# --- 4. 隨機抽選區 ---
st.divider()
if st.button("🚀 幫我選一家！", type="primary", use_container_width=True):
    # 邏輯過濾
    filtered_list = [
        res for res in st.session_state.restaurant_db 
        if int(res['price']) <= budget and float(res['rating']) >= min_rating
    ]
    
    if filtered_list:
        selected = random.choice(filtered_list)
        st.balloons()
        
        # 顯示美觀的結果框
        st.success(f"### 🎊 推薦你吃：**{selected['name']}**")
        col1, col2 = st.columns(2)
        col1.metric("預估消費", f"${selected['price']}")
        col2.metric("推薦指數", f"⭐ {selected['rating']}")
        
        # Google 地圖連結
        map_url = f"https://www.google.com/maps/search/?api=1&query={selected['name']}+成大"
        st.markdown(f"**[📍 點我開啟 Google 地圖導航]({map_url})**")
    else:
        st.error(f"抱歉！在 ${budget} 元以內且評分 > {min_rating} 的餐廳中找不到結果。試著放寬條件吧！")

# --- 5. 新增餐廳功能 ---
st.divider()
st.subheader("📝 貢獻新餐廳")
with st.form("add_restaurant_form", clear_on_submit=True):
    name = st.text_input("餐廳名稱 (必填)", placeholder="例如：元味屋")
    c1, c2 = st.columns(2)
    price = c1.number_input("平均價位 ($)", min_value=0, value=150, step=10)
    rating = c2.slider("個人評分", 0.0, 5.0, 4.0, 0.1)
    
    submitted = st.form_submit_button("✅ 提交餐廳資料", use_container_width=True)
    if submitted:
        if name:
            new_entry = {"name": name, "price": int(price), "rating": float(rating)}
            st.session_state.restaurant_db.append(new_entry)
            save_data(st.session_state.restaurant_db)
            st.toast(f"感謝貢獻！{name} 已加入清單！", icon='🎉')
            st.rerun()
        else:
            st.warning("請至少輸入餐廳名稱喔！")

# --- 6. 數據統計與展示 ---
st.divider()
st.subheader("📊 校園美食數據")
if st.session_state.restaurant_db:
    df = pd.DataFrame(st.session_state.restaurant_db)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("收錄餐廳", f"{len(df)} 間")
    m2.metric("平均消費", f"${int(df['price'].mean())}")
    m3.metric("總平均分", f"⭐ {df['rating'].mean():.1f}")
    
    with st.expander("📂 查看完整清單 (可排序)"):
        st.dataframe(
            df, 
            column_config={
                "name": "餐廳名稱",
                "price": st.column_config.NumberColumn("價位", format="$%d"),
                "rating": st.column_config.NumberColumn("評分", format="%.1f ⭐")
            },
            use_container_width=True,
            hide_index=True
        )
else:
    st.write("目前資料庫是空的，快來當第一個貢獻者吧！")


