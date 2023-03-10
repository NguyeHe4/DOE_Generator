from doepy import build
import inspect
import streamlit as st
import pandas as pd
from io import BytesIO
import datetime
import numpy as np

# build.lhs({"Pressure":[50,70], "Temperature":[25,50], "Flow": [1000,2000], "Flow2": [1000,2000]}, num_samples=None)

doe_designs = [d for d in dir(build) if "build" not in d and "__" not in d]
design = st.selectbox(
    "DOE Design", options=doe_designs, index=doe_designs.index("full_fact")
)
num_factors = int(st.number_input("Number of Factors", min_value=1))
factors = {}
for i in range(1, num_factors + 1):
    f = st.text_input(f"Factor {i}")
    levels = st.text_input(f"Level {i}")
    factors[f] = (
        eval(levels)
        if len(levels) > 0 and levels[0] == "["
        else eval("[" + levels + "]")
    )
    if len(factors[f]) > 0 and type(factors[f][0]) == str:
        try:
            factors[f] = np.float(factors[f])
        except:
            pass

function = eval(f"build.{design}")
params = dict()
func_params = inspect.signature(function).parameters

st.write(function.__doc__)
for param in list(func_params):
    if param == "d":
        continue
    elif param == "num_samples":
        param_input = st.number_input(param, value=num_factors, step=1, min_value=1)
        params[param] = param_input
    else:
        param_input = st.text_input(param)
        if param_input != "":
            try:
                params[param] = (
                    int(param_input)
                    if int(param_input) % param_input == 0
                    else float(param_input)
                )
            except:
                params[param] = param_input


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    format1 = workbook.add_format({"num_format": "0.00"})
    worksheet.set_column("A:A", None, format1)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

# DOE = pd.DataFrame()

if factors != {}:
    print(factors)
    print(params)
    if st.button("Generate DOE"):
        st.session_state["DOE"] = eval("function(factors, **params)")
        st.session_state["DOE"] = st.session_state["DOE"].reset_index()
        st.session_state["DOE"].rename(columns={st.session_state["DOE"].columns[0]: "Run"}, inplace=True)
    st.session_state["DOE"] = st.session_state["DOE"].astype(str)
    edited_DOE = st.experimental_data_editor(st.session_state["DOE"], num_rows="dynamic", disabled=False)
    # edited_DOE.loc["End"] = [""] * len(edited_DOE.columns)
    DOE_xlsx = to_excel(edited_DOE)
    st.download_button(
        "Download DOE",
        data=DOE_xlsx,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        file_name=f"{design}_{datetime.datetime.now().strftime(r'%Y-%m-%d %H-%M-%S')}.xlsx",
    )

    
