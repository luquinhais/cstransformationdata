import streamlit as st
import pandas as pd

# Função para tratar os dados
def tratar_dados(df):
    df = df.applymap(lambda x: " ".join(x.split()) if isinstance(x, str) else x)
    df = df.applymap(lambda x: x.replace(" -> done", "") if isinstance(x, str) else x)
    df = df.rename(columns={"last used operated_desc": "macro"})
    
    iniciais_permitidas = ["[AF]", "[BD]", "[CL]", "[GN]", "[LG]", "[MKT]", "[OT]", "[PP]", "[RR]", "[SO]", 
                           "[PAY]", "[SPAY]", "[SHP]", "[SPL]", "[DIV]", "[DP]", "[LOG]", "[SP]"]
    df = df[df["macro"].str.startswith(tuple(iniciais_permitidas))]
    
    return df

# Configurações iniciais da página
st.set_page_config(page_title="Tratamento de Dados", layout="wide")

st.title("Tratamento de Dados")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Carregar arquivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Dados brutos")
    st.write(df.head())

    # Tratamento dos dados
    df_tratado = tratar_dados(df)
    
    # Exibição dos dados tratados
    st.write("Dados tratados")
    st.write(df_tratado.head())
    
    # Filtros
    iniciais_permitidas = ["[AF]", "[BD]", "[CL]", "[GN]", "[LG]", "[MKT]", "[OT]", "[PP]", "[RR]", "[SO]", 
                           "[PAY]", "[SPAY]", "[SHP]", "[SPL]", "[DIV]", "[DP]", "[LOG]", "[SP]"]
    
    st.sidebar.header("Filtros")
    filtros_iniciais = st.sidebar.multiselect("Selecione as iniciais", iniciais_permitidas, iniciais_permitidas)
    
    # Filtros adicionais para reason_code_l1_name
    unique_reason_code_l1_name = df_tratado['reason_code_l1_name'].unique()
    filtros_reason_code_l1_name = st.sidebar.multiselect("Selecione reason_code_l1_name", unique_reason_code_l1_name, unique_reason_code_l1_name)
    
    # Filtros adicionais para reason_code_l3_name
    unique_reason_code_l3_name = df_tratado['reason_code_l3_name'].unique()
    filtros_reason_code_l3_name = st.sidebar.multiselect("Selecione reason_code_l3_name", unique_reason_code_l3_name, unique_reason_code_l3_name)
    
    # Filtros adicionais para CSAT Level
    unique_csat_level = df_tratado['CSAT Level'].unique()
    filtros_csat_level = st.sidebar.multiselect("Selecione CSAT Level", unique_csat_level, unique_csat_level)

    if filtros_iniciais:
        df_filtrado = df_tratado[df_tratado["macro"].str.startswith(tuple(filtros_iniciais))]
        
    if filtros_reason_code_l1_name:
        df_filtrado = df_filtrado[df_filtrado["reason_code_l1_name"].isin(filtros_reason_code_l1_name)]
        
    if filtros_reason_code_l3_name:
        df_filtrado = df_filtrado[df_filtrado["reason_code_l3_name"].isin(filtros_reason_code_l3_name)]
        
    if filtros_csat_level:
        df_filtrado = df_filtrado[df_filtrado["CSAT Level"].isin(filtros_csat_level)]
        
    st.write("Dados filtrados")
    st.write(df_filtrado)
    
    # Baixar os dados tratados e filtrados
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Baixar CSV",
        data=csv,
        file_name='dados_tratados.csv',
        mime='text/csv',
    )
else:
    st.info("Por favor, carregue um arquivo CSV.")
