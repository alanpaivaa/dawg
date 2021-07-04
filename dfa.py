from automata_arg_parser import AutomataArgParser
from nfa import NFA


class DFA(NFA):
    def parse_transitions(self, args):
        super().parse_transitions(args)
        self.validate_transitions()

    def validate_transitions(self):
        # Validate transitions
        for state in self.states:
            for symbol in self.input_symbols:
                if len(self.transitions[state][symbol]) > 1:
                    print("DFA can't have more than one destination state in transitions")
                    exit(1)


if __name__ == '__main__':
    parser = AutomataArgParser()
    args = parser.parse()

    if args.output:
        dfa = DFA.from_args()
        filename = args.output
        dfa.save(filename)
        print("DFA successfully saved to {}".format(filename))
    else:
        filename = args.load
        dfa = DFA.load(filename)
        if dfa.accepts(args.accept):
            print('Accepted')
        else:
            print('Rejected')
            exit(1)
