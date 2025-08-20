import streamlit as st
import numpy as np
import plotly.graph_objects as go



def detect_peaks(data):
    avg_value = data.mean()
    std_value = data.std()
    threshold = avg_value + 1.5 * std_value

    above = data > threshold
    edges = np.diff(above.astype(int))
    rising_edges = np.where(edges == 1)[0]
    falling_edges = np.where(edges == -1)[0] + 1

    num_peaks = min(len(rising_edges), len(falling_edges))
    if num_peaks == 0:
        return None, None, None, threshold  # No peaks found

    peak_sample_indices = ((falling_edges[:num_peaks] + rising_edges[:num_peaks]) // 2).astype(int)
    return rising_edges, falling_edges, peak_sample_indices, threshold


y_min = np.inf
y_max = - np.inf


st.title("Upload BIN files")

uploaded_files = st.file_uploader(
    "Upload BIN files", 
    type=["bin"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded.")

    data_dict = {}

    for file in uploaded_files:
        filename = file.name
        extension = filename.split('.')[-1].lower()
        st.text(f"Processing: {filename}")

        try:
            if extension == 'bin':
                binary_data = file.read()
                if filename == "samples.bin":
                    binary_content = np.frombuffer(binary_data, dtype=np.uint32)
                else:
                    binary_content = np.frombuffer(binary_data, dtype=np.uint16)

                data_dict[filename] = binary_content

                # st.write(f"Number of elements: {len(binary_content)}")
                # st.code(binary_content[:100], language='python')

            else:
                st.warning(f"Unsupported file type: {extension}")

        except Exception as e:
            st.error(f"Error reading {filename}: {e}")

    if data_dict:
        
        if "bay_1_left_VL.bin" in data_dict:
            arr_b1LVL = data_dict["bay_1_left_VL.bin"]
            sample_indices = np.arange(len(arr_b1LVL))
            rising, falling, peaks, threshold = detect_peaks(arr_b1LVL)
            
            st.subheader("Overlayed Graph of All Files")

            fig = go.Figure()

            # for fname, arr in data_dict.items():
            for fname, arr in sorted(data_dict.items(), key=lambda x: x[0].lower()): ##sorted
                y_min = min(np.min(arr), y_min)
                y_max = max(np.max(arr), y_max)
                
                visible = True if fname == "bay_1_left_VL.bin" else 'legendonly'
                fig.add_trace(go.Scatter(
                    y=arr, 
                    mode='lines', 
                    name=fname, 
                    visible=visible, 
                    showlegend=True
                ))
                


            fig.update_layout(
                xaxis_title='Index',
                yaxis_title='Value',
                height=500,
                hovermode='x unified',
                showlegend=True
                # Removed itemclick to use default legend toggle behavior
            )
            
            # If peaks detected, add markers and threshold line
            if rising is not None and falling is not None and peaks is not None:
                # Rising edges (blue markers)
                fig.add_trace(go.Scatter(
                    x=rising,
                    y=arr_b1LVL[rising],
                    mode='markers',
                    name='Rising edges',
                    marker=dict(color='green', size=8, symbol='triangle-up')
                ))

                # Falling edges (red markers)
                fig.add_trace(go.Scatter(
                    x=falling,
                    y=arr_b1LVL[falling],
                    mode='markers',
                    name='Falling edges',
                    marker=dict(color='red', size=8, symbol='triangle-down')
                ))

                # Peak points (green markers)
                fig.add_trace(go.Scatter(
                    x=peaks,
                    y=arr_b1LVL[peaks],
                    mode='markers',
                    name='Peaks',
                    marker=dict(color='black', size=4, symbol='circle-dot')
                ))
                
                # for x in rising:
                #     fig.add_shape(
                #         type="line",
                #         x0=x, x1=x,
                #         y0=y_min, y1=y_max,
                #         line=dict(color="green", width=1, dash="dot"),
                #         opacity=0.5,
                #         layer="below"
                #     )

                # for x in falling:
                #     fig.add_shape(
                #         type="line",
                #         x0=x, x1=x,
                #         y0=y_min, y1=y_max,
                #         line=dict(color="red", width=1, dash="dot"),
                #         opacity=0.5,
                #         layer="below"
                #     )

                

                # Threshold line
                threshold_line = np.full(len(arr_b1LVL), threshold)
                fig.add_trace(go.Scatter(
                    y=threshold_line,
                    mode='lines',
                    name='Threshold',
                    line=dict(color='orange', width=2, dash='dash')
                ))

                # fig.add_shape(
                #     type="line",
                #     x0=0,
                #     y0=threshold,
                #     x1=len(arr_b1LVL),
                #     y1=threshold,
                #     line=dict(color="orange", width=2, dash="dash")
                # )

                # fig.add_annotation(
                #     x=len(arr_b1LVL) * 0.95,
                #     y=threshold,
                #     text=f"Threshold: {threshold:.2f}",
                #     showarrow=False,
                #     font=dict(color="orange"),
                #     bgcolor="rgba(255,255,255,0.7)"
                # )



                fig.update_layout(
                    xaxis_title='Index',
                    yaxis_title='Value',
                    height=500,
                    hovermode='x unified',
                    showlegend=True
                )

                st.plotly_chart(fig, use_container_width=True)

            
            
            
        else:
            rising = falling = peaks = None
            threshold = None
            st.error("No bay_1_left_VL.bin found ! ")
        
        
        
        
        # Select box to choose individual graph
        st.subheader("Select individual graph to display")
        # selected_file = st.selectbox("Choose a file", options=list(data_dict.keys()))

        sorted_filenames = sorted(data_dict.keys(), key=str.lower)
        selected_file = st.selectbox("Choose a file", options=sorted_filenames)

        if selected_file:
            fig_single = go.Figure()
            fig_single.add_trace(go.Scatter(
                y=data_dict[selected_file], 
                mode='lines', 
                name=selected_file
            ))

            fig_single.update_layout(
                xaxis_title='Index',
                yaxis_title='Value',
                height=500,
                hovermode='x unified'
            )
            


            st.plotly_chart(fig_single, use_container_width=True)



else:
    st.info("Please upload one or more files.")
