import pickle
from automata_arg_parser import AutomataArgParser

# TODO: Parse args
# TODO: Check if input symbols are valid
# TODO Check if transition exists
# TODO: Save automaton


# -st q0,q1,q2,q3 -sy 0,1 -is q0 -fs q3 -t q0|0:q0 -t q0|1:q0,q1 -t q1|0:q2 -t q1|1:q2 -t q2|0:q3 -t q2|1:q3 -l test_fda.aut -a 100

class NFA:
    def __init__(self, args):
        self.states = None
        self.input_symbols = None
        self.initial_state = args.initial_state
        self.final_states = None
        self.transitions = None

        self.parse_states(args)
        self.parse_input_symbols(args)
        self.parse_final_states(args)
        self.parse_transitions(args)

    def parse_states(self, args):
        self.states = set(args.states.split(','))

    def parse_input_symbols(self, args):
        self.input_symbols = set(args.symbols.split(','))

    def parse_final_states(self, args):
        self.final_states = set(args.final_states.split(','))

    def parse_transitions(self, args):
        transitions_str = [t[0] for t in args.transition]
        self.transitions = dict()
        for t in transitions_str:
            # Split source state from the rest
            comps = t.split('-')
            origin_state = comps[0]

            # Split input symbol from destination states
            symbol = comps[1]

            # Set destination states
            new_states_str = comps[2]
            destination_states = set(new_states_str.split(','))
            if self.transitions.get(origin_state) is None:
                self.transitions[origin_state] = dict()
            self.transitions[origin_state][symbol] = destination_states

        # Fill in with empty transitions
        for origin_state in self.states:
            if self.transitions.get(origin_state) is None:
                self.transitions[origin_state] = dict()
            for symbol in self.input_symbols:
                if self.transitions[origin_state].get(symbol) is None:
                    self.transitions[origin_state][symbol] = set()

    def accepts(self, input_chain):
        current_states = {self.initial_state}

        for symbol in input_chain:
            # Check if symbol is valid
            if symbol not in self.input_symbols:
                return False

            # Get transitioned states
            new_states = set()
            for state in current_states:
                tr = self.transitions[state]
                t_states = tr[symbol]
                for ts in t_states:
                    new_states.add(ts)
            current_states = new_states

        if len(self.final_states.intersection(current_states)) > 0:
            return True
        else:
            return False

    def save(self, filename):
        pickle.dump(self, open(filename, "wb"))

    @staticmethod
    def load(filename):
        return pickle.load(open(filename, "rb"))


parser = AutomataArgParser()
args = parser.parse()

if args.output:
    nfa = NFA(args=args)
    filename = args.output
    nfa.save(filename)
    print("NFA successfully saved to {}".format(filename))
else:
    filename = args.load
    nfa = NFA.load(filename)
    if nfa.accepts(args.accept):
        print('Accepted')
    else:
        print('Rejected')
        exit(1)
