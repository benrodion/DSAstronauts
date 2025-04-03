# initial idea
class SplitWise:
    """
    Core algorithm for debt splitting with minimal amount of payments. 

    Attributes: 
        names: a list of type character containing names indicating the names of the borrowers/lenders.
        expenses: a list of type float containing the expenses per person.
    """

    def __init__(self, names, expenses):
        self.names = str(names) # impose that names are of type string
        self.expenses = float(expenses) # impose that expenses are of type float --> throws error in case of TypeError


        # Check if the lists have the same length, raise error if not
        if len(names) != len(expenses):
            raise ValueError("`names` and `expenses` must be the same length!")
        
        ### create a dictionary with key=`names` and values=`expenses`
        names_exps = {}
        for i  in range(len(names)):
            names_exps[names[i]] = expenses[i]

        ...

# improved idea
class OptimalSplit:
    def minTransfers(self, transactions):
        score = defaultdict(int)

        for l, d, a in transactions: # l = lender, d = debtor, a = amount
            score[l] -= a #reduce score of lender by amount they lent
            score[d] += d #increase score of borrower by amount borrowed

        # separate into debtors and lenders
        positives = [val for val in score.values() if val > 0] #exttract all positive values
        negatives = [val for val in score.values() if val > 0] #exttract all negative values

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
                new_negatives.rmove(negative)


                if positive == -negative:
                    pass #we don't worry about this
                elif positive > -negative:
                    new_positives.append(positive+negative)
                else:
                    new_negatives.append(positive+negative)

                #from all positive values, we iterate over, try to get the one that matches best with the given negative value
                count = min(count, recurse(new_positives, new_negatives))


            return count +1
            return recurse(positives, negatives)