// Package scenario parses the shared JSON scenario file. Only the fields the
// Go topology engine cares about (the "network" block plus a little federation
// metadata) are decoded; everything else is ignored, keeping the Go and Python
// tools loosely coupled around one file.
package scenario

import (
	"encoding/json"
