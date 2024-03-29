package main

import (
	"encoding/json"
	"fmt"
	"net"
	"os"
	"time"

	"github.com/c-robinson/iplib"
)

type Data struct {
	IpRange             string `json:"ip_range"`
	CountryCode         string `json:"country_code"`
	Subdivision1ISOCode string `json:"subdivision_1_iso_code"`
	City                string `json:"city"`
	PostalCode          string `json:"postal_code"`
}

func deduplicate(data []Data) []Data {
	m := make(map[string]struct{})
	var result []Data
	for _, d := range data {
		if _, ok := m[d.IpRange]; !ok {
			m[d.IpRange] = struct{}{}
			result = append(result, d)
		}
	}
	return result
}

func getIplibNet(CIDR string) iplib.Net {
	if ip, net, err := net.ParseCIDR(CIDR); err == nil {

		ones, _ := net.Mask.Size()
		return iplib.NewNet(ip, ones)
	} else {
		fmt.Println(CIDR, "is not a valid CIDR notation")
		return nil
	}
}

func readJSONFile(filename string) {
	start := time.Now()

	file, err := os.ReadFile(filename)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	var data []Data
	err = json.Unmarshal(file, &data)
	if err != nil {
		fmt.Println("Error while unmarshalling JSON file:", err)
		return
	}

	data = deduplicate(data)

	m := make(map[string]int)
	for _, d := range data {
		network := getIplibNet(d.IpRange)
		for cidr := range m {
			existingNet := getIplibNet(cidr)
			if existingNet.ContainsNet(network) {
				fmt.Println("Contained!")
			}
		}
		m[d.IpRange]++
	}

	// Calculate memory usage after reading the IP ranges

	fmt.Printf("Time taken: %v\n", time.Since(start))
	fmt.Printf("Number of IP ranges: %v\n", len(m))
	// Calculate the total number of IPs and overlaps here (if required)
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Please provide a JSON file path as command line argument.")
		return
	}
	jsonFilePath := os.Args[1]
	readJSONFile(jsonFilePath)
}
