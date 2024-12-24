from flask import Flask, jsonify, request
from typing import List

app = Flask(__name__)


def calculate_collatz(n: int) -> List[int]:
    """
    Calculate the Collatz sequence for a given number.

    Args:
        n (int): The starting number

    Returns:
        List[int]: The complete Collatz sequence
    """
    if n <= 0:
        return []

    sequence = [n]
    current = n

    while current != 1:
        if current % 2 == 0:
            current = current // 2
        else:
            current = 3 * current + 1
        sequence.append(current)

    return sequence


@app.route("/collatz", methods=["GET"])
def collatz_handler():
    """Handle GET requests to /collatz endpoint."""
    # Get the number parameter from the query string
    number_str = request.args.get("number")

    # Check if number parameter exists
    if not number_str:
        return jsonify({"error": "Missing 'number' parameter"}), 400

    # Try to convert the string to integer
    try:
        number = int(number_str)
    except ValueError:
        return jsonify({"error": "Invalid number format"}), 400

    # Validate the number is positive
    if number <= 0:
        return jsonify({"error": "Number must be positive"}), 400

    # Calculate the sequence
    sequence = calculate_collatz(number)

    # Return the response
    return jsonify({"number": number, "sequence": sequence})


@app.errorhandler(500)
def server_error(error):
    """Handle internal server errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
