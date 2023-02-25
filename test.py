# -*- coding: utf-8 -*-
import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
import pymysql.cursors
import altair as alt
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rc("font", family='YouYuan')
matplotlib.rc('axes', unicode_minus=False)  # 用来正常显示负号


def save_to_sql(df, user, password, ip, database):
    con = create_engine(f"mysql+pymysql://{user}:{password}@{ip}:3306/{database}?charset=utf8")
    df.to_sql(table_name, con, if_exists='replace')


st.title('Test page')
# 连接数据库
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="rootpassword",
    db="test",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

# 获取现在访问的数据库名称，以及数据库中已有表格名
with connection.cursor() as cursor:
    # 查询当前数据库
    cursor.execute('SELECT DATABASE()')
    # 获取结果
    current_database = cursor.fetchone()['DATABASE()']
    cursor.execute("SHOW TABLES")
    table_names = [table['Tables_in_test'] for table in cursor.fetchall()]

uploaded_file = st.file_uploader("上传数据文件(csv或excel)", type=["csv", "xlsx"])

# 如果用户上传了文件
if uploaded_file is not None:
    # 读取文件内容为DataFrame
    df1 = pd.read_csv(uploaded_file) if uploaded_file.type == 'text/csv' else pd.read_excel(uploaded_file)

    # 读取文件名作为表名
    table_name = uploaded_file.name.split('.')[0]
    print('\n\n\n\n\n', table_name)
    print(table_names)
    # 将文件内容保存到MySQL数据库
    if table_name not in table_names:
        save_to_sql(df1, 'root', 'rootpassword', 'localhost', 'test')

# 如果用户没有上传文件，展示数据库中的数据
else:
    # 如果数据库中没有表格，则提示用户上传数据
    if len(table_names) == 0:
        st.warning("请上传数据文件(csv或excel)或在MySQL数据库中创建表格")

    # 如果数据库中有表格
    else:
        # 显示表格名选择框
        table_name = st.selectbox(f"或者选择当前数据库( {current_database} )中现有的数据表格：", table_names)

        # 从数据库中读取表格内容
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()

        # 转换为DataFrame并展示
        df1 = pd.DataFrame(data)

if st.checkbox("显示当前数据？"): st.write(df1)
show_chart = st.checkbox("绘制折线图？")

if show_chart:
    # 选择要绘制的列
    x_col = st.selectbox("选择X轴数据列", df1.columns)
    y_col = st.multiselect("选择Y轴数据列(可选多个)", df1.columns)

    # 提取x轴和y轴数据
    x = df1[x_col]
    y_data = df1[y_col]

    # 绘制折线图
    fig, ax = plt.subplots()
    for col in y_data.columns:
        y = y_data[col]
        ax.plot(x, y, label=col)

    # 添加图例和标签
    ax.legend()
    ax.set_xlabel(x_col)

    # 显示图表
    st.pyplot(fig)
