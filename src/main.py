from __future__ import annotations

import json
import sys
from typing import Dict, Any

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def build_ghz_circuit(num_qubits: int = 3) -> QuantumCircuit:
    """Constructs an N-qubit GHZ state circuit."""
    if num_qubits < 2:
        raise ValueError("GHZ state requires at least 2 qubits.")

    qc = QuantumCircuit(num_qubits)
    
    # 1. Hadamard gate on Qubit 0 -> Superposition
    qc.h(0)
    
    # 2. Entangle remaining qubits via CNOT chain
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
        
    # 3. Add measurements
    qc.measure_all()
    
    return qc


def run_sampler_simulation(circuit: QuantumCircuit, shots: int = 1024) -> Dict[str, int]:
    """Executes the circuit using the StatevectorSampler primitive."""
    sampler = StatevectorSampler()
    
    # Run sampler job
    job = sampler.run([circuit], shots=shots)
    result = job.result()[0]
    
    # Format counts dictionary
    counts = result.data.meas.get_counts()
    return counts


def main() -> int:
    num_qubits = 3
    shots = 1024
    
    circuit = build_ghz_circuit(num_qubits=num_qubits)
    counts = run_sampler_simulation(circuit, shots=shots)

    payload: Dict[str, Any] = {
        "num_qubits": num_qubits,
        "shots": shots,
        "circuit_depth": circuit.depth(),
        "counts": counts,
        "valid_ghz": set(counts.keys()).issubset({"000", "111"}),
    }

    sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
