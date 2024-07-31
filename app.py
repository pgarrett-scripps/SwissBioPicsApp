import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

if 'selection' not in st.session_state:
    st.session_state['selection'] = []


@st.dialog('Add GO ID')
def add_go_id():
    go_id = st.number_input('GO ID', 1, key='go_id_add')
    color = st.color_picker('Color', '#FF0000', key='color_add')
    opacity = st.slider('Opacity', 0.0, 1.0, 0.5, 0.1, key='opacity_add')

    c1, c2 = st.columns(2)
    submit = c1.button('Add', use_container_width=True, type='primary', key='add_go_id')
    cancel = c2.button('Cancel', use_container_width=True, type='secondary', key='cancel_go_id')
    if submit:

        # if go_id already exists, error
        if go_id in [x[0] for x in st.session_state['selection']]:
            st.error(f'GO ID {go_id} already exists')
            st.stop()

        st.session_state['selection'].append((go_id, color, opacity))
        st.rerun()

    if cancel:
        st.rerun()


@st.dialog('Edit GO ID')
def edit_go_id(go_id, color, opacity):
    st.write(f'Editing {go_id}')
    color = st.color_picker('Color', color, key='color_edit')
    opacity = st.slider('Opacity', 0.0, 1.0, opacity, 0.1, key='opacity')
    c1, c2 = st.columns(2)
    if c1.button('Save', use_container_width=True, type='primary', key='save_go'):
        st.session_state['selection'] = [(go_id, color, opacity) if x[0] == go_id else x for x in
                                         st.session_state['selection']]
        st.rerun()
    if c2.button('Cancel', use_container_width=True, type='secondary', key='cancel_edit'):
        st.rerun()


with st.sidebar:
    st.title('Swiss Bio Pics')

    tax_id = st.number_input('Tax ID', value=9606)

    df = pd.DataFrame(st.session_state['selection'], columns=['ID', 'Color', 'Opacity'])
    selection = st.dataframe(df, use_container_width=True, hide_index=True, selection_mode='single-row',
                             on_select='rerun')
    selected_indices = [row for row in selection['selection']['rows']]
    selected_ids = [df.iloc[i].ID for i in selected_indices]

    selected_go_id = None
    if len(selected_ids) == 1:
        selected_go_id = selected_ids[0]

    c1, c2, c3, c4 = st.columns(4)
    if c1.button('Add', type='secondary', use_container_width=True):
        add_go_id()
    if c2.button('Delete', type='secondary', disabled=selected_go_id is None, use_container_width=True):
        st.session_state['selection'] = [x for x in st.session_state['selection'] if x[0] != selected_go_id]
        st.rerun()
    if c3.button('Edit', type='secondary', disabled=selected_go_id is None, use_container_width=True):
        edit_go_id(selected_go_id, *[x for x in st.session_state['selection'] if x[0] == selected_go_id][0][1:])
    if c4.button('Clear', type='secondary', use_container_width=True):
        st.session_state['selection'] = []
        st.rerun()

go_ids = list(map(str, [item[0] for item in st.session_state['selection']]))
go_styles = "\n".join(
    f"""
    svg .GO{go_id} *:not(text) {{fill:{color}; opacity:{opacity};}}
    svg .GO{go_id} *:not(path, .coloured) {{opacity:{opacity};}}
    svg .GO{go_id} .coloured {{stroke:black;}}
    svg .mp_GO{go_id} *:not(text) {{fill:{color}; opacity:{opacity};}}
    svg .mp_GO{go_id} *:not(path, .coloured) {{opacity:{opacity};}}
    svg .mp_GO{go_id} .coloured {{stroke:black;}}
    svg .part_GO{go_id} *:not(text) {{fill:{color}; opacity:{opacity};}}
    svg .part_GO{go_id} *:not(path, .coloured) {{opacity:{opacity};}}
    svg .part_GO{go_id} .coloured {{stroke:black;}}
    """
    for go_id, color, opacity in st.session_state['selection']
)

if not go_ids:
    st.warning('No GO IDs selected')
    st.stop()

html = f"""
<script type="module" src="https://www.swissbiopics.org/static/swissbiopics.js"></script>
<template id="sibSwissBioPicsSlLiItem">
    <li class="subcellular_location">
         <a class="subcell_name"></a>
         <span class="subcell_description"></span>
    </li>
</template>
<sib-swissbiopics-sl taxid="{tax_id}" gos="{','.join(go_ids)}"></sib-swissbiopics-sl>
<template id="sibSwissBioPicsStyle">
    <style>
        ul > li > a {{
            font-style: oblique;
        }}
        ul.notpresent li > .subcell_description {{
            display: none;
        }}
        {go_styles}
    </style>
</template>
"""

# Render the Lorikeet HTML
components.html(html, height=1000, width=1500, scrolling=True)
