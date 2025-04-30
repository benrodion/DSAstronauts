from collections import defaultdict
from math import inf, isclose
import heapq

# in this script, I am trying to fix the issues the algorithm has with scaling 

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
            score[lender] += float(amount)
            score[borrower] -= float(amount)


         # to check if balances are correct. 
         # output helps verify correctness of solution for simple transactions
        print(score)


        # remove settled accounts (accounts with balance = 0)
        debt = {person: amt for person, amt in score.items() if amt != 0}

        #to check that all accounts with balance 0 have been removed 
        # output helps verify correctness of solution for simple transactions
        print(debt)

        #form priority queues to track who needs to give and receive
        # format is tuple: (-amount, person)
        debtors = []
        creditors = []

        # if the value is negative, the person is a debtor
        # heapq -->  ensure that the person with the biggest balance sits on top of the heap, everything else is unsorted
        for k, v in debt.items(): 
            if v < 0: 
                heapq.heappush(debtors, (-abs(v), k)) #heapq is a min-heap, so we need to work with negative values!

            elif v > 0: 
                heapq.heappush(creditors, (-v, k))

        # initialize empty results list --> will store lists of the format [creditor, debtor, amount]
        best_path = []

        # core of the algorithm: debt settlement 
        while len(debtors) > 0: 
            debtAmount, debtor = heapq.heappop(debtors) #take debtor with biggest debt from heap and remove
            creditAmount, creditor = heapq.heappop(creditors) #take debtor with biggest debt from heap and remove

            debtAmount = -debtAmount
            creditAmount = -creditAmount


            # Identify amount to be paid
            payment = min(debtAmount, creditAmount)

            #record payment 
            path = [creditor, debtor, payment]

            #update balances
            debtAmount -= payment
            creditAmount -= payment

            #import: check if debtor/creditor still have open balances after the transaction
            # if yes: add them back to the heap 
            if debtAmount > 0: 
                heapq.heappush(debtors, (-debtAmount, debtor))
            elif creditAmount > 0:
                heapq.heappush(creditors, (-creditAmount, creditor))

            #add path to solution path
            best_path.append(path)


        return best_path
