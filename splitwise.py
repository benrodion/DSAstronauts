from collections import defaultdict
from math import inf, isclose


class OptimalSplit:
    """
    Core algorithm for debt splitting with minimal amount of payments.
    """
    def minTransfers(self, transactions):
        """
        Performs debt split with minimal amount of payments.

        Args:
        - transactions: a list of [lender, borrower, amount] entries.

        Returns:
        - A list of transactions of the form [creditor, debtor, amount].
        """
        score = defaultdict(int) # default value of every new key in the score-dict is set to 0 

        #creates score-dict. Keys: names of group members, Values: total amount owed/borrowed.
        for lender, borrower, amount in transactions:
            score[lender] += amount
            score[borrower] -= amount


         # for us to check what's going on 
        print(score)


        # remove settled accounts (accounts with balance = 0)
        debt = {person: amt for person, amt in score.items() if amt != 0}
        people = list(debt.keys())
        balances = list(debt.values())

        #to check that all accounts with balance 0 have been removed 
        print(debt)

        def dfs(start, balances, people):
            # skip over people with balance == 0 (settled debts)
            while start < len(balances) and abs(balances[start]) < 1e-9: # floating point safeguard 
                start += 1
            # base case: there are no balances to settle --> return 0 (0 payments need to be made) and empty list of transactions    
            if start == len(balances):
                return 0, []
            #initialize minimum number of payments and optimal transaction list
            min_payments = inf
            best_path = []

            # attempt debt settling by pairing balances[start] with each of the later people in the list 
            for i in range(start + 1, len(balances)):
                if balances[start] * balances[i] < 0:# ensures that only debtors & creditors can be paired, not debtor & debtor or creditor & creditor
                    amount = min(abs(balances[start]), abs(balances[i]))#amount to be paid in the simulated transaction 
                    #save balance-values for backtracing
                    start_original = balances[start]
                    i_original = balances[i]

                    # This block is mainly helpful for debugging with print-statements.
                    # It determine direction of payment: from start to i or from i to start. 
                    # It also simulates the payments for us to keep track of them. 
                    if balances[start] < 0: #Case 1: if `start` owes money
                        path = [(people[start], people[i], amount)]
                        #reflect the changes of the transactions in the balances list 
                        balances[i] -= amount
                        balances[start] += amount
                    else:  #Case 2: if `start` gets money
                        path = [(people[i], people[start], amount)]
                        balances[start] -= amount
                        balances[i] += amount

                    # determine whether to move to the next person or stay with 'start' depending on whether `start` has been settled
                    if isclose(balances[start], 0, abs_tol= 1e-6): # Case 1: `start` is settled and we move on 
                        next_start = start + 1
                    else:
                        next_start = start # Case 2: `start` is not settled and we stay with it 

                    # recursive settlement of remaining debt 
                    payments, next_path = dfs(next_start, balances[:], people)
                    if payments + 1 < min_payments: # if path results in fewer payments than before, update best solution 
                        min_payments = payments + 1
                        best_path = path + next_path

                    # restore original balances for next depth-first search
                    balances[start] = start_original
                    balances[i] = i_original
                
            return min_payments, best_path


            return min_payments, best_path


        # run recursive function starting from first unsettled person     
        _, result = dfs(0, balances, people)
        
        return result
    



