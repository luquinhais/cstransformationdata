import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

# Função para carregar os dados principais
def load_data(file):
    data = pd.read_csv(file)
    
    # Remover espaços em branco antes e depois das frases
    data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Remover a string " ->" da coluna "last_used_operated_desc"
    if 'last_used_operated_desc' in data.columns:
        data['last_used_operated_desc'] = data['last_used_operated_desc'].str.replace(" ->", "")
    
    data['cdate'] = pd.to_datetime(data['cdate'])  # Convertendo 'cdate' para datetime
    data['week'] = data['cdate'].dt.isocalendar().week  # Extraindo a semana
    data['month'] = data['cdate'].dt.to_period('M')  # Extraindo o mês
    return data

# Função para calcular CSAT e DSAT com seleção reversa de macros
def calculate_csat_dsat(data, freq, selected_macros=None):
    if selected_macros:
        data = data[data['macro'].isin(selected_macros)]
    
    if freq == 'Weekly':
        grouped = data.groupby(['week', 'macro', 'CSAT Level']).size().unstack(fill_value=0)
    elif freq == 'Monthly':
        grouped = data.groupby(['month', 'macro', 'CSAT Level']).size().unstack(fill_value=0)
    
    grouped['total'] = grouped.sum(axis=1)
    grouped['CSAT'] = grouped['Good'] / grouped['total']
    grouped['DSAT'] = grouped['Bad'] / grouped['total']
    return grouped.reset_index()

# Função para destacar valores de CSAT acima de 80%
def highlight_csat(val):
    color = 'green' if val > 0.8 else ''
    return f'background-color: {color}'

# Função para calcular estatísticas descritivas
def calculate_statistics(data, column):
    # Converter a coluna para numérica, ignorando erros
    data[column] = pd.to_numeric(data[column], errors='coerce')
    desc = data[column].describe()
    
    # Identificar outliers
    z_scores = np.abs(stats.zscore(data[column].dropna()))
    outliers = data.loc[data[column].dropna().index[z_scores > 3]]
    
    return desc, outliers

# Configuração da página
st.set_page_config(page_title="CSAT Analysis", layout="wide")

# Título da aplicação
st.title("CSAT Analysis")

# Carregamento do arquivo CSV principal para análise de CSAT
uploaded_file = st.file_uploader("Upload your main CSV file", type="csv")

# Estrutura para exibir a análise de CSAT
if uploaded_file is not None:
    # Carregar e exibir os dados principais
    data = load_data(uploaded_file)
    st.write("Dados Carregados:")
    st.dataframe(data.head())

    # Filtrar dados, excluindo 'Neutral'
    data_filtered = data[data['CSAT Level'].isin(['Good', 'Bad'])]

    # Seleção de frequência de cálculo
    freq = st.selectbox("Selecione a frequência de cálculo", ['Weekly', 'Monthly'])

    # Seleção reversa de macros para CSAT
    all_macros_csat = data_filtered['macro'].unique()
    selected_macros_csat = st.multiselect("Selecione as macros para CSAT", all_macros_csat)

    # Calcular CSAT e DSAT com seleção reversa de macros
    results_csat = calculate_csat_dsat(data_filtered, freq, selected_macros_csat)
    
    # Aplicar destaque aos valores de CSAT
    styled_results_csat = results_csat.style.applymap(highlight_csat, subset=['CSAT'])
    
    # Exibir resultados de CSAT
    st.write(f"Resultados CSAT & DSAT ({freq}):")
    st.dataframe(styled_results_csat)
    
    # Opção para download dos resultados de CSAT
    csv_csat = results_csat.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download resultados CSAT como CSV", data=csv_csat, file_name=f'csat_dsat_results_{freq.lower()}.csv', mime='text/csv')

    # Agrupar e contar valores da coluna 'macro'
    st.write("## Agrupamento por macro")
    macro_counts = data['macro'].value_counts().reset_index()
    macro_counts.columns = ['macro', 'count']
    st.dataframe(macro_counts)

    # Agrupar e contar valores da coluna 'reason_code_l3_name'
    st.write("## Agrupamento por reason_code_l3_name")
    reason_code_counts = data['reason_code_l3_name'].value_counts().reset_index()
    reason_code_counts.columns = ['reason_code_l3_name', 'count']
    st.dataframe(reason_code_counts)

    # Calcular estatísticas descritivas para 'AHT(s)'
    st.write("## Estatísticas descritivas para AHT(s)")
    if 'AHT(s)' in data.columns:
        data['AHT(s)'] = pd.to_numeric(data['AHT(s)'], errors='coerce')
        aht_desc, aht_outliers = calculate_statistics(data, 'AHT(s)')
        st.write(aht_desc)
        if not aht_outliers.empty:
            st.write("Outliers em AHT(s):")
            st.dataframe(aht_outliers)
    else:
        st.write("Coluna 'AHT(s)' não encontrada nos dados.")

    # Calcular estatísticas descritivas para 'Case E2E (day)'
    st.write("## Estatísticas descritivas para Case E2E (day)")
    if 'Case E2E (day)' in data.columns:
        data['Case E2E (day)'] = pd.to_numeric(data['Case E2E (day)'], errors='coerce')
        case_e2e_desc, case_e2e_outliers = calculate_statistics(data, 'Case E2E (day)')
        st.write(case_e2e_desc)
        if not case_e2e_outliers.empty:
            st.write("Outliers em Case E2E (day):")
            st.dataframe(case_e2e_outliers)
    else:
        st.write("Coluna 'Case E2E (day)' não encontrada nos dados.")

else:
    st.write("Por favor, carregue um arquivo CSV principal para iniciar a análise de CSAT.")
