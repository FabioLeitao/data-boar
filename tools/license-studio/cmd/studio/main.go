// Command studio: offline license JWT signer (Ed25519).
// Build: go build -trimpath -ldflags="-s -w" -o studio ./cmd/studio
package main

import (
	"crypto/ed25519"
	"crypto/x509"
	"encoding/json"
	"encoding/pem"
	"flag"
	"fmt"
	"os"

	"github.com/golang-jwt/jwt/v5"
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(2)
	}
	switch os.Args[1] {
	case "sign":
		runSign(os.Args[2:])
	default:
		printUsage()
		os.Exit(2)
	}
}

func printUsage() {
	fmt.Fprintf(os.Stderr, "usage: %s sign -key <ed25519-private.pem> -claims <claims.json>\n", os.Args[0])
}

func runSign(args []string) {
	fs := flag.NewFlagSet("sign", flag.ExitOnError)
	keyPath := fs.String("key", "", "Ed25519 private key PEM (PKCS#8)")
	claimsPath := fs.String("claims", "", "JSON object with JWT claims")
	_ = fs.Parse(args)
	if *keyPath == "" || *claimsPath == "" {
		fatalf("sign requires -key and -claims")
	}
	pemData, err := os.ReadFile(*keyPath)
	if err != nil {
		fatalf("read key: %v", err)
	}
	block, _ := pem.Decode(pemData)
	if block == nil {
		fatalf("invalid PEM")
	}
	keyAny, err := x509.ParsePKCS8PrivateKey(block.Bytes)
	if err != nil {
		fatalf("parse key: %v", err)
	}
	priv, ok := keyAny.(ed25519.PrivateKey)
	if !ok {
		fatalf("key is not Ed25519")
	}
	rawClaims, err := os.ReadFile(*claimsPath)
	if err != nil {
		fatalf("read claims: %v", err)
	}
	var claims jwt.MapClaims
	if err := json.Unmarshal(rawClaims, &claims); err != nil {
		fatalf("claims json: %v", err)
	}
	tok, err := jwt.NewWithClaims(jwt.SigningMethodEdDSA, claims).SignedString(priv)
	if err != nil {
		fatalf("sign: %v", err)
	}
	fmt.Println(tok)
}

func fatalf(format string, args ...interface{}) {
	fmt.Fprintf(os.Stderr, "studio: "+format+"\n", args...)
	os.Exit(1)
}
