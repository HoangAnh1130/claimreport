import duckdb
import pandas as pd
import plotly.express as px
# import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import numpy as np
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
    
if 'top_by' not in st.session_state:
    st.session_state.top_by = ''
if lua_chon in ['Cơ sở y tế','Nhóm bệnh']:
    col1,col2 = st.columns(2)
    with col1:      
        if st.button('Top 5 theo số tiền đã bồi thường'):
            st.session_state.top_by = 'ST5'
        if st.button('Top 5 theo số người yêu cầu bồi thường'):
            st.session_state.top_by = 'SN5'
    with col2:
        # if st.button('Top 10 theo số tiền đã bồi thường'):
        #     st.session_state.top_by = 'ST10'
        # if st.button('Top 10 theo số người yêu cầu bồi thường'):
        #     st.session_state.top_by = 'SN10'
        if st.button('Tất cả'):
            st.session_state.top_by = 'TC'

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
            df_fullerton_cleaned["Nhóm khách hàng"] = df_fullerton_cleaned["Nhóm khách hàng"].replace({
                'Others': 'Người thân',
                'Member': 'Nhân viên',
                'Child': 'Người thân'
                # 'children' : 'Dependant',
                # 'nhanvien_01' : 'Employee',
                # 'người thân' : 'Dependant',
                # 'nguoithan_01' : 'Dependant',
                # 'nhân viên' : 'Employee'
            })
            
            dataframes.append(df_fullerton_cleaned) 
        elif "pvi" in uploaded_file.name.lower():
            df1 = df
            df1 = df1.drop(index = [0,1])   
            df1 = df1[['Số hồ sơ bồi thường','Đối tượng bảo hiểm','Nhóm bệnh','Số tiền yêu cầu BT','Số tiền bồi thường\n(100%)','Số tiền từ chối BT','Cơ sở y tế','Quyền lợi BH','Nguyên nhân từ chối BT',
                    'Đơn vị tham gia BH','Từ ngày','Phương thức khai thác','Tuổi NĐBH']]
            df1.rename(columns={'Số hồ sơ bồi thường': 'Insured ID', 'Đối tượng bảo hiểm':'Nhóm khách hàng','Số tiền yêu cầu BT':'Số tiền yêu cầu bồi thường','Số tiền bồi thường\n(100%)':'Số tiền đã được bồi thường',
                                'Số tiền từ chối BT':'Chênh lệch','Nguyên nhân từ chối BT':'Lý do từ chối','Từ ngày':'Ngày hiệu lực','Phương thức khai thác':'Loại hình bồi thường','Tuổi NĐBH'  :'Tuổi','Quyền lợi BH' : 'Nhóm quyền lợi'}, inplace= True)
            df1.head(2)
            dataframes.append(df1) 
        elif "pti" in uploaded_file.name.lower():
            df2 = df
            df2 = df2.drop(index = 0)
            df_filter = df2[['Trợ cấp nghỉ/lương','Tử vong/ Thương tật  vĩnh viễn','Nằm viện điều trị','Nằm viện phẫu thuật','Sinh thường','Sinh mổ và biến chứng thai sản','Điều trị ngoại trú','Điều trị răng','Tử vong do ốm bệnh thai sản']]
            df_filter['Nhóm quyền lợi'] = df_filter.apply(lambda row: ', '.join(row.index[row != 0]), axis=1)
            df2 = pd.concat([df2, df_filter['Nhóm quyền lợi']], axis=1)
            df2 = df2[['Số hồ sơ','Nhóm','Mã Bệnh','Số tiền yêu cầu bồi thường','Tổng số tiền bồi thường','Tên bệnh viện','Nhóm quyền lợi','Diễn giải','Tên chủ hợp đồng','Từ','Phân loại hồ sơ','Nam/Nữ','Tuổi']]
            df2.rename(columns={'Số hồ sơ': 'Insured ID', 'Nhóm': 'Nhóm khách hàng','Mã Bệnh':'Nhóm bệnh','Tổng số tiền bồi thường':'Số tiền đã được bồi thường',
                                'Tên bệnh viện':'Cơ sở y tế','Diễn giải':'Lý do từ chối','Tên chủ hợp đồng':'Đơn vị tham gia BH','Từ':'Ngày hiệu lực','Phân loại hồ sơ':'Loại hình bồi thường','Nam/Nữ':"Giới tính"}, inplace= True)
            df2.head()
            df2["Nhóm khách hàng"] = df2["Nhóm khách hàng"].replace({
                'NHANVIEN_01': 'Nhân viên'
            })
            dataframes.append(df2)
        elif 'hopdongbaohiem' in uploaded_file.name.lower():
            df_hopdongbaohiem = df
        elif 'nhansu' in uploaded_file.name.lower():
            df_nhansu = df
        else: 
            df_phan_tich = df['Insured ID','Nhóm khách hàng', 'Nhóm bệnh', 'Số tiền yêu cầu bồi thường', 'Số tiền đã được bồi thường','Chênh lệch','Cơ sở y tế','Nhóm quyền lợi','Lý do từ chối','Đơn vị tham gia BH','Ngày hiệu lực','Loại hình bồi thường','Giới tính','Ngày sinh'] 
            dataframes.append(df_phan_tich) 
        # elif 'nhansu' in uploaded_file.name.lower():
        #     df = df['Insured ID','Nhóm', 'Nhóm bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Cơ sở y tế','Nhóm quyền lợi','Lý do từ chối','Tên công ty']
        # else:
        #     # File không hợp lệ, xóa nó khỏi danh sách và cảnh báo
        #     st.error(f"Invalid file name: {uploaded_file.name}. This file does not match expected naming conventions.")
        #     uploaded_files.remove(uploaded_file)  # Xóa file không hợp lệ khỏi danh sách
if dataframes:
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df['Tuổi'] = combined_df['Tuổi'].apply(lambda x: "Dưới 18" if x < 18 
                                          else ("18-24" if x <= 24 
                                                else ("25-34" if x <= 34 
                                                      else ("35-44" if x <= 44 
                                                            else ("45-54" if x <= 54 
                                                                  else ("55-64" if x <= 64 
                                                                        else "Trên 65"))))))
else:
    combined_df = pd.DataFrame(columns=['Insured ID','Nhóm khách hàng', 'Nhóm bệnh', 'Số tiền yêu cầu bồi thường', 'Số tiền đã được bồi thường','Chênh lệch','Cơ sở y tế','Nhóm quyền lợi','Lý do từ chối','Đơn vị tham gia BH','Ngày hiệu lực','Loại hình bồi thường','Giới tính','Ngày sinh'])


if lua_chon in  ['Nhóm khách hàng','Loại hình bồi thường','Nhóm quyền lợi','Đơn vị tham gia BH','Nhóm bệnh','Cơ sở y tế','Giới tính','Tuổi']:
    option = lua_chon
    group = duckdb.sql(
        f"""
    SELECT 
        "{option}",
        count(distinct "Insured ID") as "Số người yêu cầu bồi thường",
        count("Insured ID") as "Số hồ sơ bồi thường",
        ROUND(COUNT("Insured ID") * 100.0 / (SELECT COUNT(*) FROM combined_df), 1) as "%Trường hợp",
        ROUND(SUM("Số tiền yêu cầu bồi thường")) AS "Số tiền yêu cầu bồi thường",
        ROUND(SUM("Số tiền đã được bồi thường")) AS "Số tiền được bồi thường",
        ROUND(SUM("Số tiền đã được bồi thường")/count(distinct "Insured ID")) as "Số tiền bồi thường trung bình/người",
        round(SUM("Số tiền đã được bồi thường")*100/SUM("Số tiền yêu cầu bồi thường"),1) as "Tỉ lệ thành công"
        -- datediff('day',STRPTIME(CAST("Ngày hiệu lực" AS VARCHAR), '%Y-%m-%d %H:%M:%S'), now()) as "Số ngày đã tham gia"
    FROM combined_df
    GROUP BY "{option}"
"""
    ).df()

    if lua_chon == "Tuổi":
        
        group["Tuổi"] = group["Tuổi"].apply(
            lambda x: f"{int(float(x)):,}" if isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.', '', 1).isdigit()) else x
        )

    if dataframes:    
        tencongty = combined_df['Đơn vị tham gia BH'][0]
        nhansu_file = None 
        for file in uploaded_files:
            if 'nhansu' in file.name.lower():  # Kiểm tra tên tệp có chứa 'nhansu'
                nhansu_file = file
                break
        try:
            if nhansu_file:
                nhansu_df = pd.read_excel(nhansu_file)  
                if tencongty in nhansu_df['Tên công ty'].values:
                    try:                   
                        tongsonhanvien = nhansu_df["Đối tượng bảo hiểm"].value_counts().get("Nhân viên", 0)
                        tongsonguoithan = nhansu_df["Đối tượng bảo hiểm"].value_counts().get("Người thân", 0)
                        tongsongdcbaohiem = tongsonhanvien+tongsonguoithan
                        group.insert(1, 'Số người được bảo hiểm',None)
                        group.loc[group[f'{lua_chon}'] == "Nhân viên", "Số người được bảo hiểm"] = tongsonhanvien
                        group.loc[group[f'{lua_chon}'] == "Người thân", "Số người được bảo hiểm"] = tongsonguoithan
                        group.insert(3, 'Tỉ lệ yêu cầu bồi thường',None)
                        sonhanvienyeucauboithuong = group.loc[group['Nhóm khách hàng'] == 'Nhân viên', 'Số người yêu cầu bồi thường']
                        songuoithanyeucauboithuong = group.loc[group['Nhóm khách hàng'] == 'Người thân', 'Số người yêu cầu bồi thường']
                        # try: 
                        #     sonhanvienyeucauboithuong = float(sonhanvienyeucauboithuong)
                        # except TypeError:
                        #     sonhanvienyeucauboithuong = 0
                        # try: 
                        #     songuoithanyeucauboithuong = float(songuoithanyeucauboithuong)
                        # except TypeError:
                        #     songuoithanyeucauboithuong = 0
                        group.loc[group[f'{lua_chon}'] == "Nhân viên", "Tỉ lệ yêu cầu bồi thường"] = sonhanvienyeucauboithuong*100/tongsonhanvien
                        group.loc[group[f'{lua_chon}'] == "Người thân", "Tỉ lệ yêu cầu bồi thường"] = songuoithanyeucauboithuong*100/tongsonguoithan
                        
                        # try:
                        #     group.loc[group[f'{lua_chon}'] == "Nhân viên", "Tỉ lệ yêu cầu bồi thường"] = sonhanvienyeucauboithuong*100/tongsonhanvien
                        # except ZeroDivisionError:
                        #     group.loc[group[f'{lua_chon}'] == "Người thân", "Tỉ lệ yêu cầu bồi thường"] = 0
                        # try:
                        #     group.loc[group[f'{lua_chon}'] == "Người thân", "Tỉ lệ yêu cầu bồi thường"] = songuoithanyeucauboithuong*100/tongsonguoithan
                        # except ZeroDivisionError:
                        #     group.loc[group[f'{lua_chon}'] == "Người thân", "Tỉ lệ yêu cầu bồi thường"] = 0 
                    # result = pd.merge(group, nhansu_df, how='right', on='Insure ID')
                    # count = result.groupby('Insure ID')['Insure ID'].count().reset_index(name='Số người được bảo hiểm')
                    # a = group["Số người yêu cầu bồi thường"] / group['Số người được bảo hiểm']
                    # group.insert(3, 'Tỉ lệ yêu cầu bồi thường', a )
                    except KeyError:
                        pass
            else:
                pass
        except NameError:
            pass    
            
            
        hopdongbaohiem_file = None 
        for file in uploaded_files:
            if 'hopdongbaohiem' in file.name.lower():  # Kiểm tra tên tệp có chứa 'nhansu'
                hopdongbaohiem_file = file
                break
        try:
            if hopdongbaohiem_file:  
                hopdongbaohiem_df = pd.read_excel(hopdongbaohiem_file)
                ngay_intable = hopdongbaohiem_df['Ngày bắt đầu'].loc[(hopdongbaohiem_df['Tên công ty'] == tencongty) & ((hopdongbaohiem_df['Nhóm khách hàng'] == 'Nhân viên'))]
                ngay_hieu_luc = pd.to_datetime(ngay_intable.iloc[0])
                ngay_lam_bao_cao = datetime.now()
                so_ngay_tham_gia_BH = (ngay_lam_bao_cao-ngay_hieu_luc).days
                tongphibaohiem_nv = hopdongbaohiem_df['Tổng phí bảo hiểm'].loc[(hopdongbaohiem_df['Tên công ty'] == tencongty) & ((hopdongbaohiem_df['Nhóm khách hàng'] == 'Nhân viên'))]
                tongphibaohiem_nt = hopdongbaohiem_df['Tổng phí bảo hiểm'].loc[(hopdongbaohiem_df['Tên công ty'] == tencongty) & ((hopdongbaohiem_df['Nhóm khách hàng'] == 'Người thân'))]
                sum_tien_phi_BH_theo_donvi = hopdongbaohiem_df.groupby('Tên công ty')['Tổng phí bảo hiểm'].sum().reset_index(name='Tổng phí bảo hiểm')
                tong_phi_bao_hiem = sum_tien_phi_BH_theo_donvi['Tổng phí bảo hiểm'].loc[(sum_tien_phi_BH_theo_donvi['Tên công ty'] == tencongty)]
                so_ngay_tham_gia_BH = float(so_ngay_tham_gia_BH)
                group['Số tiền được bồi thường'] = group['Số tiền được bồi thường'].astype(float)
                        
                try:
                    tongphibaohiem_nv = float(tongphibaohiem_nv)
                except TypeError:
                    tongphibaohiem_nv = 1
                try:
                    tongphibaohiem_nt = float(tongphibaohiem_nt)
                except TypeError:
                    tongphibaohiem_nt = 1
                # group = pd.merge(group, df_tinh_toan[[f'{option}', 'Tỉ lệ loss thực tế', 'Tỉ lệ loss ước tính (14m)']], on=f'{option}', how='left')
                if lua_chon == 'Nhóm khách hàng':
                    group["Tỉ lệ loss thực tế"] = np.where(
                    group["Nhóm khách hàng"] == "Nhân viên",  # Điều kiện
                    (group['Số tiền được bồi thường']*100)/(tongphibaohiem_nv),                         # Nếu điều kiện đúng
                    (group['Số tiền được bồi thường']*100)/(tongphibaohiem_nt)                      # Nếu điều kiện sai
                )
                        
                    group["Tỉ lệ loss ước tính (14m)"] = np.where(
                    group["Nhóm khách hàng"] == "Nhân viên",  # Điều kiện
                    (group['Số tiền được bồi thường']*1.1*100*425)/(((so_ngay_tham_gia_BH))*tongphibaohiem_nv),                         # Nếu điều kiện đúng
                    (group['Số tiền được bồi thường']*1.1*100*425)/((so_ngay_tham_gia_BH)*tongphibaohiem_nt)                        # Nếu điều kiện sai
                )
        except NameError:
            pass
        sum_tien_da_boi_thuong_theo_donvi = combined_df.groupby('Đơn vị tham gia BH')['Số tiền đã được bồi thường'].sum().reset_index(name='Tổng số tiền đã bồi thường')
        sum_tien_da_boi_thuong_theo_level = combined_df.groupby('Nhóm khách hàng')['Số tiền đã được bồi thường'].sum().reset_index(name='Tổng số tiền đã bồi thường')
        sum_tien_yeu_cau_boi_thuong_theo_level = combined_df.groupby('Nhóm khách hàng')['Số tiền yêu cầu bồi thường'].sum().reset_index(name='Tổng số tiền yêu cầu bồi thường')
        tongsotienyeucauboithuongtheonhanvien = sum_tien_yeu_cau_boi_thuong_theo_level[sum_tien_yeu_cau_boi_thuong_theo_level["Nhóm khách hàng"] == "Nhân viên"]["Tổng số tiền yêu cầu bồi thường"]
        tongsotienyeucauboithuongtheonguoithan = sum_tien_yeu_cau_boi_thuong_theo_level[sum_tien_yeu_cau_boi_thuong_theo_level["Nhóm khách hàng"] == "Người thân"]["Tổng số tiền yêu cầu bồi thường"]
        tongsotiendaboithuongtheonhanvien = sum_tien_da_boi_thuong_theo_level[sum_tien_da_boi_thuong_theo_level["Nhóm khách hàng"] == "Nhân viên"]["Tổng số tiền đã bồi thường"]
        tongsotiendaboithuongtheonguoithan = sum_tien_da_boi_thuong_theo_level[sum_tien_da_boi_thuong_theo_level["Nhóm khách hàng"] == "Người thân"]["Tổng số tiền đã bồi thường"]
        try:
            if float(tongsotienyeucauboithuongtheonguoithan) and float(tongsotienyeucauboithuongtheonhanvien):
                tongsotienyeucauboithuong = float(tongsotienyeucauboithuongtheonhanvien) + float(tongsotienyeucauboithuongtheonguoithan)
        except TypeError:
            try:         
                if float(tongsotienyeucauboithuongtheonhanvien) :
                    tongsotienyeucauboithuong = float(tongsotienyeucauboithuongtheonhanvien)
            except TypeError:
                try:
                    if float(tongsotienyeucauboithuongtheonguoithan):
                        tongsotienyeucauboithuong = float(tongsotienyeucauboithuongtheonguoithan)
                except TypeError:
                    pass          
        try:       
            if  float(tongsotiendaboithuongtheonhanvien) and float(tongsotiendaboithuongtheonguoithan):
                tongsotiendaboithuong = float(tongsotiendaboithuongtheonhanvien) + float(tongsotiendaboithuongtheonguoithan)  
        except TypeError:
            try:
                if  float(tongsotiendaboithuongtheonhanvien) :
                    tongsotiendaboithuong = float(tongsotiendaboithuongtheonhanvien)
            except TypeError:
                try:
                    if  float(tongsotiendaboithuongtheonguoithan):
                        tongsotiendaboithuong = float(tongsotiendaboithuongtheonguoithan)
                except TypeError:
                    pass
        tongsonguoiyeucauboithuong = group['Số người yêu cầu bồi thường'].sum()
        group['Số tiền được bồi thường'] = group['Số tiền được bồi thường'].astype(float)
        group['Số người yêu cầu bồi thường'] = group['Số người yêu cầu bồi thường'].astype(float)
        try :
            top_5_case = group.sort_values(by='Số người yêu cầu bồi thường', ascending=False).head(5)
            top_5_amount = group.sort_values(by='Số tiền được bồi thường', ascending=False).head(5)
            top_10_case = group.sort_values(by='Số người yêu cầu bồi thường', ascending=False).head(10)
            top_10_amount = group.sort_values(by='Số tiền được bồi thường', ascending=False).head(10)
            
            if lua_chon in ['Cơ sở y tế','Nhóm bệnh']:
                if st.session_state.top_by == 'ST5':
                    group = top_5_amount.copy()
                elif st.session_state.top_by == 'SN5':
                    group = top_5_case.copy()
                # elif st.session_state.top_by == 'ST10':
                #     group = top_10_case.copy()
                # elif st.session_state.top_by == 'SN10':
                #     group = top_10_amount.copy()
                elif st.session_state.top_by == 'TC':
                    pass
        except NameError:
            pass
        
        group.loc[len(group), f'{lua_chon}'] = "Total"
        group.loc[group[f'{lua_chon}'] == "Total", "Số tiền được bồi thường"] = group["Số tiền được bồi thường"].sum()
        group.loc[group[f'{lua_chon}'] == "Total", "Tỉ lệ thành công"] = ''
        try:
            group.loc[group[f'{lua_chon}'] == "Total", "Số người được bảo hiểm"] = group["Số người được bảo hiểm"].sum()
            group.loc[group[f'{lua_chon}'] == "Total", "Tỉ lệ yêu cầu bồi thường"] = group["Số người yêu cầu bồi thường"].sum()*100/tongsongdcbaohiem
        except KeyError:
            pass
        group.loc[group[f'{lua_chon}'] == "Total", "Số hồ sơ bồi thường"] = group["Số hồ sơ bồi thường"].sum()
        group.loc[group[f'{lua_chon}'] == "Total", "%Trường hợp"] = group["%Trường hợp"].sum()
        group.loc[group[f'{lua_chon}'] == "Total", "Số người yêu cầu bồi thường"] = group["Số người yêu cầu bồi thường"].sum()
        group.loc[group[f'{lua_chon}'] == "Total", "Số tiền yêu cầu bồi thường"] = group["Số tiền yêu cầu bồi thường"].sum()
        group.loc[group[f'{lua_chon}'] == "Total", "Số tiền bồi thường trung bình/người"] =   tongsotiendaboithuong/float(tongsonguoiyeucauboithuong)
        group.loc[group[f'{lua_chon}'] == "Total", "Tỉ lệ thành công"] =   tongsotiendaboithuong*100/tongsotienyeucauboithuong
        if lua_chon == 'Nhóm khách hàng' and hopdongbaohiem_file is not None:
            try:
                group.loc[group[f'{lua_chon}'] == "Total", "Tỉ lệ loss thực tế"] = (group['Số tiền được bồi thường']*100)/(float(tong_phi_bao_hiem))
                group.loc[group[f'{lua_chon}'] == "Total", "Tỉ lệ loss ước tính (14m)"] = (group['Số tiền được bồi thường']*1.11*100*425)/((so_ngay_tham_gia_BH)*float(tong_phi_bao_hiem))
            except NameError:
                group.loc[group[f'{lua_chon}'] == "Total", "Tỉ lệ loss thực tế"] = "NaN"
                group.loc[group[f'{lua_chon}'] == "Total", "Tỉ lệ loss ước tính (14m)"] = "NaN"

    group_display = group.copy()
    def convert_to_int(df, columns):
        for col in columns:
            if col in df.columns:  # Kiểm tra cột có tồn tại trong DataFrame không
                df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) else x)  # Chuyển đổi thành số nguyên
        return df
    columns_to_convert = ["Số người yêu cầu bồi thường", "Số hồ sơ bồi thường"]
    group_display = convert_to_int(group_display, columns_to_convert)
    def format_number(x):
        return "{:,.0f}".format(x)
    def format_percentage(value):
        return "{:.2f}%".format(float(value)).replace('.', ',')
    try:
        group_display['Tỉ lệ loss thực tế'] =  group_display['Tỉ lệ loss thực tế'].apply(format_percentage)
        group_display['Tỉ lệ loss ước tính (14m)'] =  group_display['Tỉ lệ loss ước tính (14m)'].apply(format_percentage)
    except KeyError as e:
        note = 'Khong tim thay cot'
    group_display['Tỉ lệ thành công'] =  group_display['Tỉ lệ thành công'].apply(format_percentage)
    group_display['%Trường hợp'] =  group_display['%Trường hợp'].apply(format_percentage)
    group_display['Số tiền yêu cầu bồi thường'] = group_display['Số tiền yêu cầu bồi thường'].apply(format_number)
    group_display['Số tiền được bồi thường'] = group_display['Số tiền được bồi thường'].apply(format_number)
    group_display['Số tiền bồi thường trung bình/người'] = group_display['Số tiền bồi thường trung bình/người'].apply(format_number)
    try:
        group_display['Tỉ lệ yêu cầu bồi thường'] =  group_display['Tỉ lệ yêu cầu bồi thường'].apply(format_percentage)
    except (KeyError,TypeError) as e:
        note = 'Khong tim thay cot'

    def style_table(df):
        styles = [
            {'selector': 'thead th',
            'props': [('background-color', '#330099'),  # Màu xanh dương đậm
                    ('color', 'white'),              # Chữ trắng
                    ('font-weight', 'bold'),         # Chữ in đậm
                    ('text-align', 'center')]}       # Chữ căn giữa
            ]
    
    # Áp dụng màu nền xen kẽ cho các dòng dữ liệu
        # def alternating_row_colors(row):
        #     if row.name % 2 == 0:
        #         return ['background-color: None'] * len(row)  # Hàng chẵn: trắng
        #     else:
        #         return ['background-color: None'] * len(row)  # Hàng lẻ: tím nhạt
        
    # Kết hợp styles
        styled_df = df.style.set_table_styles(styles) 
        # \
        #                     .apply(alternating_row_colors, axis=1)
    
        st.markdown(styled_df.to_html(), unsafe_allow_html=True)
        return styled_df
    # top_10_amount = group_display.sort_values(by='Số người yêu cầu bồi thường', ascending=False).head(10)
    
    style_table(group_display)

    try:
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
    except NameError:
        pass
