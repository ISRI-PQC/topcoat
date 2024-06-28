package main

import (
	"crypto/rand"
	"fmt"
	"log"
	"os"
	"sync"
	"time"

	"cyber.ee/pq/topcoat/config"
	"cyber.ee/pq/topcoat/operations"
	"cyber.ee/pq/topcoat/utils"
)

const (
	REPEATS      = 100
	MAX_PARALLEL = 10
)

func mean(data []int64) float64 {
	if len(data) == 0 {
		return 0
	}
	var sum float64
	for _, d := range data {
		sum += float64(d)
	}
	return sum / float64(len(data))
}

func main() {
	config.InitParams()

	filename := fmt.Sprint(time.Now().Unix()) + ".results.txt"
	f, err := os.Create(filename)
	if err != nil {
		log.Fatal("Error opening file: ", err)
	}
	defer f.Close()

	for parallel := 1; parallel <= MAX_PARALLEL; parallel++ {
		fmt.Printf("Parallel sessions: %v\n", parallel)
		config.Params.PARALLEL_SESSIONS = int64(parallel)
		f.WriteString(fmt.Sprintf("\n\nPARALLEL SESSIONS: %v", parallel))

		results := make(map[string][]int64)
		resultsF := make(map[string][]string)
		averages := make(map[string]float64)

		for rep := 0; rep < REPEATS; rep++ {
			fmt.Printf("Iteration: %v\n", rep)
			fromAliceToBob := make(chan any, 1)
			fromBobToAlice := make(chan any, 1)

			aliceComms := utils.ChanComms{ToOtherParty: fromAliceToBob, FromOtherParty: fromBobToAlice}
			bobComms := utils.ChanComms{ToOtherParty: fromBobToAlice, FromOtherParty: fromAliceToBob}

			// KEYGEN
			aliceKeygenResult := make(chan operations.KeygenResult, 1)
			bobKeygenResult := make(chan operations.KeygenResult, 1)

			var wg sync.WaitGroup
			wg.Add(2)
			start := time.Now()
			go operations.Keygen(&wg, aliceComms, "Alice", aliceKeygenResult)
			go operations.Keygen(&wg, bobComms, "Bob", bobKeygenResult)
			wg.Wait()

			results["keygen"] = append(results["keygen"], time.Since(start).Milliseconds())

			aliceKeys := <-aliceKeygenResult
			bobKeys := <-bobKeygenResult

			message := make([]byte, 32)

			_, err := rand.Read(message)
			if err != nil {
				panic("Could not generate random message")
			}

			// SIGNATURE
			aliceSignResult := make(chan utils.TopcoatSignature, 1)
			bobSignResult := make(chan utils.TopcoatSignature, 1)

			wg.Add(2)
			start = time.Now()
			go operations.Sign(&wg, aliceComms, aliceKeys.Pk, aliceKeys.Sk, message, "Alice", aliceSignResult)
			go operations.Sign(&wg, bobComms, bobKeys.Pk, bobKeys.Sk, message, "Bob", bobSignResult)
			wg.Wait()
			results["sign"] = append(results["sign"], time.Since(start).Milliseconds())

			aliceSignature := <-aliceSignResult
			// bobSignature := <-bobSignResult

			results["iterations"] = append(results["iterations"], int64(aliceSignature.Iterations))
			resultsF["perIt"] = append(resultsF["perIt"], fmt.Sprintf("%.2f", float64(results["sign"][len(results["sign"])-1])/float64(results["iterations"][len(results["iterations"])-1])))

			// VERIFY SIGNATURES
			// result1 := operations.Verify(message, aliceSignature, aliceKeys.Pk)
			// result2 := operations.Verify(message, aliceSignature, bobKeys.Pk)
			// result3 := operations.Verify(message, bobSignature, aliceKeys.Pk)
			// result4 := operations.Verify(message, bobSignature, bobKeys.Pk)

			// log.Printf("Signature results: %v, %v, %v, %v\n", result1, result2, result3, result4)

			averages["keygen"] = mean(results["keygen"])
			averages["sign"] = mean(results["sign"])
			averages["iterations"] = mean(results["iterations"])
		}

		f.WriteString(fmt.Sprintf("\nKEYGEN [ms] (average: %v): %v", averages["keygen"], results["keygen"]))
		f.WriteString(fmt.Sprintf("\nSIGN [ms] (average: %v): %v", averages["sign"], results["sign"]))
		f.WriteString(fmt.Sprintf("\nITERATIONS (average: %v): %v", averages["iterations"], results["iterations"]))
		f.WriteString(fmt.Sprintf("\nSIGN / ITERATIONS: %v", resultsF["perIt"]))
	}

	log.Print("Done.")
}
