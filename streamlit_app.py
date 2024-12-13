import streamlit as st
import pandas as pd
import altair as alt

# Carica i file CSV caricati dall'utente
st.title("Dashboard Interattiva per Visualizzazione Dati")
st.sidebar.header("Caricamento dati")

uploaded_files = st.sidebar.file_uploader("Carica uno o più file CSV", accept_multiple_files=True, type="csv")

if uploaded_files:
    st.sidebar.success(f"{len(uploaded_files)} file caricati con successo!")

    # Dizionario per contenere i dati
    datasets = {}

    # Legge i file caricati
    for file in uploaded_files:
        datasets[file.name] = pd.read_csv(file)

    # Seleziona i dataset da visualizzare
    dataset_names = list(datasets.keys())
    st.sidebar.subheader("Selezione Dataset")

    selected_datasets = st.sidebar.multiselect("Seleziona uno o più dataset", options=dataset_names,
                                               default=dataset_names)

    if selected_datasets:
        combined_data = pd.DataFrame()

        for name in selected_datasets:
            data = datasets[name]
            data['Dataset'] = name  # Aggiunge una colonna per identificare il dataset

            # Rimuovi eventuali spazi o caratteri speciali dai nomi delle colonne
            data.columns = [col.replace(" ", "_").replace("[", "").replace("]", "") for col in data.columns]

            combined_data = pd.concat([combined_data, data], ignore_index=True)

        # Mostra una tabella con i dati combinati
        st.subheader("Anteprima dei Dati Combinati")

        # Dividi i dati in pagine per evitare di sovraccaricare la visualizzazione
        page_size = st.sidebar.slider("Numero di righe per pagina", min_value=1, max_value=100, value=20)
        num_pages = (len(combined_data) + page_size - 1) // page_size  # Calcola il numero di pagine

        # Visualizza i dati sulla pagina selezionata
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0

        page = st.session_state.current_page
        start_idx = page * page_size
        end_idx = start_idx + page_size
        paged_data = combined_data.iloc[start_idx:end_idx]

        # Visualizza i dati paginati
        st.write(paged_data)

        # Pulsanti di navigazione per le pagine
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Pagina Precedente") and st.session_state.current_page > 0:
                st.session_state.current_page -= 1

        with col2:
            if st.button("Pagina Successiva") and st.session_state.current_page < num_pages - 1:
                st.session_state.current_page += 1

        st.write("")  # Spazio vuoto tra i pulsanti e i dati

        # Selezione delle colonne
        columns = combined_data.columns.tolist()
        st.sidebar.subheader("Configurazione del Bar Chart")

        x_column = st.sidebar.selectbox("Seleziona la colonna X", options=columns)
        y_column = st.sidebar.selectbox("Seleziona la colonna Y", options=columns)

        # Filtra i dati con una checkbox
        unique_values = combined_data[x_column].unique()
        selected_values = st.sidebar.multiselect(
            f"Seleziona i valori da visualizzare per {x_column}", options=unique_values
        )

        if selected_values:
            # Assicura che i valori siano formattati correttamente per il confronto
            combined_data[x_column] = combined_data[x_column].round(10)  # Adjust the number of decimals as needed
            filtered_data = combined_data[combined_data[x_column].isin(selected_values)]
        else:
            filtered_data = combined_data

        # Genera il grafico
        st.subheader("Bar Chart Interattivo")
        chart = (
            alt.Chart(filtered_data)
            .mark_bar()
            .encode(
                x=alt.X(x_column, title=f"{x_column}"),
                y=alt.Y(y_column, title=f"{y_column}"),
                color='Dataset',
                tooltip=[x_column, y_column, 'Dataset']
            )
            .interactive()
        )

        st.altair_chart(chart, use_container_width=True)

    else:
        st.warning("Seleziona almeno un dataset per continuare.")

else:
    st.warning("Carica almeno un file CSV per iniziare.")
