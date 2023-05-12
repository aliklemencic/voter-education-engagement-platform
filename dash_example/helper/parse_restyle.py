import re
## SAMPLE INPUTS ##
#single range outputs this:
#sample = [{'dimensions[1].constraintrange': [[0.6248482204515293, 0.786903328351732]]},[0]]
# multi range outputs this:
#sample2 = [{'dimensions[2].constraintrange': [[[67574.85492934738, 69844.9430051734], [70633.16811502521, 72178.08933033475]]]}, [0]]
# when you click off a range it outputs this:
#sample3 = [{'dimensions[1].constraintrange': None}, [0]]
def parse_restyle(input):
    '''
    Parse the values from the restyle interactive attribute from the plotly
    parallel coordinates chart
    Inputs:
        input:  Data from latest restyle event (restyleData) which occurs when
            the user changes selections on the parallel coordinates chart. 
    Outputs:
        index (integer): an integer of the data column that has been filtered
        range_pairs: a list of lists (each of length two) containing the min
        and max value in a given range.
    '''
    index = [re.findall('[0-9]+', k) for k in input[0].keys()]
    range_pairs = []
    for i in input[0].values():
        range_pair = [i[0][0], i[0][1]]
        range_pairs.append(range_pair)
    
    return (int(index[0][0]), range_pairs[0])