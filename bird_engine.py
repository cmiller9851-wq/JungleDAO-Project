import sys
import math
import time
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional

class MemoryTape:
    """Unbounded bidirectional memory tape for dynamic state expansion."""
    def __init__(self):
        self.tape = defaultdict(int)
        self.head = 0

    def read(self) -> int:
        return self.tape[self.head]

    def write(self, val: int):
        self.tape[self.head] = val & 0xFF

    def move(self, direction: int):
        # direction: 0 = Left, 1 = Right
        self.head += 1 if direction == 1 else -1

    def state_snapshot(self) -> Tuple[int, ...]:
        if not self.tape:
            return (0,)
        min_idx = min(self.tape.keys())
        max_idx = max(self.tape.keys())
        return tuple(self.tape[i] for i in range(min_idx, max_idx + 1))


class PrefixTuringMachine:
    """
    3-state Universal Turing Machine running over binary prefix codes.
    Bytecode opcodes are decoded dynamically from the program bitstream.
    """
    def __init__(self, program_bits: str):
        self.bits = program_bits
        self.bit_ptr = 0
        self.tape = MemoryTape()
        self.state = 0
        self.halted = False
        self.steps_executed = 0

    def _read_bit(self) -> Optional[int]:
        if self.bit_ptr >= len(self.bits):
            return None
        bit = int(self.bits[self.bit_ptr])
        self.bit_ptr += 1
        return bit

    def step(self) -> bool:
        if self.halted:
            return False

        # Read instruction from tape head and program bitstream
        tape_val = self.tape.read()
        b0 = self._read_bit()
        b1 = self._read_bit()

        # If bitstream starves, program is incomplete or halts
        if b0 is None or b1 is None:
            self.halted = True
            return False

        # Decode: Write Bit (b0), Move Direction (b1), Next State transition
        self.tape.write(tape_val ^ b0)
        self.tape.move(b1)
        self.state = (self.state + b0 + b1 + 1) % 3
        self.steps_executed += 1

        # State 2 with zero tape value triggers program termination
        if self.state == 2 and self.tape.read() == 0:
            self.halted = True

        return True


class LevinMultiverseQuantifier:
    """
    Simultaneously executes all programs in prefix space using $2^{-|p|}$ time allocation.
    """
    def __init__(self, max_bit_length: int = 12):
        self.max_len = max_bit_length
        self.universal_outputs: Dict[Tuple[int, ...], float] = defaultdict(float)
        self.total_solomonoff_weight = 0.0
        self.executed_programs = 0

    def _generate_prefix_space(self) -> List[str]:
        """Generates all binary prefix programs up to max_bit_length."""
        programs = []
        for length in range(1, self.max_len + 1):
            for i in range(1 << length):
                bit_str = format(i, f'0{length}b')
                programs.append(bit_str)
        return programs

    def execute_dovetail_epoch(self, time_epoch: int = 8):
        """
        Executes Levin Dovetailing across prefix space.
        Program p of length |p| gets budget = 2^(epoch - |p|).
        """
        programs = self._generate_prefix_space()
        
        t0 = time.perf_counter_ns()

        for prog_bits in programs:
            p_len = len(prog_bits)
            # Levin time allocation budget: 2^(time_epoch - p_len)
            if time_epoch < p_len:
                continue
            
            step_budget = 1 << (time_epoch - p_len)
            solomonoff_weight = 2.0 ** (-p_len)

            tm = PrefixTuringMachine(prog_bits)
            for _ in range(step_budget):
                if not tm.step():
                    break

            if tm.halted:
                snapshot = tm.tape.state_snapshot()
                self.universal_outputs[snapshot] += solomonoff_weight
                self.total_solomonoff_weight += solomonoff_weight
                self.executed_programs += 1

        t1 = time.perf_counter_ns()
        return (t1 - t0) / 1e6

    def compute_ensemble_metrics(self) -> Dict[str, float]:
        """Computes true Shannon Entropy over the Solomonoff Universal Distribution."""
        if self.total_solomonoff_weight == 0:
            return {"shannon_entropy": 0.0, "realms": 0}

        entropy = 0.0
        for snapshot, weight in self.universal_outputs.items():
            prob = weight / self.total_solomonoff_weight
            entropy -= prob * math.log2(prob)

        return {
            "shannon_entropy": entropy,
            "unique_realms": len(self.universal_outputs),
            "solomonoff_mass": self.total_solomonoff_weight
        }


def main():
    sys.stdout.write("======================================================================\n")
    sys.stdout.write(" BARE-METAL SOLOMONOFF DOVETAIL ENGINE: LEVEL IV QUANTIFIER\n")
    sys.stdout.write("======================================================================\n")

    quantifier = LevinMultiverseQuantifier(max_bit_length=10)
    
    # Run Levin time-slicing epochs
    for epoch in range(4, 12):
        elapsed_ms = quantifier.execute_dovetail_epoch(time_epoch=epoch)
        metrics = quantifier.compute_ensemble_metrics()
        
        sys.stdout.write(f"Epoch {epoch:2d} | Time: {elapsed_ms:7.2f} ms | "
                         f"Halted Realities: {quantifier.executed_programs:6,d} | "
                         f"Unique States: {metrics['unique_realms']:5,d} | "
                         f"Entropy: {metrics['shannon_entropy']:.4f} bits\n")

    sys.stdout.write("======================================================================\n")
    sys.stdout.write(f"Total Solomonoff Probability Mass Captured: {metrics['solomonoff_mass']:.6f}\n")
    sys.stdout.write("======================================================================\n")


if __name__ == "__main__":
    main()
