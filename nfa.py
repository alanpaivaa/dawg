import pickle
from automata_arg_parser import AutomataArgParser


class NFA:
    def __init__(self, states, input_symbols, initial_state, final_states, transitions):
        self.states = states
        self.input_symbols = input_symbols
        self.initial_state = initial_state
        self.final_states = final_states
        self.transitions = transitions

    @classmethod
    def from_args(klass, args):
        states = klass.parse_states(args)
        input_symbols = klass.parse_input_symbols(args)
        final_states = klass.parse_final_states(args)
        transitions = klass.parse_transitions(args, states, input_symbols)
        return klass(states, input_symbols, args.initial_state, final_states, transitions)

    @staticmethod
    def parse_states(args):
        return set(args.states.split(','))

    @staticmethod
    def parse_input_symbols(args):
        return set(args.symbols.split(','))

    @staticmethod
    def parse_final_states(args):
        return set(args.final_states.split(','))

    @staticmethod
    def parse_transitions(args, states, input_symbols):
        transitions_str = [t[0] for t in args.transition]
        transitions = dict()
        for t in transitions_str:
            # Split source state from the rest
            comps = t.split('-')
            origin_state = comps[0]

            # Split input symbol from destination states
            symbol = comps[1]

            # Set destination states
            new_states_str = comps[2]
            destination_states = set(new_states_str.split(','))
            if transitions.get(origin_state) is None:
                transitions[origin_state] = dict()
            transitions[origin_state][symbol] = destination_states

        # Fill in with empty transitions
        for origin_state in states:
            if transitions.get(origin_state) is None:
                transitions[origin_state] = dict()
            for symbol in input_symbols:
                if transitions[origin_state].get(symbol) is None:
                    transitions[origin_state][symbol] = set()

        return transitions

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

    def transition_str(self, state, symbol):
        ts = sorted(list(self.transitions[state][symbol]))
        if len(ts) == 0:
            return ''
        return "{}".format(ts)

    def __str__(self):
        sorted_states = sorted(list(self.states))
        sorted_input_symbols = sorted(list(self.input_symbols))
        transitions_array = list()
        for state in sorted_states:
            for symbol in sorted_input_symbols:
                ts = self.transition_str(state, symbol)
                if len(ts) > 0:
                    transitions_array.append("{} x {} -> {}".format(state, symbol, ts))
        transitions_str = "\n".join(transitions_array)
        return "States: {}\nInput Symbols: {}\nInitial State: {}\nFinal States: {}\nTransitions:\n{}" \
            .format(sorted_states,
                    sorted_input_symbols,
                    self.initial_state,
                    sorted(list(self.final_states)),
                    transitions_str
        )


if __name__ == '__main__':
    parser = AutomataArgParser()
    args = parser.parse()

    if args.output:
        nfa = NFA.from_args(args)
        filename = args.output
        nfa.save(filename)
        print("NFA successfully saved to {}".format(filename))
    else:
        filename = args.load
        nfa = NFA.load(filename)
        print("---------- NFA ----------\n{}\n-------------------------".format(nfa))
        print("Result: ", end="")
        if nfa.accepts(args.accept):
            print('Accepted')
        else:
            print('Rejected')
            exit(1)
