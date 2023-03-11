from typing import Callable, Generic, TypeVar, Set

S = TypeVar("S")
T = TypeVar("T")

class NFA(Generic[S]):
	def __init__ (self, init_state, final_states, alphabet, states_mult, transition_func):
		self.init_state : S = init_state
		self.final_states : [S] = final_states
		self.alphabet : Set[str] = alphabet
		self.states_mult : Set[S] = states_mult
		self.transition_func : [(S, str, S)] = transition_func
	def map(self, f: Callable[[S], T]) -> 'NFA[T]':
		states_mult = set([f(x) for x in self.states_mult])
		init_state = f(self.init_state)
		final_states = [f(x) for x in self.final_states]
		transition_func = [
			(f(x[0]), x[1], f(x[2])) for x in self.transition_func
		]
		return NFA(init_state, final_states, self.alphabet, states_mult, transition_func)

	def next(self, from_state: S, on_chr: str) -> 'set[S]':
		return set([t[2] for t in self.transition_func if t[0] == from_state and t[1] == on_chr])

	def getStates(self) -> 'set[S]':
		return self.states_mult

	def accepts(self, str: str) -> bool:
		def aux_accepts(state: S, str: str, visited) -> bool:
			if (state, str) not in visited:
				visited.append((state, str))
				if len(str) == 0:
					if state in self.final_states:
						return True
					for i in self.next(state, "eps"):
						if aux_accepts(i, str, visited):
							return True
					return False
				for i in self.next(state, str[0]):
					if aux_accepts(i, str[1:], visited):
						return True
				for i in self.next(state, "eps"):
					if aux_accepts(i, str, visited):
						return True
				return False
		return aux_accepts(self.init_state, str, [])

	def isFinal(self, state: S) -> bool:
		for i in self.final_states:
			if i == state:
				return True
		return False


	@staticmethod
	def fromPrenex(str: str) -> 'NFA[int]':
		my_str = str.replace("' '", "space")
		if "	" in my_str:
			my_str = my_str.replace("	", "tab")
		if "'''" in my_str:
			my_str = my_str.replace("'''", "'ghilimea'")
		if "\r" in my_str:
			my_str = my_str.replace("\r", "backR")
		if "\n" in my_str:
			my_str = my_str.replace("\n", "backN")
		if "\0" in my_str:
			my_str = my_str.replace("\0", "nullT")
		my_str = my_str.replace("'", "").split()
		def createNFA(my_str) -> 'NFA[int]':
			token = my_str.pop(0)
			if token == "UNION":
				return union(createNFA(my_str), createNFA(my_str))
			elif token == "CONCAT":
				return concat(createNFA(my_str), createNFA(my_str))
			elif token == "STAR":
				return star(createNFA(my_str))
			elif token == "PLUS":
				return plus(createNFA(my_str))
			else:
				if token == "eps":
					return NFA[int](0, [1], {}, {0,1}, [(0, "eps", 1)])
				elif token == "space":
					return NFA[int](0, [1], {" "}, {0, 1}, [(0, " ", 1)])
				elif token == "void":
					return NFA[int](0, [], {}, {}, [])
				elif token == "tab":
					return NFA[int](0, [1], {"	"}, {0, 1}, [(0, "	", 1)])
				elif token == "ghilimea":
					return NFA[int](0, [1], {"'"}, {0, 1}, [(0, "'", 1)])
				elif token == "backR":
					return NFA[int](0, [1], {"\r"}, {0, 1}, [(0, "\r", 1)])
				elif token == "backN":
					return NFA[int](0, [1], {"\n"}, {0, 1}, [(0, "\n", 1)])
				elif token == "nullT":
					return NFA[int](0, [1], {"\0"}, {0, 1}, [(0, "\0", 1)])
				else:
					return NFA[int](0, [1], {token}, {0,1}, [(0, token, 1)])
		return createNFA(my_str)


def concat(nfa1 : NFA[int], nfa2 : NFA[int]) -> 'NFA[int]' :
	nfa1_prime = nfa1
	nfa2_prime = nfa2


	lista = [x + len(nfa1_prime.states_mult) + 1 for x in nfa2_prime.states_mult]
	nfa2_prime.states_mult = set(lista)
	nfa2_prime.init_state += len(nfa1_prime.states_mult) + 1
	nfa2_prime.final_states[:] = [x + len(nfa1_prime.states_mult) + 1 for x in nfa2_prime.final_states]
	nfa2_prime.transition_func[:] = [
		(x[0] + len(nfa1_prime.states_mult) + 1, x[1], x[2] + len(nfa1_prime.states_mult) + 1) for x in
		nfa2_prime.transition_func]

	states_concat = nfa1.states_mult | nfa2_prime.states_mult

	alphabets_concat = nfa1.alphabet | nfa2_prime.alphabet

	concat_transitions = nfa1.transition_func + nfa2_prime.transition_func
	for i in nfa1.final_states:
		concat_transitions += [(i, "eps", nfa2_prime.init_state)]


	return NFA[int](nfa1.init_state, nfa2_prime.final_states,alphabets_concat, states_concat, concat_transitions)

def union(nfa1 : NFA[int], nfa2 : NFA[int])  -> 'NFA[int]' :
	new_init = 0 #creez starea initiala

	nfa1_prime = nfa1
	nfa2_prime = nfa2

	lista = [x + 1 for x in nfa1_prime.states_mult]
	nfa1_prime.states_mult = set(lista)
	nfa1_prime.init_state += 1
	nfa1_prime.final_states[:] = [x + 1 for x in nfa1_prime.final_states]
	nfa1_prime.transition_func[:] = [(x[0] + 1, x[1],  x[2] + 1 )for x in nfa1_prime.transition_func]

	lista = [x + len(nfa1_prime.states_mult) + 1 for x in nfa2_prime.states_mult]
	nfa2_prime.states_mult = lista
	nfa2_prime.init_state += len(nfa1_prime.states_mult) + 1
	nfa2_prime.final_states[:] = [x + len(nfa1_prime.states_mult) + 1 for x in nfa2_prime.final_states]
	nfa2_prime.transition_func[:] = [(x[0] + len(nfa1_prime.states_mult) + 1, x[1], x[2] + len(nfa1_prime.states_mult) + 1 )for x in nfa2_prime.transition_func]



	new_final = len(nfa1_prime.states_mult) + 1 + len(nfa2_prime.states_mult) + 1#creez starea finala care este urmatoarea stare dupa NFA2

	alphabets_concat = nfa1.alphabet | nfa2_prime.alphabet
	states_concat = []
	states_concat += [new_init] + list(nfa1_prime.states_mult) + list(nfa2_prime.states_mult) + [new_final]
	set_of_states = set(states_concat)

	concat_transitions = [(new_init, "eps", nfa1_prime.init_state)] + [(new_init, "eps", nfa2_prime.init_state)] + nfa1_prime.transition_func + nfa2_prime.transition_func
	for i in nfa1_prime.final_states:
		concat_transitions +=  [(i, "eps", new_final)]

	for i in nfa2_prime.final_states:
		concat_transitions +=  [(i, "eps", new_final)]



	return NFA[int](new_init, [new_final], alphabets_concat, set_of_states, concat_transitions)

def star (nfa1: NFA[int]) -> 'NFA[int]':
	nfa1_prime = nfa1
	new_init = 0

	lista = [x + 1 for x in nfa1_prime.states_mult]
	nfa1_prime.states_mult = set(lista)
	nfa1_prime.init_state += 1
	nfa1_prime.final_states[:] = [x + 1 for x in nfa1_prime.final_states]
	nfa1_prime.transition_func[:] = [(x[0] + 1, x[1], x[2] + 1) for x in nfa1_prime.transition_func]


	new_final = len(nfa1_prime.states_mult) + 1

	states_concat = []
	states_concat += [new_init] + list(nfa1_prime.states_mult) + [new_final]
	states_set = set(states_concat)
	concat_transitions = [(new_init, "eps", new_final)] + [(new_init, "eps", nfa1_prime.init_state)] + nfa1_prime.transition_func
	for i in nfa1_prime.final_states:
		concat_transitions += [(i, "eps", nfa1_prime.init_state)]
	for i in nfa1_prime.final_states:
		concat_transitions += [(i, "eps", new_final)]

	return NFA[int](new_init, [new_final], nfa1_prime.alphabet, states_set, concat_transitions)

def plus (nfa1: NFA[int]) -> 'NFA[int]':
	nfa1_prime = nfa1
	new_init = 0

	lista = [x + 1 for x in nfa1_prime.states_mult]
	nfa1_prime.states_mult = set(lista)
	nfa1_prime.init_state += 1
	nfa1_prime.final_states[:] = [x + 1 for x in nfa1_prime.final_states]
	nfa1_prime.transition_func[:] = [(x[0] + 1, x[1], x[2] + 1) for x in nfa1_prime.transition_func]

	new_final = len(nfa1_prime.states_mult) + 1

	states_concat = []
	states_concat += [new_init] + list(nfa1_prime.states_mult) + [new_final]
	states_set = set(states_concat)
	concat_transitions = [
		(new_init, "eps", nfa1_prime.init_state)] + nfa1_prime.transition_func
	for i in nfa1_prime.final_states:
		concat_transitions += [(i, "eps", nfa1_prime.init_state)]
	for i in nfa1_prime.final_states:
		concat_transitions += [(i, "eps", new_final)]

	return NFA[int](new_init, [new_final], nfa1_prime.alphabet, states_set, concat_transitions)

if __name__ == "__main__":
	nfa = NFA.fromPrenex("UNION CONCAT a b c")
	print(nfa.transition_func)
	print(nfa.accepts("abc"))



