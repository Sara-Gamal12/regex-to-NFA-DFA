import graphviz
print(graphviz.__version__)

def draw_nfa(nfa, output_file="nfa_graph"):
    dot = graphviz.Digraph(format="png")

    # Extract the starting state
    start_state = nfa["startingState"]

    ##color the starting state
    dot.node(start_state, shape="circle", style="filled", fillcolor="lightgrey")

    
    for state, transitions in nfa.items():
        if state == "startingState":
            continue  
        # Mark accepting (terminating) states differently
        if transitions["isTerminatingState"]:
            dot.node(state, shape="doublecircle")
        else:
            dot.node(state, shape="circle")

        # Add transitions
        for symbol, target_state in transitions.items():
            if symbol != "isTerminatingState":  # Avoid unnecessary key
                for target in target_state:
                     dot.edge(state, target, label=symbol)

    
    # Render and save the graph
    dot.render(output_file)
    print(f"NFA graph saved as {output_file}.png")


# import json

# # Load the NFA JSON file
# with open(r"src\nfa.json", "r") as file:
#     nfa = json.load(file)

# draw_nfa(nfa)
