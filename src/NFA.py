from dataclasses import dataclass
from typing import List
import json
from Visualize_NFA import draw_nfa
precedence={
    "*": 6,
    "+": 5,
    "?": 4,
    ".": 3,
    "&": 2,
    "|": 1,
    "(": 0,
   }
@dataclass
class State:
    index: int = 0

    def __post_init__(self):
        self.index = State._generate_index()

    @staticmethod
    def _generate_index():
        if not hasattr(State, "_index_counter"):
            State._index_counter = 0
        index = State._index_counter
        State._index_counter += 1
        return index
    pass
@dataclass  
class Edge:
        from_:State
        to:State
        label:str

@dataclass
class NFA_node:
    start:int
    end:int
    edges:list[Edge]
    states:list[int]

     
class NFA:
    def __init__(self, regex):
     
        if not self.is_valid_regex(regex):
            raise ValueError("Invalid regex")
        tokens=self.tokenize(regex)
        tokens=self.add_concatenation(tokens) #& operator
        
        postfix=self.regex_to_postfix(tokens)
        print(postfix)
        nfa=self.build_nfa(postfix)
        nfa_json=self.construct_json(nfa)
        draw_nfa(nfa_json)

    def construct_json(self,nfa):
        nfa_json={}
        nfa_json["startingState"] = str(nfa.start.index)
        for state in nfa.states:
            nfa_json[str(state.index)]={}
            nfa_json[str(state.index)]["isTerminatingState"]=state==nfa.end

        for edge in nfa.edges:
            edge_from=edge.from_
            edge_to=edge.to
            if edge.label=="epsilon":
                edge.label="ε"
            if  not edge.label in nfa_json[str(edge_from.index)] :
                nfa_json[str(edge_from.index)][edge.label]=[str(edge_to.index)]
            else:
                nfa_json[str(edge_from.index)][edge.label].append(str(edge_to.index))
        print(json.dumps(nfa_json, indent=4))
        return nfa_json
    def build_nfa(self, postfix):
        stack=[]
        for token in postfix:
            if token.isalnum():
               
                stack.append(self.construct_nfa( token))
            elif token=="*":
                stack.append(self.kleene_closure(stack.pop()))
            elif token=="+":
                stack.append(self.positive_closure(stack.pop()))
            elif token=="?":
                stack.append(self.zero_or_one(stack.pop()))
            elif token==".":
                nfa2=stack.pop()
                nfa1=stack.pop()
                stack.append(self.concatenation(nfa1,nfa2))
            elif token=="&":
                nfa2=stack.pop()
                nfa1=stack.pop()
                stack.append(self.concatenation(nfa1,nfa2))
            elif token=="|":
                nfa2=stack.pop()    
                nfa1=stack.pop()
                stack.append(self.union(nfa1,nfa2))
        nfa=stack.pop()
        return nfa
    def construct_nfa(self, char):
       
        start=State()
        end=State() 
        edge=Edge(start,end,char)
        states=[start,end]
        nfa= NFA_node(start,end,[edge],states)
        return nfa
    def concatenation(self, nfa1, nfa2):
        nfa1.states.extend(nfa2.states)
        nfa1.edges.extend(nfa2.edges)
        nfa1.edges.append(Edge(nfa1.end, nfa2.start, "epsilon"))
       
        nfa1.end = nfa2.end
        return nfa1
    def union(self, nfa1, nfa2):
        start = State()
        end = State()
        nfa1.states.extend(nfa2.states)
        nfa1.states.append(end)
        nfa1.states.append(start)
        nfa1.edges.extend(nfa2.edges)

        nfa1.edges.append(Edge(start,nfa1.start, "epsilon"))
        nfa1.edges.append(Edge(start,nfa2.start, "epsilon"))
        nfa1.edges.append(Edge(nfa1.end,end, "epsilon"))
        nfa1.edges.append(Edge(nfa2.end,end, "epsilon"))
        nfa1.start=start
        
        nfa1.end=end
        return nfa1
       
    def kleene_closure(self, nfa):
        start = State()
        end = State()
        nfa.edges.append(Edge(start, nfa.start, "epsilon"))
        nfa.edges.append(Edge(start, end, "epsilon"))
        nfa.edges.append(Edge(nfa.end, start, "epsilon"))
        nfa.edges.append(Edge(nfa.end, nfa.start, "epsilon"))
        nfa.states.extend([start, end])
        nfa.start = start
        nfa.end = end
        return nfa
    def zero_or_one(self, nfa):
        start = State()
        end = State()
        nfa.edges.append(Edge(start, nfa.start, "epsilon"))
        nfa.edges.append(Edge(start, end, "epsilon"))
        nfa.edges.append(Edge(nfa.end, end, "epsilon"))
        nfa.states.extend([start, end])
        nfa.start = start
        nfa.end = end
        return nfa
    def positive_closure(self, nfa):
        start = State()
        end = State()   
        nfa.states.extend([start, end])
    

        nfa.edges.append(Edge(start, nfa.start, "epsilon"))
        nfa.edges.append(Edge(nfa.end, start, "epsilon"))
        nfa.edges.append(Edge(nfa.end, end, "epsilon"))
        nfa.start = start
        nfa.end = end
        return nfa

  

    def add_concatenation(self,tokens):
        new_tokens=[]
        i=0
        while i<len(tokens):
            token=tokens[i]
            if token=="[":
                ##skip till ]
                while i<len(tokens) and tokens[i]!="]":
                    new_tokens.append(tokens[i])
                    i+=1
                continue
            new_tokens.append(token)
            if token.isalnum() or token in ")]?+.*": #add concatenation operator
                if i+1<len(tokens) and (tokens[i+1].isalnum() or tokens[i+1]=="(" or tokens[i+1]=="["):
                    new_tokens.append("&")
            i+=1
        return new_tokens

    def is_valid_regex(self,regex):
        stack = []
        prev_char = None
        escaped=False
        bracket_content = ""
        in_bracket = False


        for i, char in enumerate(regex):
            ##check that char belongs to the valid set of characters
            if not char.isalnum() and char not in "-()|*+?[]\\":
                return False
            if escaped:  
                # Allow any character after `\` (like `\[` or `\+`)
                escaped = False  
                continue  
            if char == '(':
                stack.append('(')
            elif char == ')':
                if not stack or stack[-1] != '(':
                    return False
                stack.pop()
            elif char == '[':
                in_bracket = True
                bracket_content = ""
                stack.append('[')
            elif char == ']':
                if not stack or stack[-1] != '[':
                    return False
                if not self.valid_range(bracket_content):
                    return False
                in_bracket = False

                stack.pop()
            elif in_bracket:
                bracket_content += char
            elif char=="-":
                if not in_bracket or i==0 or i==len(regex)-1 or prev_char in "[-|":
                    return False
            # Ensure `*`, `+`, `?` are not first characters
            elif char in "*+?" and (i == 0 or prev_char in "(|"):
                return False

            # Ensure `|` is not at start or end
            elif char == "|" and (i == 0 or i == len(regex) - 1 or regex[i - 1] in "(|"):
                return False
            
            # Ensure `\` is followed by something
            elif char == "\\":
                escaped = True
                if i == len(regex) - 1:  # Last character cannot be `\`
                    return False
            
            prev_char = char

        # Ensure no unclosed brackets or parentheses
        return len(stack) == 0
    def valid_range(self, bracket_content):
        """
        Check if the content of a bracket is a valid range
        
        """
        if not bracket_content:
             return False
    
        parts = bracket_content.split('-')
        i = 0
        while i < len(bracket_content):
            if i + 2 < len(bracket_content) and bracket_content[i + 1] == '-':
                if bracket_content[i] >= bracket_content[i + 2]:
                    return False  # Invalid range (e.g., Z-A)
                i += 3  # Skip over the range
            else:
                i += 1  # Move to the next character
        
        return True


    def tokenize(self,regex):
        """"
        Tokenize the regex string
    
        """
        tokens=[]
        escaped=False
        for i,char in enumerate(regex):
            if escaped:
                escaped=False
                tokens.append(char)
                continue
            if char=="\\":
                escaped=True
                continue

            tokens.append(char)

        return tokens

    def regex_to_postfix(self,tokens):
        """
        Convert the regex to postfix notation
        
        """
        stack=[]
        postfix=[]
        i =0
        while i <  (len(tokens)):
            token=tokens[i]
            
            i+=1
            if token.isalnum():
                postfix.append(token)
            elif token=="(":
                stack.append(token)
            elif token==")":
                while stack and stack[-1]!="(":
                    postfix.append(stack.pop())
                stack.pop()
            elif token=="[":
                expanded_chars = []
                while i < len(tokens) and tokens[i] != "]":
                    if i + 2 < len(tokens) and tokens[i + 1] == "-":  # Handle ranges like a-c
                        start, end = tokens[i], tokens[i + 2]
                      
                        expanded_chars.extend(chr(j) for j in range(ord(start), ord(end) + 1))
                        i += 3  # Skip `start-end`
                    else:
                        expanded_chars.append(tokens[i])
                        i += 1
                i += 1
                postfix.append(expanded_chars[0])

                for char in expanded_chars[1:]:
                                postfix.append(char)
                                postfix.append("|")  

            elif token in "*+?.":
                postfix.append(token)
            elif token in "&|":
                while stack  and precedence[stack[-1]]>=precedence[token]:
                    postfix.append(stack.pop())
                stack.append(token)
           
        while stack:
            postfix.append(stack.pop())
        return postfix

nfa=NFA("[abc]g*")