import streamlit as st
import pandas as pd
import json
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

# Function to generate SQL code
def generate_sql(json_data_sources, json_data_target,json_example_data_sources,json_example_data_target):
    prompt = f'''
    You are an accurate SQL mapping assistant. Write a SQL query that uses the sources and maps to the target definition. The JSONs contain the metadata of the sources and targets. Important: Do not use the JSON in the SQL. The SQL should be accurate and should not contain any errors. The SQL should be modular but without unnecessary repetition.

    <EXAMPLE>
    JSON for the Sources = {json_example_data_sources}
    JSON for the Targets = {json_example_data_target}
    
    -- CTE for Latest Department
    WITH LatestDepartment AS (
        SELECT ee.ID AS EmployeeID, ed.DEPID AS DepartmentID, d.name AS DepartmentName, ROW_NUMBER() OVER (PARTITION BY ee.ID ORDER BY ed.ValidFrom DESC) AS rn
        FROM EE ee
        LEFT JOIN ED ed ON ee.ID = ed.EMPID
        LEFT JOIN Dep d ON ed.DEPID = d.ID
    ),
    -- CTE for Latest Department Address
    LatestDepartmentAddress AS (
        SELECT ld.EmployeeID, ld.DepartmentID, ld.DepartmentName, a.City AS DepartmentAddressCity, a.State AS DepartmentAddressState, a.Zip AS DepartmentAddressZip, ROW_NUMBER() OVER (PARTITION BY ld.EmployeeID, ld.DepartmentID ORDER BY a.ValidFrom DESC) AS rn
        FROM LatestDepartment ld
        LEFT JOIN AD a ON ld.DepartmentID = a.DEPID
        WHERE ld.rn = 1
    ),
    -- Final Query
    SELECT ld.EmployeeID, CONCAT(CAST(ee.firstname AS VARCHAR(100)), ' ', CAST(ee.lastname AS VARCHAR(100))) AS EmployeeName, lda.DepartmentName, CAST(lda.DepartmentID AS VARCHAR(20)) AS DeptID, lda.DepartmentAddressCity, lda.DepartmentAddressState, lda.DepartmentAddressZip
    FROM LatestDepartment ld
    INNER JOIN EE ee ON ld.EmployeeID = ee.ID
    LEFT JOIN LatestDepartmentAddress lda ON ld.EmployeeID = lda.EmployeeID AND ld.DepartmentID = lda.DepartmentID
    WHERE ld.rn = 1;
    <EXAMPLE>
    
    JSON for the Sources = {json_data_sources}
    JSON for the Targets = {json_data_target}
    '''

    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=payload, params={'key': api_key})

    if response.status_code == 200:
        data = json.loads(response.text)
        sql_code = data['candidates'][0]['content']['parts'][0]['text']
        sql_code = sql_code.strip('```')
        return sql_code
    else:
        return f'Error: {response.status_code} - {response.text}'

# Streamlit app
def app():
    st.title("SQL Query Generator")

    # Example JSON data
    json_data_sources = '[{"Column1": "Value1", "Column2": "Value2"}, {"Column1": "Value3", "Column2": "Value4"}]'
    json_data_target = '[{"Column1": "Value5", "Column2": "Value6"}, {"Column1": "Value7", "Column2": "Value8"}]'
    json_example_data_sources = '[{"Column1": "Value9", "Column2": "Value10"}, {"Column1": "Value11", "Column2": "Value12"}]'
    json_example_data_target = '[{"Column1": "Value13", "Column2": "Value14"}, {"Column1": "Value15", "Column2": "Value16"}]'

    # Create DataFrames from JSON data
    df_sources = pd.read_json(json_data_sources)
    df_target = pd.read_json(json_data_target)
    df_example_sources = pd.read_json(json_example_data_sources)
    df_example_target = pd.read_json(json_example_data_target)

    # Allow editing of DataFrames
    st.subheader("Edit Sources1 DataFrame")
    edited_df_sources = st.data_editor(df_sources)

    st.subheader("Edit Target1 DataFrame")
    edited_df_target = st.data_editor(df_target)

    st.subheader("Edit Sources2 DataFrame")
    edited_df_example_sources = st.data_editor(df_example_sources)

    st.subheader("Edit Target2 DataFrame")
    edited_df_example_target = st.data_editor(df_example_target)

    # Convert edited DataFrames to JSON
    json_data_sources = edited_df_sources.to_json(orient='records')
    json_data_target = edited_df_target.to_json(orient='records')
    json_example_data_sources = edited_df_example_sources.to_json(orient='records')
    json_example_data_target = edited_df_example_target.to_json(orient='records')

    # Generate SQL code
    sql_code = generate_sql(json_data_sources, json_data_target,json_example_data_sources,json_example_data_target)
    
    # Display SQL code
    st.subheader("Generated SQL Code")
    st.code(sql_code, language='sql')


if __name__ == "__main__":
    app()