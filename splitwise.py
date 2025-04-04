from collections import defaultdict
from math import inf

#CAREFUL: I'VE CHANGED THE SIGN FOR THE AMOUNT FOR CREDITOR AND DEBTOR HERE (compared to the function in splitwise.py)

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

        #final dictionary has names of group members as keys and the total amount owed/borrowed as value 
        for lender, borrower, amount in transactions:
            score[lender] += amount
            score[borrower] -= amount
        #to check 
        print(score)


        # Remove settled accounts
        debt = {person: amt for person, amt in score.items() if amt != 0}
        people = list(debt.keys())
        balances = list(debt.values())

        #to check 
        print(debt)

        def dfs(start, balances, people):
            # Skip settled debts
            while start < len(balances) and balances[start] == 0:
                start += 1
            if start == len(balances):
                return 0, []

            min_txns = inf
            best_path = []

            for i in range(start + 1, len(balances)):
                if balances[start] * balances[i] < 0:
                    # Try settling start with i
                    balances[i] += balances[start]
                    amount = min(abs(balances[start]), abs(balances[i] - balances[start]))

                    if balances[start] < 0:
                        path = [(people[start], people[i], amount)]
                    else:
                        path = [(people[i], people[start], amount)]

                    txns, next_path = dfs(start + 1, balances[:], people)
                    if txns + 1 < min_txns:
                        min_txns = txns + 1
                        best_path = path + next_path

                    balances[i] -= balances[start]  # backtrack

            return min_txns if best_path else 0, best_path

        _, transactions = dfs(0, balances, people)
        return transactions


    """
    Core algorithm for debt splitting with minimal amount of payments.

    Attributes: None
    """

    def nTransfers(self, transactions):
        """
        Calculates the minimum amount of transactions required for debt settlement.

        Args:
        - transactions: a list of [lender, borrower, amount] entries.
        """
        score = defaultdict(int) # default value of every new key in the score-dict is set to 0 

        #final dictionary has names of group members as keys and the total amount owed/borrowed as value 
        for l, b, a in transactions: # l = lender, d = debtor, a = amount
            score[l] -= a #reduce score of lender by amount they lent
            score[b] += a #increase score of borrower by amount borrowed

        # iteratore over dictionary and separate into debtors and lenders
        positives = [val for val in score.values() if val > 0] #exttract all positive values
        negatives = [val for val in score.values() if val < 0] #exttract all negative values

        def recurse(positives, negatives):
            if len(positives) + len(negatives) == 0:
                return 0
            negative = negatives[0]
            count = inf

            for positive in positives:
                #create copies of positives and negatives to store updated values
                new_positives = positives.copy()
                new_negatives = negatives.copy()

                # initially removes the positive and negative from the copied list
                # if positive and negative are satisfied with the transction, we don't do anything
                # if the positive isn't satisfied, we add what remains to be paid back to the list int elif-statement
                # if the positive value does not satisfy the negative value, we add the remaining negative value back to the list
                new_positives.remove(positive)
                new_negatives.remove(negative)


                if positive == -negative:
                    pass #we don't worry about this
                elif positive > -negative:
                    new_positives.append(positive+negative)
                else:
                    new_negatives.append(positive+negative)

                #from all positive values, we iterate over, try to get the one that matches best with the given negative value
                count = min(count, recurse(new_positives, new_negatives))


            return count +1, recurse(positives, negatives)
