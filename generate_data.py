
from pathlib import Path

sample_text = """
Cloud computing provides computing resources over the internet.
MapReduce is a programming model used in cloud computing.
The map function processes data and creates key value pairs.
The shuffle phase groups identical keys together.
The reduce function combines values and generates final results.
Python supports parallel processing using multiprocessing.
Cloud computing supports scalable distributed applications.
"""

# Repeat the sample text to create a larger dataset.
number_of_repetitions = 10000

input_file = Path(__file__).parent / "input.txt"
input_file.write_text(
    sample_text * number_of_repetitions,
    encoding="utf-8"
)

print("Large dataset generated successfully!")
print("Number of repetitions:", number_of_repetitions)
print("Input file:", input_file)
print("Total characters:", input_file.stat().st_size)
