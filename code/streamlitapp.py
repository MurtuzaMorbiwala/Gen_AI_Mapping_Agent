import streamlit as st
import pandas as pd
import json
import requests
#from dotenv import load_dotenv
import os

## Load environment variables
#load_dotenv()
#api_key = os.getenv('GEMINI_API_KEY')

api_key = st.secrets["API_KEY"]

# Function to generate SQL code
def generate_sql(json_data_sources, json_data_target,json_example_data_sources,json_example_data_target,example_query):
    prompt = f'''
    You are an accurate SQL mapping assistant. Write a SQL query that uses the sources and maps to the target definition. The JSONs contain the metadata of the sources and targets. Important: Do not use the JSON in the SQL. The SQL should be accurate and should not contain any errors. The SQL should be modular but without unnecessary repetition.

    <EXAMPLE>
    JSON for the Sources = {json_example_data_sources}
    JSON for the Targets = {json_example_data_target}
    
    query : {example_query}
    
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
    st.set_page_config(layout="wide")
    st.title("SQL Query Generator")

    # Example JSON data
    json_data_sources = '[{"SourceTableName":"Ptnt101","SourceColumnName ":"ID","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"patient table","Nullable":"N"},{"SourceTableName":"Ptnt101","SourceColumnName ":"firstname","SourceColumnDataType":"varchar","UniqueDataValues ":"Raj,Kamal","TableDescription":"patient table","Nullable":"Y"},{"SourceTableName":"Ptnt101","SourceColumnName ":"lastname","SourceColumnDataType":"varchar","UniqueDataValues ":"Kumar,Hassan","TableDescription":"patient table","Nullable":"Y"},{"SourceTableName":"PTINS101","SourceColumnName ":"ptntid","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"patient insurance bridge","Nullable":"N"},{"SourceTableName":"PTINS101","SourceColumnName ":"insid","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"patient insurance bridge","Nullable":"N"},{"SourceTableName":"PTINS101","SourceColumnName ":"ValidFrom","SourceColumnDataType":"Date","UniqueDataValues ":"1,2","TableDescription":"patient insurance bridge","Nullable":"N"},{"SourceTableName":"ADD101","SourceColumnName ":"ID","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"address table","Nullable":"N"},{"SourceTableName":"ADD101","SourceColumnName ":"Address Line 1","SourceColumnDataType":"varchar","UniqueDataValues ":"504 church street,101 gated road","TableDescription":"address table","Nullable":"Y"},{"SourceTableName":"ADD101","SourceColumnName ":"City ","SourceColumnDataType":"varchar","UniqueDataValues ":"mumbai,pune","TableDescription":"address table","Nullable":"Y"},{"SourceTableName":"ADD101","SourceColumnName ":"State ","SourceColumnDataType":"varchar","UniqueDataValues ":"maharastra,maharastra","TableDescription":"address table","Nullable":"Y"},{"SourceTableName":"ADD101","SourceColumnName ":"Zip","SourceColumnDataType":"varchar","UniqueDataValues ":"400050 ,  400093","TableDescription":"address table","Nullable":"Y"},{"SourceTableName":"ADD101","SourceColumnName ":"ValidFrom","SourceColumnDataType":"Date","UniqueDataValues ":"10-10-2024,11-10-2024","TableDescription":"address table","Nullable":"N"},{"SourceTableName":"ADD101","SourceColumnName ":"AddType","SourceColumnDataType":"varchar","UniqueDataValues ":"H,I","TableDescription":"address table","Nullable":"N"},{"SourceTableName":"ADD101","SourceColumnName ":"INSID","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"address table","Nullable":"Y"},{"SourceTableName":"ADD101","SourceColumnName ":"ptntid","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"address table","Nullable":"N"},{"SourceTableName":"INS101","SourceColumnName ":"Id","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"insurance table","Nullable":"N"},{"SourceTableName":"INS101","SourceColumnName ":"name","SourceColumnDataType":"varchar","UniqueDataValues ":"HomeInsuranceforAll,Grownups","TableDescription":"insurance table","Nullable":"N"}]'  
    json_data_target = '[{"TargetTableName":"PATIENT","TargetColumnName":"PatientId","TargetExplanation":"unique patient id","TargetColumnDataType":"varchar"},{"TargetTableName":"PATIENT","TargetColumnName":"PatientName","TargetExplanation":"patient full name","TargetColumnDataType":"varchar"},{"TargetTableName":"PATIENT","TargetColumnName":"InsuranceName","TargetExplanation":"latest Insurance using valid from date from patient insurance bridge table","TargetColumnDataType":"varchar"},{"TargetTableName":"PATIENT","TargetColumnName":"InsuranceId","TargetExplanation":"latest Insurance using valid from date from patient insurance bridge table","TargetColumnDataType":"varchar"},{"TargetTableName":"PATIENT","TargetColumnName":"InsuranceAddressLine1","TargetExplanation":"Latest Insurance Address using valid from date for each patient , insurance","TargetColumnDataType":"varchar"},{"TargetTableName":"PATIENT","TargetColumnName":"InsuranceCity","TargetExplanation":"Latest Insurance Address using valid from date for each patient , insurance","TargetColumnDataType":"varchar"},{"TargetTableName":"PATIENT","TargetColumnName":"InsuranceState","TargetExplanation":"Latest Insurance Address using valid from date for each patient , insurance","TargetColumnDataType":"varchar"},{"TargetTableName":"PATIENT","TargetColumnName":"InsuranceZip","TargetExplanation":"Latest Insurance Address using valid from date for each patient , insurance","TargetColumnDataType":"varchar"},{"TargetTableName":"PATIENT","TargetColumnName":"AddressLine1","TargetExplanation":"Latest  home address from the address table using valid from date disregarding the insurance.","TargetColumnDataType":"varchar"},{"TargetTableName":"PATIENT","TargetColumnName":"City ","TargetExplanation":"Latest  home address from the address table using valid from date disregarding the insurance.","TargetColumnDataType":"varchar"},{"TargetTableName":"PATIENT","TargetColumnName":"State ","TargetExplanation":"Latest  home address from the address table using valid from date disregarding the insurance.","TargetColumnDataType":"varchar"},{"TargetTableName":"PATIENT","TargetColumnName":"Zip","TargetExplanation":"Latest  home address from the address table using valid from date disregarding the insurance.","TargetColumnDataType":"varchar"}]'
    json_example_data_sources = '[{"SourceTableName":"EE","SourceColumnName ":"ID","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"Employee table","Nullable":"N"},{"SourceTableName":"EE","SourceColumnName ":"firstname","SourceColumnDataType":"varchar","UniqueDataValues ":"Raj,Kamal","TableDescription":"Employee table","Nullable":"Y"},{"SourceTableName":"EE","SourceColumnName ":"lastname","SourceColumnDataType":"varchar","UniqueDataValues ":"Kumar,Hassan","TableDescription":"Employee table","Nullable":"Y"},{"SourceTableName":"Dep","SourceColumnName ":"ID","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"Department Table","Nullable":"N"},{"SourceTableName":"Dep","SourceColumnName ":"name","SourceColumnDataType":"varchar","UniqueDataValues ":"Finance,Sales","TableDescription":"Department Table","Nullable":"N"},{"SourceTableName":"ED","SourceColumnName ":"EMPID","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"Employee Department table","Nullable":"N"},{"SourceTableName":"ED","SourceColumnName ":"DEPID","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"Employee Department table","Nullable":"N"},{"SourceTableName":"ED","SourceColumnName ":"ValidFrom","SourceColumnDataType":"Date","UniqueDataValues ":"01-10-2020,01-01-2018","TableDescription":"Employee Department table","Nullable":"Y"},{"SourceTableName":"AD","SourceColumnName ":"City ","SourceColumnDataType":"varchar","UniqueDataValues ":"Ahmedabad,Goa","TableDescription":"address table","Nullable":"Y"},{"SourceTableName":"AD","SourceColumnName ":"State ","SourceColumnDataType":"varchar","UniqueDataValues ":"Gujarat,maharastra","TableDescription":"address table","Nullable":"Y"},{"SourceTableName":"AD","SourceColumnName ":"Zip","SourceColumnDataType":"varchar","UniqueDataValues ":"400050 ,  400093","TableDescription":"address table","Nullable":"Y"},{"SourceTableName":"AD","SourceColumnName ":"ValidFrom","SourceColumnDataType":"Date","UniqueDataValues ":"01-10-2000,01-01-2005","TableDescription":"address table","Nullable":"N"},{"SourceTableName":"AD","SourceColumnName ":"DEPID","SourceColumnDataType":"int","UniqueDataValues ":"1,2","TableDescription":"address table","Nullable":"N"}]'
    json_example_data_target = '[{"TargetTableName":"Employee","TargetColumnName":"EmployeeID","TargetExplanation":"unique patient id","TargetColumnDataType":"varchar"},{"TargetTableName":"Employee","TargetColumnName":"EmployeeName","TargetExplanation":"patient full name","TargetColumnDataType":"varchar"},{"TargetTableName":"Employee","TargetColumnName":"DeptName","TargetExplanation":"Latest Department Name using valid from","TargetColumnDataType":"varchar"},{"TargetTableName":"Employee","TargetColumnName":"DeptID","TargetExplanation":"Latest Department ID using valid from","TargetColumnDataType":"varchar"},{"TargetTableName":"Employee","TargetColumnName":"DeptAddressCity","TargetExplanation":"Latest  Address for Latest Department using valid from","TargetColumnDataType":"varchar"},{"TargetTableName":"Employee","TargetColumnName":"DeptAddressState","TargetExplanation":"Latest  Address for Latest Department using valid from","TargetColumnDataType":"varchar"},{"TargetTableName":"Employee","TargetColumnName":"DeptAddressZip","TargetExplanation":"Latest  Address for Latest Department using valid from","TargetColumnDataType":"varchar"}]'
    example_query ='''-- CTE for Latest Department
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
    '''

    # Create DataFrames from JSON data
    df_sources = pd.read_json(json_data_sources)
    df_target = pd.read_json(json_data_target)
    df_example_sources = pd.read_json(json_example_data_sources)
    df_example_target = pd.read_json(json_example_data_target)

    # Allow editing of DataFrames
    st.subheader("Data Mapping Agent takes Sources and Target information and provides a query to Map them")
    st.subheader("For Few Shot Learning We Provide an Example")
    st.subheader("Sources Metadata")
    edited_df_example_sources = st.data_editor(df_example_sources)

    st.subheader("Target Metadata")
    edited_df_example_target = st.data_editor(df_example_target)

    st.subheader("Example Query")
    edited_example_query = st.text_area("Example Query", example_query, height=300)
    
    
    st.subheader("")
    st.subheader("Now We Provide The Medatadata for the Mapping We Need")
    st.subheader("Then Click Generate SQL for your Mapping Query")

    st.subheader("Edit Your Sources Metadata")
    edited_df_sources = st.data_editor(df_sources)

    st.subheader("Edit Your Target Metadata")
    edited_df_target = st.data_editor(df_target)

    # Convert edited DataFrames to JSON
    json_data_sources = edited_df_sources.to_json(orient='records')
    json_data_target = edited_df_target.to_json(orient='records')
    json_example_data_sources = edited_df_example_sources.to_json(orient='records')
    json_example_data_target = edited_df_example_target.to_json(orient='records')
    
    if st.button("Generate SQL Code"):
        # Generate SQL code
        sql_code = generate_sql(json_data_sources, json_data_target,json_example_data_sources,json_example_data_target,example_query)
    
        # Display SQL code
        st.subheader("Generated SQL Code")
        st.code(sql_code, language='sql')


if __name__ == "__main__":
    app()