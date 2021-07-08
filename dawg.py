from nfa import NFA
from csv import reader as csv_reader
import argparse
from nfa_to_dfa import AutomatonConverter
import time


class Graph:
    def __init__(self, V):
        self.V = V
        self.adj = [[] for i in range(V)]

    def add_edge(self, u, v):
        self.adj[u].append(v)

    def count_paths(self, s, d):
        visited = [False] * self.V

        pathCount = [0]
        self.count_paths_util(s, d, visited, pathCount)
        return pathCount[0]

    def count_paths_util(self, u, d, visited, pathCount):
        visited[u] = True
        if u == d:
            pathCount[0] += 1
        else:
            i = 0
            while i < len(self.adj[u]):
                if not visited[self.adj[u][i]]:
                    self.count_paths_util(self.adj[u][i], d, visited, pathCount)
                i += 1
        visited[u] = False


class TrieNode:
    def __init__(self):
        self.children = dict()
        self.is_leaf = False

    def has_children(self):
        return len(list(self.children.values())) > 0


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        if len(word) == 0:
            return
        curr = self.root
        for char in word:
            if curr.children.get(char) is None:
                curr.children[char] = TrieNode()
            curr = curr.children[char]
        curr.is_leaf = True


class EdgeGenerator:
    def __init__(self, trie):
        self.trie = trie
        self.next_id = None

    def get_edges(self):
        self.next_id = 2  # 0 is s, 1 is t
        edges = list()
        s = 0
        self.get_edges_rec(self.trie.root, s, edges)
        return self.edges_to_dict(edges)

    def get_edges_rec(self, node, node_id, edges):
        t = 1
        for char, value in node.children.items():
            if value.is_leaf:
                edges.append(((node_id, t), char))
            if value.has_children():
                edges.append(((node_id, self.next_id), char))
                self.next_id += 1
                self.get_edges_rec(value, self.next_id - 1, edges)

    @staticmethod
    def edges_to_dict(edges):
        result = dict()
        for edge, char in edges:
            if result.get(edge) is None:
                result[edge] = set()
            result[edge].add(char)
        return result


class EdgePotencySorter:
    @staticmethod
    def sort_edges(edges):
        v = 0
        for edge in edges:
            v = max(v, edge[0])
            v = max(v, edge[1])
        g = Graph(v + 1)
        for u, v in edges:
            g.add_edge(u, v)

        edges = [((e[0], e[1]), g.count_paths(e[1], 1)) for e in edges]
        edges = sorted(edges, key=lambda e: e[1], reverse=True)
        edges = [edge for edge, _ in edges]
        return edges


class NFAGenerator:
    def __init__(self, edges):
        self.transitions = None
        self.states = None
        self.input_symbols = None
        self.initial_state = '0'
        self.final_states = {'1'}
        self.generate_transitions(edges)

    def generate_transitions(self, edges):
        self.transitions = dict()
        for edge, chars in edges.items():
            origin = str(edge[0])
            dest = str(edge[1])
            if self.transitions.get(origin) is None:
                self.transitions[origin] = dict()
            for char in chars:
                if self.transitions[origin].get(char) is None:
                    self.transitions[origin][char] = set()
                self.transitions[origin][char].add(dest)

        self.set_states()
        self.set_input_symbols()

        # Fill in with empty transitions
        for origin_state in self.states:
            if self.transitions.get(origin_state) is None:
                self.transitions[origin_state] = dict()
            for symbol in self.input_symbols:
                if self.transitions[origin_state].get(symbol) is None:
                    self.transitions[origin_state][symbol] = set()

    def set_states(self):
        self.states = set(list(self.transitions.keys()))
        self.states.add('1')  # End state

    def set_input_symbols(self):
        self.input_symbols = set()
        for value in self.transitions.values():
            self.input_symbols = self.input_symbols.union(value)

    def get_nfa(self):
        return NFA(self.states, self.input_symbols, self.initial_state, self.final_states, self.transitions)


class DatasetLoader:
    def load_training_set(self):
        with open('waltz.txt') as f:
            lines = f.readlines()
        lines = [word.replace("\n", "").replace("\t", "") for word in lines]

        positive_words = []
        negative_words = []
        for word in lines:
            if "+" in word:
                positive_words.append(word.replace("+", ""))
            else:
                negative_words.append(word)

        return positive_words, negative_words

    def load_test_set(self):
        dataset = []
        with open("waltzdb.csv", "r") as file:
            reader = csv_reader(file)
            for row in reader:
                dataset.append(row)
        # Remove headers
        dataset.pop(0)

        for i in range(len(dataset)):
            dataset[i][0] = dataset[i][0] == "amyloid"

        return dataset


dataset_loader = DatasetLoader()

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", help="Mode for training or testing the DAWG. Can be either train, nfa or dfa")

args = parser.parse_args()

if args.mode is None:
    print("Mode is required for testing the DAWG")
    exit(1)

if args.mode == 'train':
    print("Creating Waltz DAWG...")
    positive_words, negative_words = dataset_loader.load_training_set()
    trie = Trie()
    for word in positive_words:
        trie.insert(word)

    generator = EdgeGenerator(trie)
    edges = generator.get_edges()

    sorter = EdgePotencySorter()
    sorted_edges = sorter.sort_edges(list(edges.keys()))

    nfa_generator = NFAGenerator(edges)
    nfa = nfa_generator.get_nfa()

    input_symbols = nfa.input_symbols
    last_progress = 0
    for k in range(len(sorted_edges)):
        edge = sorted_edges[k]
        for a in input_symbols:
            if a not in edges[edge]:
                u = str(edge[0])
                v = str(edge[1])
                nfa.add_transition(u, a, v)

                for word in negative_words:
                    if nfa.accepts(word):
                        nfa.remove_transition(u, a, v)
                        break
        progress = (k + 1) / len(sorted_edges) * 100
        if progress - last_progress > 5:
            print("Progress: {:.2f}%".format(progress))
            last_progress = progress

    nfa.save("waltz.aut")
    print("Done!")
elif args.mode == 'nfa' or args.mode == 'dfa':
    automaton = NFA.load("waltz.aut")
    test_set = dataset_loader.load_test_set()

    if args.mode == 'dfa':
        start_time = time.time()
        converter = AutomatonConverter()
        automaton = converter.convert_to_dfa(automaton)
        duration = time.time() - start_time
        print("Time to convert to DFA: {:.2f}s".format(duration))

    pred_count = 0
    time_sum = 0
    for row in test_set:
        start_time = time.time()
        res = automaton.accepts([row[1]])
        time_sum += time.time() - start_time
        if res == row[0]:
            pred_count += 1
    print("Taxa de acerto: {:.2f}%".format(pred_count / len(test_set) * 100))
    print("Total time processing strings: {:.5f}ms".format(time_sum * 1000))
    print("Average string processing time: {:.5f}ms".format(time_sum / len(test_set) * 1000))
else:
    print("Invalid mode")
    exit(1)
