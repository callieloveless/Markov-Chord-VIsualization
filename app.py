import streamlit as st
import networkx as nx
import numpy as np
import random
import time
import plotly.graph_objects as go
import audio
from mingus.core import chords
import base64
import os

st.title("Markov Chord Progression Simulator")
st.markdown(""" 
    ### Instructions:
    - **Option 1:** Press the button below to generate a default chord progression.
    - **Option 2:** Enter your own custom chord progression (separate chords by spaces, e.g., `G Cm Gm9/E Eb7`).
""")

if 'chords_text' not in st.session_state:
    st.session_state.chords_text = ""

Jpop = st.button("Generate default JPop Chord Progression", key="Jpop")

if Jpop:
    st.session_state.chords_text = """F7 G Em9 Am
    F7 G Em Am
    F G G#dim7 Am7
    F E7 F C 
    F G Em Am
    F D G C 
    """

chords_text = st.text_input("Enter your custom chord progression:", st.session_state.chords_text)

if chords_text != st.session_state.chords_text:
    st.session_state.chords_text = chords_text

if not st.session_state.chords_text:
    st.info("Please either select the JPop button or enter your own chord progression.")
    st.stop()

chords_list = st.session_state.chords_text.split()

invalid_chords = []
for chord in chords_list:
    try:
        chords.from_shorthand(chord)
    except:
        invalid_chords.append(chord)

if invalid_chords:
    st.error(f"Invalid chords detected: {', '.join(invalid_chords)}. Please correct your input.")
    st.stop()

chords_list.append(chords_list[0])

frequences = {}
for i, chord in enumerate(chords_list[:-1], 0):
    chord_and_next = (chord, chords_list[i + 1])
    if chord_and_next not in frequences:
        frequences[chord_and_next] = 1
    else:
        frequences[chord_and_next] += 1

chord_names = sorted(list({chord for (chord, next_chord) in frequences}))

num_chords = len(chord_names)
adjacency_matrix = np.zeros((num_chords, num_chords), dtype=float)

for (source, target), weight in frequences.items():
    source_index = chord_names.index(source)
    target_index = chord_names.index(target)
    adjacency_matrix[source_index][target_index] = weight

transition_matrix = adjacency_matrix / adjacency_matrix.sum(axis=0)
G = nx.DiGraph()

for (source, target), weight in frequences.items():
    source_index = chord_names.index(source)
    target_index = chord_names.index(target)
    G.add_edge(source, target, weight=round(transition_matrix[source_index][target_index], 2))

pos = nx.circular_layout(G)

default_node_color = '#0074D9'
highlight_color = '#FF4136'

def create_plotly_graph(highlight_node=None):
    edge_trace = go.Scatter(
        x=[], y=[],
        line=dict(width=2, color='#888'),
        mode='lines'
    )
    
    edge_label_trace = go.Scatter(
        x=[], y=[],
        mode='text',
        text=[],
        textposition='middle center',
        showlegend=False  
    )

    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)
    
        weight = edge[2].get('weight', 1)
        edge_label_trace['x'] += ((x0 + x1) / 2,)
        edge_label_trace['y'] += ((y0 + y1) / 2,)
        edge_label_trace['text'] += (f"{weight}",)

    node_trace = go.Scatter(
        x=[], y=[],
        text=[], mode='markers+text',
        textposition='top center',
        hoverinfo='text',
        marker=dict(size=10, color=[], line=dict(width=2))
    )

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)
        color = highlight_color if node == highlight_node else default_node_color
        node_trace['marker']['color'] += (color,)
        node_trace['text'] += (node,)

    return edge_trace, edge_label_trace, node_trace

plotly_chart_placeholder = st.empty()

edge_trace, edge_label_trace, node_trace = create_plotly_graph(None)

if chords_list: 
    fig = go.Figure(data=[edge_trace, edge_label_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False),
                        title="Chord Transition Network"
                    ))

if 'highlighted_chord' not in st.session_state:
    st.session_state.highlighted_chord = None

st.info("Click on a starting chord for the Markov chain simulation")

columns = st.columns(len(chord_names))

for i in range(len(chord_names)):
    if columns[i].button(chord_names[i], key=chord_names[i]):
        st.session_state.highlighted_chord = chord_names[i]

clicked_node = st.session_state.highlighted_chord if st.session_state.highlighted_chord else chord_names[0]

steps = st.number_input("How many steps should the Markov chain simulate?", min_value=1, value=10, step=1)

# conversion to base64 is needed to have the mp3s autoplay  
def get_base64_audio(mp3_file_path):
    """Converts audio file to base64 string for streaming."""
    with open(mp3_file_path, "rb") as audio_file:
        encoded_string = base64.b64encode(audio_file.read()).decode()
    return f"data:audio/mp3;base64,{encoded_string}"

if st.button("Start Markov Chain"):
    index = chord_names.index(clicked_node)

    def markov_simulator(index):
        """Simulates the markov chain by playing audio 
        and updating the graph at each step"""
        sequence = [clicked_node]
        for i in range(steps):
            chord = chord_names[index]
            sequence.append(chord)

            st.write(f"Chord {i+1}: {chord}")
            st.session_state.highlighted_chord = chord

            highlight_node = st.session_state.highlighted_chord
            edge_trace, edge_label_trace, node_trace = create_plotly_graph(highlight_node)

            plotly_chart_placeholder.plotly_chart(
                go.Figure(data=[edge_trace, edge_label_trace, node_trace],
                           layout=go.Layout(
                               showlegend=False,
                               xaxis=dict(showgrid=False, zeroline=False),
                               yaxis=dict(showgrid=False, zeroline=False),
                               title="Chord Transition Network"
                           )),
                use_container_width=True
            )

            audio.play_chord(chord)
            sanitized_chord_name = chord.replace('/', 'slash')
            mp3_file_path = f"{sanitized_chord_name}.mp3"
            print("Waiting for audio file to be created...")
            while not os.path.exists(mp3_file_path):
                time.sleep(0.1) 

            audio_base64 = get_base64_audio(mp3_file_path)

            st.markdown(f'<audio controls autoplay><source src="{audio_base64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            time.sleep(2.5)  

            col = [idx for idx in range(len(transition_matrix))]
            row_prob = [p for p in transition_matrix[:, index]]
            index = np.random.choice(col, 1, p=row_prob)[0]
        return sequence

    st.write("Generated Chord Sequence:")
    st.write(markov_simulator(index))

if 'highlighted_chord' in st.session_state:
    plotly_chart_placeholder.plotly_chart(fig, use_container_width=True)
