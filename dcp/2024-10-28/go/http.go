package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
)

// Response represents the API response structure
type Response struct {
	Number   int   `json:"number"`
	Sequence []int `json:"sequence"`
}

// calculateCollatz generates the Collatz sequence for a given number
func calculateCollatz(n int) []int {
	if n <= 0 {
		return []int{}
	}

	sequence := []int{n}
	current := n

	for current != 1 {
		if current%2 == 0 {
			current = current / 2
		} else {
			current = 3*current + 1
		}
		sequence = append(sequence, current)
	}

	return sequence
}

// collatzHandler handles the /collatz endpoint
func collatzHandler(w http.ResponseWriter, r *http.Request) {
	// Only allow GET requests
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Get the number from query parameter
	numStr := r.URL.Query().Get("number")
	if numStr == "" {
		http.Error(w, "Missing 'number' parameter", http.StatusBadRequest)
		return
	}

	// Convert string to integer
	num, err := strconv.Atoi(numStr)
	if err != nil {
		http.Error(w, "Invalid number format", http.StatusBadRequest)
		return
	}

	if num <= 0 {
		http.Error(w, "Number must be positive", http.StatusBadRequest)
		return
	}

	// Calculate the sequence
	sequence := calculateCollatz(num)

	// Prepare the response
	response := Response{
		Number:   num,
		Sequence: sequence,
	}

	// Set response headers
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)

	// Encode and send the response
	if err := json.NewEncoder(w).Encode(response); err != nil {
		log.Printf("Error encoding response: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
}

func main() {
	// Register the handler
	http.HandleFunc("/collatz", collatzHandler)

	// Start the server
	port := ":9090"
	fmt.Printf("Server starting on port %s\n", port)
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
