from io import StringIO

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

@st.dialog('Paste')
def paste_go_ids():
    input_data = st.text_area('Paste GO IDs', key='paste_go_ids')

    # Check if input_data is empty
    if not input_data.strip():
        st.error('Please enter valid GO ID data')
        st.stop()

    # Try to read the pasted data
    try:
        go_ids = pd.read_csv(StringIO(input_data), sep='\t')
    except Exception as e:
        st.error(f'Error reading data: {e}')
        st.stop()

    # Ensure required columns exist
    required_columns = {'ID', 'Color', 'Opacity'}
    if not required_columns.issubset(go_ids.columns):
        missing = required_columns - set(go_ids.columns)
        st.error(f'Missing columns in input: {", ".join(missing)}')
        st.stop()

    c1, c2 = st.columns(2)
    submit = c1.button('Add', use_container_width=True, type='primary', key='add_go_id')
    cancel = c2.button('Cancel', use_container_width=True, type='secondary', key='cancel_go_id')

    # Handle Add button click
    if submit:
        for _, row in go_ids.iterrows():
            go_id = int(row['ID'])
            color = str(row['Color'])
            opacity = float(row['Opacity'])
            # Ensure color starts with '#'
            color = color if color.startswith('#') else f'#{color}'
            # Check if the GO ID already exists in the session state
            if go_id in [x[0] for x in st.session_state['selection']]:

                # remove existing entry
                st.session_state['selection'] = [x for x in st.session_state['selection'] if x[0] != go_id]

            # Add new GO ID entry
            st.session_state['selection'].append((go_id, color, opacity))

        st.rerun()

    # Handle Cancel button click
    if cancel:
        st.rerun()

@st.dialog('Copy')
def copy_go_ids():
    # Display current selection in DataFrame format
    if st.session_state['selection']:
        curr_data = pd.DataFrame(st.session_state['selection'], columns=['ID', 'Color', 'Opacity'])
        txt = curr_data.to_csv(index=False, sep='\t')
        st.code(txt, language='text')
    else:
        st.warning('No GO IDs to display')

    # Cancel button to close dialog
    cancel = st.button('Cancel', use_container_width=True, type='secondary', key='cancel_copy_go_id')

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

    st.subheader('Selection', divider=True)

    selection = st.dataframe(df, use_container_width=True, hide_index=True, selection_mode='single-row',
                             on_select='rerun')
    selected_indices = [row for row in selection['selection']['rows']]
    selected_ids = [df.iloc[i].ID for i in selected_indices]

    selected_go_id = None
    if len(selected_ids) == 1:
        selected_go_id = selected_ids[0]

    st.subheader('Single Operations', divider=True)

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

    st.subheader('Bulk Operations', divider=True)

    c1, c2 = st.columns(2)
    if c1.button('Paste', type='secondary', use_container_width=True):
        paste_go_ids()
    if c2.button('Copy', type='secondary', use_container_width=True):
        copy_go_ids()

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
<template id="sibSwissBioPicsSlLiItem" style="display:none;">
    <tr class="subcellular_location" style="display:none;">
         <td><a class="subcell_name"></a></td>
         <td class="subcell_description"></td>
    </tr>
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
        svg .subcell_name {{
            display: none;
        }}
        svg .subcell_description {{
            display: none;
        }}
        {go_styles}
    </style>
</template>
"""


# Render the Lorikeet HTML
components.html(html, height=1000, width=2000, scrolling=True)
