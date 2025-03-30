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