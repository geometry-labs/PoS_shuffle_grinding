from pydantic import BaseModel
from typing import List
import random
from tqdm.auto import tqdm
import time


# Minimal model of PoS state (only includes aspects relevant to the shuffle grinding attack demo)
class State(BaseModel):
    # Setup and modification
    active_validators: List[str]
    decommission_queue: List[str] = []

    # Internally-managed state
    index_of_next_block_producer: int = None
    memory_of_winners: List[str] = []

    def __init__(self, **data):
        super().__init__(**data)
        self.shuffle()

    def shuffle(self):
        self.index_of_next_block_producer = random.randint(0, len(self.active_validators) - 1)

    def add_to_decommission_queue(self, validator):
        self.decommission_queue.append(validator)

    def add_validator_to_pool(self, validator):
        self.active_validators.append(validator)
        self.shuffle()  # The fact that adding a new validator triggers a shuffle is what enables grinding

    def produce_block(self):
        # Produce Nth block
        self.memory_of_winners.append(self.active_validators[self.index_of_next_block_producer])

        # Handle decommission queue
        if len(self.decommission_queue) > 0:
            self.active_validators = [v for v in self.active_validators if v not in self.decommission_queue]
            self.decommission_queue = []

        # Pick a tentative next block producer
        self.shuffle()

    def print_pending_state(self):
        print(
            f"Pending block {len(self.memory_of_winners)} to be produced by {self.active_validators[self.index_of_next_block_producer]}"
        )


if __name__ == "__main__":
    # Experiment parameters
    organic_validator_count: int = 8
    alice_count: int = 3
    mine_depth: int = 10
    randomness_seed: int = 2
    sleep_time: float = 0.5

    # Setup
    random.seed(randomness_seed)
    honest_validator_ids = [f"organic_validator_{i}" for i in range(organic_validator_count)]
    alice_validator_ids = [f"alice_validator_{i} <--------" for i in range(alice_count)]

    # First a version where we follow the protocol rules and play nicely
    state: State = State(active_validators=honest_validator_ids + alice_validator_ids)
    print("\n>>>>>> Simulating mining (no shenanigans)\n")

    for _ in range(mine_depth):
        state.print_pending_state()
        state.produce_block()
        print("")
        time.sleep(sleep_time)
    fair_wins: int = sum("alice" in s for s in state.memory_of_winners)

    # Now a version where we technically follow the rules, but game the system by reserving the 0th validator for grinding
    reserve_validator_id = alice_validator_ids.pop(0)
    state: State = State(active_validators=honest_validator_ids + alice_validator_ids)
    print("\n>>>>>> Simulating mining (reserve validator shenanigans)\n")

    for _ in range(mine_depth):
        state.print_pending_state()
        # If we're already the next block producer, we simply sit back and win the block
        if "alice" in state.active_validators[state.index_of_next_block_producer]:
            pass
        # If we're not the next block producer, we insert our reserve validator to trigger a shuffle
        else:
            state.add_validator_to_pool(reserve_validator_id)
            state.add_to_decommission_queue(reserve_validator_id)
            print("** Alice triggers_reshuffle")
            state.print_pending_state()
        # Block gets mined
        state.produce_block()
        print("")
        time.sleep(sleep_time)
    grinding_wins: int = sum("alice" in s for s in state.memory_of_winners)

    # Print the setup and the results
    print(f"Running with {organic_validator_count} organic validators and {alice_count} Alice validators")
    print(f"(Alice has {100 * alice_count / (organic_validator_count + alice_count):.2f}% of the stake)")
    print(
        f"Without shuffle grinding, Alice won {fair_wins} blocks out of {mine_depth} ({100 * fair_wins / mine_depth:.2f}%)")
    print(
        f"With shuffle grinding, Alice won {grinding_wins} blocks out of {mine_depth} ({100 * grinding_wins / mine_depth:.2f}%)")
