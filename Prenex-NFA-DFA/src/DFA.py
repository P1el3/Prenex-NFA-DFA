from typing import Callable, Generic, TypeVar, Set

from src.NFA import NFA

S = TypeVar("S")
T = TypeVar("T")

class DFA(Generic[S]):
	def __init__ (self, init_state, final_states, alphabet, states_mult, transition_func):
		self.init_state : Set[S] = init_state
		self.final_states : [Set[S]] = final_states
		self.alphabet : Set[str] = alphabet
		self.states_mult : [Set[S]] = states_mult
		self.transition_func : [(Set[S], str, Set[S])] = transition_func

	def map(self, f: Callable[[S], T]) -> 'DFA[T]':
		states_mult = []
		init_states = set()
		final_states = []
		transition_func = []
		for sets in self.states_mult:
			states_mult += [set([f(x) for x in sets])]
		for x in self.init_state:
			init_states.add(f(x))
		for sets in self.final_states:
			final_states += [set([f(x) for x in sets])]
		transition_func = [
			(set([f(val) for val in x[0]]), x[1], [f(val) for val in x[2]])
			for x in self.transition_func
		]
		return DFA(init_states, final_states, self.alphabet, states_mult, transition_func)

	def next(self, from_state: S, on_chr: str) -> S:
		return set([t[2] for t in self.transition_func if t[0] == from_state and t[1] == on_chr])

	def getStates(self) -> 'set[S]':
		return self.states_mult

	def next_accept(self, from_states: Set[S], char):
		for states, c, next_states in self.transition_func:
			if states == from_states and char == c:
				return next_states
		return set()

	def accepts(self, str: str) -> bool:
		states = self.init_state
		for char in str:
			set_of_states = self.next_accept(states, char)
			if set_of_states == set():
				return False
			states = set_of_states
		if self.isFinal(states):
			return True
		return False

	def isFinal(self, state: Set[S]) -> bool:
		for s in self.final_states:
			if state == s:
				return True
		return False

	@staticmethod
	def fromPrenex(str: str) -> 'DFA[int]':
		nfa = NFA.fromPrenex(str)
		def recursive_next(visited, from_state, on_char, sett: set) -> Set[int]:
			for i in nfa.transition_func:
				if i[0] == from_state:
					if i[1] == on_char:
						sett.add(i[2])
						epsilon_closure([], i[2], sett)
						return sett
		def epsilon_closure(visited, from_init, states):
			if from_init not in visited:
				visited.append(from_init)
				for i in nfa.transition_func:
					if i[0] == from_init and i[1] == "eps":
						states.add(i[2])
						epsilon_closure(visited, i[2], states)
		initialStates = set()
		initialStates.add(nfa.init_state)
		epsilon_closure([], nfa.init_state, initialStates)
		statesMult = []
		statesMult.append(initialStates)
		def recursive(visited, current_states, states_mult, transitions):
			if current_states not in visited:
				visited.append(current_states)
				for char in nfa.alphabet:
					setOfStates = set()
					for states in current_states:
						recursive_next([], states, char, setOfStates)
					if setOfStates != set():
						states_mult += [setOfStates]
					transitions += [(current_states, char, setOfStates)]
					recursive(visited, setOfStates, states_mult, transitions)
		transitionss = []
		recursive([], initialStates, statesMult, transitionss)
		finalStates = []
		for sets in statesMult:
			if sets.intersection(nfa.final_states) != set():
				finalStates.append(sets)
		return DFA(initialStates, finalStates, nfa.alphabet, statesMult, transitionss)
if __name__ == "__main__":
	dfa = DFA.fromPrenex("STAR a")
	nfa = NFA.fromPrenex("STAR a")
	f: Callable[[int], int] = lambda x: x + 2
	dfa.map(f)


#print(nfa.transition_func)
	#rint(dfa.transition_func)


