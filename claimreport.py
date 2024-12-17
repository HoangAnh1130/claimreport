import duckdb
import pandas as pd
import plotly.express as px
# import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
# import subprocess
# import webbrowser
# import psutil 
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from PIL import Image
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# import time
# import os

# Mở ứng dụng Streamlit trong trình duyệt
def open_browser():
    url = "http://localhost:8501"
    webbrowser.open(url)
#######################################
# PAGE SETUP
#######################################

st.set_page_config(page_title="Claim Dashboard", page_icon=":bar_chart:", layout="wide")

# Thêm CSS để căn giữa
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)


with st.sidebar:
    st.header("UPLOAD YOUR FILE")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True, type=["csv", "xlsx", "xls"])
    if not uploaded_files:
        st.info("Upload files", icon="ℹ️")
        st.stop()

    #######################################
    # DATA LOADING
    #######################################

    @st.cache_data
    def load_data(file):
        if file.name.endswith(".xlsx"):
            return pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file.name}")
            return None
    st.title("Tiêu chí phân tích")
    
    if "active_group" not in st.session_state:
        st.session_state["active_group"] = "group_1"

# Tạo radio button để chọn nhóm
    selected_group = st.radio(
        "Chọn nhóm báo cáo:",
        ["Báo cáo bồi thường", "Báo cáo y khoa/Nhân khẩu học"],
        index=0 if st.session_state["active_group"] == "group_1" else 1
    )

    # Cập nhật trạng thái nhóm được chọn
    if selected_group == "Báo cáo bồi thường":
        st.session_state["active_group"] = "group_1"
    else:
        st.session_state["active_group"] = "group_2"

    # Hiển thị selectbox tương ứng với nhóm đã chọn
    if st.session_state["active_group"] == "group_1":
        st.session_state["selected_option_group1"] = st.selectbox(
            "Báo cáo bồi thường",
            ["Báo cáo tỉ lệ bồi thường", "Báo cáo loại hình bồi thường", "Báo cáo theo quyền lợi","Báo cáo theo chi nhánh/Tập đoàn"],
            index=st.session_state.get("selected_option_group1_index", 0)
        )
        # Lưu lại lựa chọn
        st.session_state["selected_option_group1_index"] = ["Báo cáo tỉ lệ bồi thường", "Báo cáo loại hình bồi thường", "Báo cáo theo quyền lợi","Báo cáo theo chi nhánh/Tập đoàn"].index(st.session_state["selected_option_group1"])
        # st.write(f"Bạn đã chọn: **{st.session_state['selected_option_group1']}**")

    elif st.session_state["active_group"] == "group_2":
        st.session_state["selected_option_group2"] = st.selectbox(
            "Báo cáo y khoa/Nhân khẩu học",
            ["Báo cáo nhóm bệnh", "Báo cáo cơ sở y tế","Báo cáo độ tuổi","Báo cáo giới tính"],
            index=st.session_state.get("selected_option_group2_index", 0)
        )
        # Lưu lại lựa chọn
        st.session_state["selected_option_group2_index"] = ["Báo cáo nhóm bệnh", "Báo cáo cơ sở y tế","Báo cáo độ tuổi","Báo cáo giới tính"].index(st.session_state["selected_option_group2"])
        # st.write(f"Bạn đã chọn: **{st.session_state['selected_option_group2']}**")
        
lua_chon = ''
if st.session_state["active_group"] == "group_1":
    if st.session_state['selected_option_group1'] == "Báo cáo tỉ lệ bồi thường":
        lua_chon = 'Nhóm khách hàng'
    elif st.session_state['selected_option_group1'] == "Báo cáo loại hình bồi thường":
        lua_chon = 'Loại hình bồi thường'
    elif st.session_state['selected_option_group1'] == "Báo cáo theo quyền lợi":
        lua_chon = 'Nhóm quyền lợi'
    elif st.session_state['selected_option_group1'] == "Báo cáo theo chi nhánh/Tập đoàn":
        lua_chon = 'Đơn vị tham gia BH'
elif st.session_state["active_group"] == "group_2":
    if st.session_state['selected_option_group2'] == "Báo cáo nhóm bệnh":
        lua_chon = 'Nhóm bệnh'
    elif st.session_state['selected_option_group2'] == "Báo cáo cơ sở y tế":
        lua_chon = 'Cơ sở y tế'
    elif st.session_state['selected_option_group2'] == "Báo cáo độ tuổi":
        lua_chon = 'Tuổi'
    elif st.session_state['selected_option_group2'] == "Báo cáo giới tính":
        lua_chon = 'Giới tính'
        
else:
    st.write("Vui lòng chọn nhóm phân tích")
  
# Hiển thị tiêu đề
st.markdown('<div class="title">CLAIM REPORT</div>', unsafe_allow_html=True)
st.title('')

# Load each file and display its data
dataframes = []
#df claim chungchung
for uploaded_file in uploaded_files:
    df = load_data(uploaded_file)
    
    if df is not None:
        if "fullerton" in uploaded_file.name.lower():
            df['Insured ID'] = df['Insured ID'].astype(str)
            fullerton_desired_columns = ['Insured ID',"Relation", 'Chan doan benh', 'Request amount','Claim amount','Rejected amount - paid case','Medical providers','Beneficiary type','Reject reasons','Client name','Policy effective date','Type of claim submit','Gender','DOB']
            df_fullerton_cleaned = df[fullerton_desired_columns]
            df_fullerton_cleaned.columns = ['Insured ID','Nhóm khách hàng', 'Nhóm bệnh', 'Số tiền yêu cầu bồi thường', 'Số tiền đã được bồi thường','Chênh lệch','Cơ sở y tế','Nhóm quyền lợi','Lý do từ chối','Đơn vị tham gia BH','Ngày hiệu lực','Loại hình bồi thường','Giới tính','Ngày sinh']
            df_fullerton_cleaned = df_fullerton_cleaned.reset_index(drop=True)
            df_fullerton_cleaned['Ngày sinh'] = pd.to_datetime(df_fullerton_cleaned['Ngày sinh'], errors='coerce')
            ngay_hom_nay = datetime.now()
            df_fullerton_cleaned['Tuổi'] = ((ngay_hom_nay -df_fullerton_cleaned['Ngày sinh']).dt.days)/365
            df_fullerton_cleaned['Tuổi'] = df_fullerton_cleaned['Tuổi'].astype(int)
            dataframes.append(df_fullerton_cleaned) 
        elif 'hopdongbaohiem' in uploaded_file.name.lower():
            df_hopdongbaohiem = df 
        # elif 'nhansu' in uploaded_file.name.lower():
        #     df = df['Insured ID','Nhóm', 'Nhóm bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Cơ sở y tế','Nhóm quyền lợi','Lý do từ chối','Tên công ty']
        # else:
        #     # File không hợp lệ, xóa nó khỏi danh sách và cảnh báo
        #     st.error(f"Invalid file name: {uploaded_file.name}. This file does not match expected naming conventions.")
        #     uploaded_files.remove(uploaded_file)  # Xóa file không hợp lệ khỏi danh sách

if lua_chon in  ['Nhóm khách hàng','Loại hình bồi thường','Nhóm quyền lợi','Đơn vị tham gia BH','Nhóm bệnh','Cơ sở y tế','Giới tính','Tuổi']:
    option = lua_chon
    group = duckdb.sql(
        f"""
    SELECT 
        "{option}",
        count(distinct "Insured ID") as "Số người yêu cầu bồi thường",
        count("Insured ID") as "Số hồ sơ bồi thường",
        concat(round(count("Insured ID")*100 /count(*),1),'%') as "%Trường hợp",
        ROUND(SUM("Số tiền yêu cầu bồi thường")) AS "Số tiền yêu cầu bồi thường",
        ROUND(SUM("Số tiền đã được bồi thường")) AS "Số tiền được bồi thường",
        ROUND(SUM("Số tiền đã được bồi thường")/count(distinct "Insured ID")) as "Số tiền bồi thường trung bình/người",
        concat(round(SUM("Số tiền đã được bồi thường")*100/SUM("Số tiền yêu cầu bồi thường"),1),'%') as "Tỉ lệ thành công"
        -- datediff('day',STRPTIME(CAST("Ngày hiệu lực" AS VARCHAR), '%Y-%m-%d %H:%M:%S'), now()) as "Số ngày đã tham gia"
    FROM df_fullerton_cleaned
    GROUP BY "{option}","Ngày hiệu lực"
"""
    ).df()

    nhansu_file = None 
    for file in uploaded_files:
        if 'nhansu' in file.name.lower():  # Kiểm tra tên tệp có chứa 'nhansu'
            nhansu_file = file
            break
    if "fullerton" in uploaded_file.name.lower():    
        if nhansu_file:
            nhansu_df = pd.read_excel(nhansu_file)
            result = pd.merge(group, nhansu_df, how='right', on='Insure ID')
            count = result.groupby('Insure ID')['Insure ID'].count().reset_index(name='Số người được bảo hiểm')
            group.insert(1, 'Số người được bảo hiểm', count.pop('Số người được bảo hiểm'))
            a = group["Số người yêu cầu bồi thường"] / group['Số người được bảo hiểm']
            group.insert(3, 'Tỉ lệ yêu cầu bồi thường', a )
        else:
            group.insert(1, 'Số người được bảo hiểm', None)
            group.insert(3, 'Tỉ lệ yêu cầu bồi thường', None)
        hopdongbaohiem = None 
        for file in uploaded_files:
            if 'hopdongbaohiem' in file.name.lower():  # Kiểm tra tên tệp có chứa 'nhansu'
                hopdongbaohiem_file = file
                break
        if hopdongbaohiem_file:   
            hopdongbaohiem_df = pd.read_excel(hopdongbaohiem_file)
            sum_tien_da_boi_thuong = df_fullerton_cleaned.groupby('Đơn vị tham gia BH')['Số tiền đã được bồi thường'].sum().reset_index(name='Tổng số tiền đã bồi thường')
            tencongty = df_fullerton_cleaned['Đơn vị tham gia BH'][1]
            ngay_intable = hopdongbaohiem_df['Ngày bắt đầu'].loc[hopdongbaohiem_df['Tên công ty'] == tencongty]
            ngay_hieu_luc = pd.to_datetime(ngay_intable.iloc[0])
            ngay_lam_bao_cao = datetime.now()
            so_ngay_tham_gia_BH = (ngay_lam_bao_cao-ngay_hieu_luc).days
            tongphibaohiem = ngay_intable = hopdongbaohiem_df['Tổng phí bảo hiểm'].loc[hopdongbaohiem_df['Tên công ty'] == tencongty]
            tongphibaohiem = float(tongphibaohiem)
            so_ngay_tham_gia_BH = float(so_ngay_tham_gia_BH)
            group['Số tiền được bồi thường'] = group['Số tiền được bồi thường'].astype(float)
            group['Tỉ lệ loss thực tế'] = (group['Số tiền được bồi thường']*100*so_ngay_tham_gia_BH)/((365)*tongphibaohiem)
            group['Tỉ lệ loss ước tính (14m)'] = (group['Số tiền được bồi thường']*100*so_ngay_tham_gia_BH)/((365+30*2)*tongphibaohiem)
            
            # df_tinh_toan['Tỉ lệ loss thực tế'] = (df_tinh_toan['Số tiền được bồi thường'] * in so_ngay_tham_gia_BH / 365 * tongphibaohiem * 100)
            # df_tinh_toan['Tỉ lệ loss ước tính (14m)'] = (df_tinh_toan['Số tiền được bồi thường'] * so_ngay_tham_gia_BH / (365 + 30 * 2) * tongphibaohiem * 100)
            # group = pd.merge(group, df_tinh_toan[[f'{option}', 'Tỉ lệ loss thực tế', 'Tỉ lệ loss ước tính (14m)']], on=f'{option}', how='left')
            
            
            
    group_display = group.copy()
    def format_number(x):
        return "{:,.0f}".format(x)
    def format_percentage(value):
        return "{:.2f}%".format(float(value)).replace('.', ',')
    group_display['Tỉ lệ loss thực tế'] =  group_display['Tỉ lệ loss thực tế'].apply(format_percentage)
    group_display['Tỉ lệ loss ước tính (14m)'] =  group_display['Tỉ lệ loss ước tính (14m)'].apply(format_percentage)
    group_display['Số tiền yêu cầu bồi thường'] = group_display['Số tiền yêu cầu bồi thường'].apply(format_number)
    group_display['Số tiền được bồi thường'] = group_display['Số tiền được bồi thường'].apply(format_number)
    group_display['Số tiền bồi thường trung bình/người'] = group_display['Số tiền bồi thường trung bình/người'].apply(format_number)

    def style_table(df):
        styles = [
            {'selector': 'thead th',
            'props': [('background-color', '#330099'),  # Màu xanh dương đậm
                    ('color', 'white'),              # Chữ trắng
                    ('font-weight', 'bold'),         # Chữ in đậm
                    ('text-align', 'center')]}       # Chữ căn giữa
            ]
    
    # Áp dụng màu nền xen kẽ cho các dòng dữ liệu
        def alternating_row_colors(row):
            if row.name % 2 == 0:
                return ['background-color: None'] * len(row)  # Hàng chẵn: trắng
            else:
                return ['background-color: None'] * len(row)  # Hàng lẻ: tím nhạt

    # Kết hợp styles
        styled_df = df.style.set_table_styles(styles) \
                            .apply(alternating_row_colors, axis=1)
    
        st.markdown(styled_df.to_html(), unsafe_allow_html=True)
        return styled_df
    style_table(group_display)

    
    top_5_case = group.sort_values(by='Số người yêu cầu bồi thường', ascending=False).head(5)
    top_5_amount = group.sort_values(by='Số tiền được bồi thường', ascending=False).head(5)
    col_pie_chart1, col_pie_chart2 = st.columns(2)
    with col_pie_chart1:
        pie_chart1 = px.pie(top_5_case, names=f'{lua_chon}', values="Số hồ sơ bồi thường", title=f'Số hồ sơ yêu cầu bồi thường theo {lua_chon.lower()}', 
            color=f'{lua_chon}',  
            color_discrete_map={
                "Dependant": "#3A0751", 
                "Employee": "#f2c85b"
            },  # Ánh xạ màu
            hole=0.6)
        st.plotly_chart(pie_chart1)
    with col_pie_chart2:
        pie_chart2 = px.pie(top_5_amount, names=f'{lua_chon}', values="Số tiền được bồi thường", title=f'Số tiền đã bồi thường theo {lua_chon.lower()}',hole=0.6)
        st.plotly_chart(pie_chart2)
#df demographicdemographic
for uploaded_file in uploaded_files:
    df = load_data(uploaded_file)
    if df is not None:
        if "fullerton" in uploaded_file.name.lower():
            try:
                a1 = ['Insured ID','Request amount','Claim amount','Rejected amount - paid case','Gender',"DOB"] 
                df_fullerton_demo = df[a1]  
                df_fullerton_demo.columns = ['Insured ID', 'Số tiền yêu cầu bồi thường', 'Số tiền đã được bồi thường','Chênh lệch','Giới tính','Ngày sinh']
                df_fullerton_demo = df_fullerton_cleaned.reset_index(drop=True)
            except KeyError as e:
                print(f"Lỗi: Cột {e} không tồn tại trong bảng.")
                
    
