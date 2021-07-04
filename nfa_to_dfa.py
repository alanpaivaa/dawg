import argparse
from nfa import NFA
from dfa import DFA


class AutomatonConverter:
    @staticmethod
    def node_key(node_set):
        node_list = sorted(list(node_set))
        return ''.join(node_list)

    def aggregate_transitions(self, nfa):
        queue = [{nfa.initial_state}]
        visited = {self.node_key(queue[0])}
        aggr_transitions = dict()

        while len(queue) > 0:
            node_set = queue.pop(0)
            key = self.node_key(node_set)

            # Holds the new transitions for each symbol
            nt = dict()
            for symbol in nfa.input_symbols:
                # All resulting new symbols
                ns = set()
                for node in node_set:
                    ns = ns.union(nfa.transitions[node][symbol])
                nt[symbol] = ns

                ns_key = self.node_key(ns)
                if ns_key not in visited:
                    queue.append(ns)
                    visited.add(ns_key)

            aggr_transitions[key] = nt

        return aggr_transitions

    def aggr_keys(self, aggr_transitions):
        # Create a dict mapping new aggregated keys to new keys s0, s1, etc
        i = 0
        key_map = dict()
        t_keys = sorted(aggr_transitions.keys())
        for key in t_keys:
            key_map[key] = 's{}'.format(i)
            i += 1
        return key_map

    def get_dfa_params(self, nfa, aggr_transitions):
        key_map = self.aggr_keys(aggr_transitions)

        dfa_transitions = dict()
        dfa_states = set()
        dfa_initial_state = None
        dfa_final_states = set()

        # Logic for mapping nfa params into dfa params
        t_keys = sorted(aggr_transitions.keys())
        for key in t_keys:
            nt = dict()
            for symbol in nfa.input_symbols:
                nodes = aggr_transitions[key][symbol]
                d_key = self.node_key(nodes)
                nt[symbol] = {key_map[d_key]}

            dfa_key = key_map[key]
            dfa_states.add(dfa_key)
            dfa_transitions[dfa_key] = nt

            if key == nfa.initial_state:
                dfa_initial_state = dfa_key

            for state in nfa.final_states:
                if state in key:
                    dfa_final_states.add(dfa_key)

        return dfa_states, dfa_initial_state, dfa_final_states, dfa_transitions

    def convert_to_dfa(self, nfa):
        aggr_transitions = self.aggregate_transitions(nfa)
        dfa_states, dfa_initial_state, dfa_final_states, dfa_transitions = self.get_dfa_params(nfa, aggr_transitions)
        dfa = DFA(dfa_states, nfa.input_symbols, dfa_initial_state, dfa_final_states, dfa_transitions)
        return dfa


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Path to the input NFA")
    parser.add_argument("-o", "--output", help="Path to the output DFA")

    args = parser.parse_args()

    if args.input is None:
        print("An input NFA path must be provided")
        exit(1)

    if args.output is None:
        print("An output DFA path must be provided")
        exit(1)

    nfa = NFA.load(args.input)

    converter = AutomatonConverter()
    dfa = converter.convert_to_dfa(nfa)
    dfa.save(args.output)
    print("Successfully saved DFA to {}".format(args.output))
