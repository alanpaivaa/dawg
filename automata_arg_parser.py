import argparse


class AutomataArgParser:
    @staticmethod
    def parse():
        parser = argparse.ArgumentParser()
        parser.add_argument("-st", "--states", help="Comma separated list of states")
        parser.add_argument("-sy", "--symbols", help="Comma separated list of input symbols")
        parser.add_argument("-is", "--initial_state", help="Initial state")
        parser.add_argument("-fs", "--final_states", help="Comma separated list of final states")
        parser.add_argument("-t", "--transition",
                            help="Define a transition using the format state-symbol-new_state,other_state",
                            action='append',
                            nargs='+')
        parser.add_argument("-l", "--load", help="Path where the resulting automaton will be written to")
        parser.add_argument("-o", "--output", help="Path to file containing an automaton")
        parser.add_argument("-a", "--accept", help="Pass a string to check acceptance")

        args = parser.parse_args()

        if args.output is not None:
            if not args.states:
                print("A comma separated list of states must be provided")
                exit(1)

            if not args.symbols:
                print("A comma separated list of input symbols must be provided")
                exit(1)

            if not args.initial_state:
                print("An initial state must be provided")
                exit(1)

            if not args.final_states:
                print("A comma separated list of final states must be provided")
                exit(1)

            if not args.transition:
                print("Transitions must be provided")
                exit(1)
        elif args.load is not None:
            if args.accept is None:
                print("A string for checking acceptance must be provided")
                exit(1)
        else:
            print("Either the --load or --output arguments must be provided")
            exit(1)

        return args
