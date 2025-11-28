package main

import (
	"fmt"
	"strings"
)

// ProcessData handles user data processing
func ProcessData(items []int) float64 {
	result := []int{}
	for i := 0; i < len(items); i++ {
		if items[i] > 0 {
			result = append(result, items[i]*2)
		}
	}
	// Bug: Division by zero if no positive items
	return float64(sum(result)) / float64(len(result))
}

func sum(arr []int) int {
	total := 0
	for _, v := range arr {
		total += v
	}
	return total
}

// UserLogin authenticates user - Security vulnerability
func UserLogin(username, password string) string {
	// SQL Injection vulnerability
	query := "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
	return query
}

// ParseConfig reads configuration
func ParseConfig(config string) map[string]string {
	result := make(map[string]string)
	lines := strings.Split(config, "\n")
	
	for i := 0; i < len(lines); i++ {
		parts := strings.Split(lines[i], "=")
		// Bug: No bounds checking
		result[parts[0]] = parts[1]
	}
	
	return result
}

func main() {
	data := []int{1, 2, 3, -1, 4}
	result := ProcessData(data)
	fmt.Printf("Result: %f\n", result)
	
	query := UserLogin("admin", "pass123")
	fmt.Println(query)
	
	config := "key1=value1\nkey2=value2"
	settings := ParseConfig(config)
	fmt.Println(settings)
}

