
import re
import time
import multiprocessing
from collections import Counter
from pathlib import Path


def map_words(text_chunk):
    """MAP: Convert a text chunk into (word, 1) pairs."""
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text_chunk.lower())
    return [(word, 1) for word in words]


def reduce_counts(mapped_words):
    """REDUCE: Add the counts for each word."""
    counts = Counter()
    for word, count in mapped_words:
        counts[word] += count
    return counts


def sequential_word_count(text):
    """Count words using a single process."""
    mapped_words = map_words(text)
    return reduce_counts(mapped_words)



def parallel_word_count(text):
    """MAPREDUCE: Map chunks in parallel, then shuffle and reduce."""

    # Split the text by lines so words are not cut at chunk boundaries.
    lines = text.splitlines()

    if not lines:
        return Counter()

    # Each worker receives complete lines.
    number_of_workers = min(multiprocessing.cpu_count(), len(lines))
    chunk_size = (len(lines) + number_of_workers - 1) // number_of_workers

    chunks = [
        "\n".join(lines[i:i + chunk_size])
        for i in range(0, len(lines), chunk_size)
    ]

    with multiprocessing.Pool(processes=number_of_workers) as pool:
        mapped_chunks = pool.map(map_words, chunks)

    # Shuffle and reduce: combine counts from all chunks.
    combined_counts = Counter()
    for chunk_result in mapped_chunks:
        combined_counts.update(reduce_counts(chunk_result))

    return combined_counts



def main():
    input_file = Path(__file__).parent / "input.txt"

    if not input_file.exists():
        print("Error: input.txt was not found.")
        return

    text = input_file.read_text(encoding="utf-8")

    if not text.strip():
        print("Error: input.txt is empty.")
        return

    print("=" * 55)
    print("       MAPREDUCE WORD COUNTER")
    print("=" * 55)

    # Sequential execution
    start = time.perf_counter()
    sequential_result = sequential_word_count(text)
    sequential_time = time.perf_counter() - start

    # Parallel MapReduce execution
    start = time.perf_counter()
    parallel_result = parallel_word_count(text)
    parallel_time = time.perf_counter() - start

    print("\nWORD COUNTS")
    print("-" * 55)

    for word, count in sorted(parallel_result.items()):
        print(f"{word:<25} : {count}")

    print("\nPERFORMANCE COMPARISON")
    print("-" * 55)
    print(f"Sequential execution : {sequential_time:.6f} seconds")
    print(f"Parallel execution   : {parallel_time:.6f} seconds")

    if sequential_result == parallel_result:
        print("\nVerification: Both methods produced identical results.")
    else:
        print("\nVerification: Results do not match.")

    if parallel_time < sequential_time:
        print("Result: Parallel execution was faster for this run.")
    else:
        print("Result: Sequential execution was faster for this run.")
        print("Note: Small inputs often run faster sequentially because")
        print("parallel processing has startup and communication overhead.")

    print("\nTotal words:", sum(parallel_result.values()))
    print("Unique words:", len(parallel_result))
    print("\nProject executed successfully!")

    # Save the execution results
    output_file = Path(__file__).parent / "output.txt"

    with output_file.open("w", encoding="utf-8") as file:
        file.write("MAPREDUCE WORD COUNTER - EXECUTION REPORT\n")
        file.write("=" * 55 + "\n\n")

        file.write("WORD COUNTS\n")
        file.write("-" * 55 + "\n")

        for word, count in sorted(parallel_result.items()):
            file.write(f"{word:<25} : {count}\n")

        file.write("\nPERFORMANCE COMPARISON\n")
        file.write("-" * 55 + "\n")
        file.write(f"Sequential execution: {sequential_time:.6f} seconds\n")
        file.write(f"Parallel execution: {parallel_time:.6f} seconds\n")
        file.write(f"Total words: {sum(parallel_result.values())}\n")
        file.write(f"Unique words: {len(parallel_result)}\n")
        file.write(f"Results match: {sequential_result == parallel_result}\n")
        file.write("\nProject executed successfully!\n")

    print("Execution report saved to output.txt")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
