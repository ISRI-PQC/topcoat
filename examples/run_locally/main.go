package main

import (
	"crypto/rand"
	"log"
	"os"
	"sync"

	"cyber.ee/pq/topcoat/config"
	"cyber.ee/pq/topcoat/operations"
	"cyber.ee/pq/topcoat/utils"
)

func main() {
	paramf, err := os.Open("/Users/petr/Developer/Repos/qsv/topcoat/config/params.yaml")
	if err != nil {
		log.Fatal(err)
	}

	err = config.InitParams(paramf)
	if err != nil {
		log.Fatal(err)
	}

	fromAliceToBob := make(chan any, 1)
	fromBobToAlice := make(chan any, 1)

	aliceComms := utils.ChanComms{ToOtherParty: fromAliceToBob, FromOtherParty: fromBobToAlice}
	bobComms := utils.ChanComms{ToOtherParty: fromBobToAlice, FromOtherParty: fromAliceToBob}

	// KEYGEN
	aliceKeygenResult := make(chan operations.KeygenResult, 1)
	bobKeygenResult := make(chan operations.KeygenResult, 1)

	var wg sync.WaitGroup
	wg.Add(2)
	go operations.Keygen(&wg, aliceComms, "Alice", aliceKeygenResult)
	go operations.Keygen(&wg, bobComms, "Bob", bobKeygenResult)
	aliceKeys := <-aliceKeygenResult
	bobKeys := <-bobKeygenResult
	wg.Wait()

	log.Printf("PK size: %d\n", len(aliceKeys.Pk.Serialize()))

	message := make([]byte, 32)

	_, err = rand.Read(message)
	if err != nil {
		panic("Could not generate random message")
	}

	// SIGNATURE
	aliceSignResult := make(chan utils.TopcoatSignature, 1)
	bobSignResult := make(chan utils.TopcoatSignature, 1)

	wg.Add(2)
	go operations.Sign(&wg, aliceComms, aliceKeys.Pk, aliceKeys.Sk, message, "Alice", aliceSignResult)
	go operations.Sign(&wg, bobComms, bobKeys.Pk, bobKeys.Sk, message, "Bob", bobSignResult)
	wg.Wait()

	aliceSignature := <-aliceSignResult
	bobSignature := <-bobSignResult

	bb := aliceSignature.Serialize()

	log.Printf("SIG size: %d\n", len(bb))

	// VERIFY SIGNATURES
	result1 := operations.Verify(message, aliceSignature, aliceKeys.Pk)
	result2 := operations.Verify(message, aliceSignature, bobKeys.Pk)
	result3 := operations.Verify(message, bobSignature, aliceKeys.Pk)
	result4 := operations.Verify(message, bobSignature, bobKeys.Pk)

	log.Printf("Signature results: %v, %v, %v, %v", result1, result2, result3, result4)
	log.Println("Done")
}
