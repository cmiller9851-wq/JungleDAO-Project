import pytest
from src.main import build_ghz_circuit, run_sampler_simulation


def test_circuit_depth_and_qubits():
    qc = build_ghz_circuit(num_qubits=3)
    assert qc.num_qubits == 3
    assert qc.depth() > 0


def test_ghz_entanglement():
    shots = 500
    qc = build_ghz_circuit(num_qubits=3)
    counts = run_sampler_simulation(qc, shots=shots)
    
    # Check that only |000> and |111> states occur
    measured_states = set(counts.keys())
    assert measured_states.issubset({"000", "111"})
    
    # Check total shot count balance
    total_shots = sum(counts.values())
    assert total_shots == shots


def test_invalid_qubit_count():
    with pytest.raises(ValueError):
        build_ghz_circuit(num_qubits=1)
