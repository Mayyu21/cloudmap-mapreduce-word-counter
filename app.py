
import csv
import io
import time
from collections import Counter

import pandas as pd
import streamlit as st

from main import sequential_word_count, parallel_word_count


st.set_page_config(
    page_title="CloudMap | MapReduce Analytics",
    page_icon="☁️",
    layout="wide",
)

st.title("☁️ CloudMap")
st.subheader("MapReduce Word Count & Analytics Platform")
st.caption(
    "Upload a text dataset, process words using MapReduce, "
    "and compare sequential and parallel execution."
)

with st.sidebar:
    st.header("About CloudMap")
    st.write("A Python-based MapReduce analytics application.")
    st.markdown("**Processing pipeline**")
    st.write("1. Upload dataset")
    st.write("2. Split text into chunks")
    st.write("3. Map words in parallel")
    st.write("4. Shuffle and reduce counts")
    st.write("5. Analyze results")

    st.info(
        "This version runs on the machine hosting the app. "
        "It does not yet use a distributed cluster."
    )

uploaded_file = st.file_uploader(
    "Upload a text file",
    type=["txt"],
    help="Choose a UTF-8 text file to analyze.",
)

if uploaded_file is not None:
    try:
        text = uploaded_file.getvalue().decode("utf-8")
    except UnicodeDecodeError:
        st.error("Please upload a valid UTF-8 text file.")
        st.stop()

    if not text.strip():
        st.warning("The uploaded file is empty.")
        st.stop()

    st.success(f"Dataset loaded: {uploaded_file.name}")

    if st.button("Run MapReduce Analysis", type="primary"):
        with st.spinner("Processing your dataset..."):
            start = time.perf_counter()
            sequential_result = sequential_word_count(text)
            sequential_time = time.perf_counter() - start

            start = time.perf_counter()
            parallel_result = parallel_word_count(text)
            parallel_time = time.perf_counter() - start

        results_match = sequential_result == parallel_result
        total_words = sum(parallel_result.values())
        unique_words = len(parallel_result)

        st.session_state["cloudmap_results"] = {
            "counts": dict(parallel_result),
            "sequential_time": sequential_time,
            "parallel_time": parallel_time,
            "results_match": results_match,
            "total_words": total_words,
            "unique_words": unique_words,
            "filename": uploaded_file.name,
        }

if "cloudmap_results" in st.session_state:
    result = st.session_state["cloudmap_results"]
    counts = result["counts"]

    st.divider()
    st.header("Analysis Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Words", f'{result["total_words"]:,}')
    col2.metric("Unique Words", f'{result["unique_words"]:,}')
    col3.metric("Sequential Time", f'{result["sequential_time"]:.4f} s')
    col4.metric("Parallel Time", f'{result["parallel_time"]:.4f} s')

    if result["results_match"]:
        st.success("Verification passed: Both methods produced identical counts.")
    else:
        st.error("Verification failed: The word counts do not match.")

    st.subheader("MapReduce Workflow")

    stage1, stage2, stage3 = st.columns(3)

    stage1.info("**MAP**\n\nExtract words and generate intermediate counts.")
    stage2.info("**SHUFFLE**\n\nGroup counts belonging to the same word.")
    stage3.info("**REDUCE**\n\nCombine counts to calculate final frequencies.")

    st.subheader("Most Frequent Words")

    top_n = st.slider(
        "Number of words to display",
        min_value=5,
        max_value=min(30, len(counts)),
        value=min(10, len(counts)),
    )

    top_words = sorted(
        counts.items(),
        key=lambda item: (-item[1], item[0]),
    )[:top_n]

    chart_data = pd.DataFrame(top_words, columns=["Word", "Count"])
    chart_data = chart_data.set_index("Word")
    st.bar_chart(chart_data)

    st.subheader("Complete Word Count Table")

    table_data = pd.DataFrame(
        sorted(counts.items()),
        columns=["Word", "Count"],
    )
    st.dataframe(table_data, use_container_width=True, hide_index=True)

    st.subheader("Performance Comparison")

    comparison = pd.DataFrame({
        "Method": ["Sequential", "Parallel MapReduce"],
        "Time (seconds)": [
            result["sequential_time"],
            result["parallel_time"],
        ],
    })

    st.bar_chart(comparison.set_index("Method"))

    if result["parallel_time"] < result["sequential_time"]:
        st.write("Parallel execution was faster in this run.")
    else:
        st.write(
            "Sequential execution was faster in this run. "
            "Parallel processing overhead can affect small workloads."
        )

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["Word", "Count"])

    for word, count in sorted(counts.items()):
        writer.writerow([word, count])

    st.download_button(
        "Download Word Counts (CSV)",
        data=csv_buffer.getvalue(),
        file_name="cloudmap_word_counts.csv",
        mime="text/csv",
    )

    report = (
        "CLOUDMAP - MAPREDUCE EXECUTION REPORT\n"
        f'Input file: {result["filename"]}\n'
        f'Total words: {result["total_words"]}\n'
        f'Unique words: {result["unique_words"]}\n'
        f'Sequential time: {result["sequential_time"]:.6f} seconds\n'
        f'Parallel time: {result["parallel_time"]:.6f} seconds\n'
        f'Results match: {result["results_match"]}\n'
    )

    st.download_button(
        "Download Execution Report",
        data=report,
        file_name="cloudmap_execution_report.txt",
        mime="text/plain",
    )

else:
    st.info("Upload a text file and click Run MapReduce Analysis to begin.")
