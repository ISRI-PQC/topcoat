package config

import (
	"fmt"
	"io"

	"cyber.ee/pq/latticehelper"
	"github.com/spf13/viper"
)

type PublicParamsType struct {
	PARALLEL_SESSIONS int64 `yaml:"PARALLEL_SESSIONS"`
	N                 int64 `yaml:"N"`
	Q                 int64 `yaml:"Q"`
	D                 int64 `yaml:"D"`
	K                 int64 `yaml:"K"`
	L                 int64 `yaml:"L"`
	ETA               int64 `yaml:"ETA"`
	TAU               int64 `yaml:"TAU"`
	BETA              int64 `yaml:"BETA"`
	GAMMA             int64 `yaml:"GAMMA"`
	GAMMA_PRIME       int64 `yaml:"GAMMA_PRIME"`
	COMMITMENT_Q      int64 `yaml:"COMMITMENT_Q"`
	COMMITMENT_N      int64 `yaml:"COMMITMENT_N"`
	COMMITMENT_K      int64 `yaml:"COMMITMENT_K"`
	COMMITMENT_L      int64 `yaml:"COMMITMENT_L"`
	COMMITMENT_Nlower int64 `yaml:"COMMITMENT_Nlower"`
	COMMITMENT_BETA   int64 `yaml:"COMMITMENT_BETA"`
	COMMITMENT_B2     int64 `yaml:"COMMITMENT_B2"`
	DIFFERENT_Qs      bool
}

var Params *PublicParamsType

func InitParams(conf io.Reader) error {
	// PARAMETERS
	Params = new(PublicParamsType)

	viper.SetConfigType("yaml")
	err := viper.ReadConfig(conf)
	if err != nil {
		return fmt.Errorf("fatal error config file: %w", err)
	}

	_ = viper.AllKeys()

	err = viper.Unmarshal(&Params)
	if err != nil {
		return fmt.Errorf("unable to decode into struct, %w", err)
	}

	Params.DIFFERENT_Qs = Params.Q != Params.COMMITMENT_Q

	// INITIALIZE LatticeHelper
	if Params.DIFFERENT_Qs {
		return latticehelper.InitMultiple(Params.N, []uint64{uint64(Params.Q), uint64(Params.COMMITMENT_Q)})
	} else {
		return latticehelper.InitSingle(Params.N, uint64(Params.Q))
	}
}
