from doepy import build
import inspect
import streamlit as st
import pandas as pd
from io import BytesIO
import datetime


doe_designs = [d for d in dir(build) if "build" not in d and "__" not in d]
design = st.selectbox("DOE Design", options=doe_designs, index=doe_designs.index("full_fact"))
num_factors = int(st.number_input("Number of Factors", min_value=1))
factors = {}
for i in range(1, num_factors + 1):
    f = st.text_input(f"Factor {i}")
    levels = st.text_input(f"Level {i}")
    factors[f] = eval(levels) if len(levels) > 0 and levels[0] == "["  else eval("[" + levels + "]")

function = eval(f"build.{design}")
params = dict()
func_params = inspect.signature(eval(f"build.{design}")).parameters
DOE = pd.DataFrame()
st.write(function.__doc__)
for param in list(func_params):
    if param == "d":
        continue
    else:
        param_input = st.text_input(param)
        if param_input != "":
            params[param] = param_input
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

if factors != {}:
    DOE = eval("function(factors, **params)")
    DOE.loc["End"] = [""] * len(DOE.columns)
    DOE = DOE.reset_index()
    DOE.rename(columns={DOE.columns[0]: "Run"}, inplace=True)
    st.dataframe(DOE)
    DOE_xlsx = to_excel(DOE)
    st.download_button("Download DOE", data=DOE_xlsx, mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', file_name=f"{design}_{datetime.datetime.now().strftime(r'%Y-%m-%d %H-%M-%S')}.xlsx")

