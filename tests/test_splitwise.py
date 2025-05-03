from app.splitwise import OptimalSplit
from app.helpers import generate_transactions
import time

def test_functionality():
    solver = OptimalSplit()

    transactions0 = [
        ['Ben', 'Sofiya', 10.0] # Ben paid 10 for Sofiya
    ]

    transactions1 = [
        ['Ben', 'Sofiya', 10.0], # Ben paid 10 for Sofiya
        ['Mona', 'Sofiya', 2.5], # Mona paid 2.5 for Sofiya
        ['Mona', 'Ben', 5.0] # Mona paid 5 for Ben
    ]

    transactions_balanced = [
        ['Sofiya', 'Ben', 15.0],
        ['Ben', 'Franka', 7.0],
        ['Franka', 'Mona', 5.0],
        ['Mona', 'Sofiya', 8.0],
        ['Sofiya', 'Franka', 2.0],
        ['Ben', 'Mona', 5.0],
        ['Franka', 'Sofiya', 5.0],
        ['Mona', 'Ben', 3.0],
        ['Sofiya', 'Mona', 1.0],
        ['Ben', 'Sofiya', 1.0],
        ['Franka',  'Ben', 2.0],
        ['Mona', 'Franka', 4.0],
        ['Ben', 'Sofiya', 4.0],
        ['Ben', 'Mona', 4.0],
        ['Franka', 'Ben', 1.0],
    ]

    assert solver.minTransfers(transactions0) == [['Ben', 'Sofiya', 10.0]] # Sofiya owes Ben 10
    assert solver.minTransfers(transactions1) == [['Mona', 'Sofiya', 7.5], ['Ben', 'Sofiya', 5.0]] # Sofiya owes Mona 7.5 and Ben 5
    assert solver.minTransfers(transactions_balanced) == []  # Nothing left to settle

def test_optimality(capsys):
    solver = OptimalSplit()
    
    for n in (10, 50, 1000):
        txns = generate_transactions(n) # generate transactions involving n different people
        start = time.perf_counter()
        solution = solver.minTransfers(txns)
        elapsed = time.perf_counter() - start
        with capsys.disabled():
            print()
            print(f"{n:2d} people → {elapsed:.4f}s")
        assert elapsed < 1.0, f"Took too long for {n} people"
