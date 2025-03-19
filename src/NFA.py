token_map = {
    '(': "openparen",
    ')': "closeparen",
    '|': "or",
    '[': "opensquare",
    ']': "closesquare",
    '?': "question",
    '*': "star",
    '+': "plus"
}

class NFA:
    def __init__(self, regex):
        self.regex = regex
        if not self.is_valid_regex():
            raise ValueError("Invalid regex")
        self.tokens =[]
        self.tokenize()
        print(self.tokens)
      

    def is_valid_regex(self):
        regex = self.regex
        stack = []
        prev_char = None
        escaped=False
        for i, char in enumerate(regex):
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
                stack.append('[')
            elif char == ']':
                if not stack or stack[-1] != '[':
                    return False
                stack.pop()

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
    def tokenize(self):
        """"
        Tokenize the regex string
    
        """
        regex=self.regex
        tokens=[]
        escaped=False
        for i,char in enumerate(regex):
            if escaped:
                escaped=False
                tokens.append(("char",char))
                continue
            if char=="\\":
                escaped=True
                continue
            if char in token_map.keys():
                tokens.append((token_map[char],char))
            else:
                tokens.append(("char",char))

        self.tokens=tokens


nfa=NFA("a(b|c)\\*")