#!/usr/bin/python

#this module automatically converts ast to json.
#So if you want pure AST, this is the best option. It needs to be installed from the internet though. It's not a default Python module.
#from ast2json_modified import ast2json
import ast
import json

DEBUG = False
to_return = {}

to_return['body'] = {}

#TODO
# implement one node parse per type in order to parse the tree correctly 
# as there's no other way to figure out how many children each node has.
# a lot ast types to implement 
#Reference: http://greentreesnakes.readthedocs.org/en/latest/nodes.html

#BinOp operators. Each entry is a pair: ast.Type => str_representation
operators = {ast.Add: '+',ast.Sub: '-',ast.Mult: '*',ast.Div: '/',ast.FloorDiv: '/',
    ast.Mod: '%',ast.Pow: '^',ast.LShift: '<',ast.RShift: '>',ast.BitOr: '|',
    ast.BitAnd: '&',ast.BitXor: 'XOR'}

#main parsing function
def parse_ast(node,level):
    """This function is called recursively keeping track of its current depth
    Returns a dictionary containing the ast structure modified to match
    the JS library that will render the tree. Which means that the representation
    IS NOT the original AST, it's a modified version of it """
    
    #first thing is to make sure that node is a AST subtype 
    assert isinstance(node, ast.AST)
    #debugging: print the tree path with node type and current level
    if DEBUG: 
        print node.__class__.__name__ + ' - Node-level: ' + str(level) + ' Instance: ' + str(type(node))
    
    
    result = {} #create a dict representing the current node 
    result['name'] = node.__class__.__name__ #gets the "name" of the Node
    result['level']= level #keeping track of the tree level
    #result['size'] = 5000/(level+1) #attribute used by the JS lib. not using it yet.
    
    #for each node type we're supposed to make little changes to make it matches the
    #expected node format for the lib we're using
    
    #ast.Assign
    if type(node) in [ast.Assign]:
        result['name'] += '( = )'
    
    #ast.Store, ast.Load, ast.Delete
    if type(node) in [ast.Store,ast.Load,ast.Delete]:
        pass 
    
    #ast.Name
    if isinstance(node,ast.Name):
        result['name'] += ' = ' + str(node.id)
    
    #ast.BinOp
    if isinstance(node,ast.BinOp):
        #include a fiekd with the 'result' to show when collapsed
        result['collapsed'] = 'null'
        pass
    
    #BinOp arguments "op" types --> operators dictionary
    if type(node) in operators.keys():
        result['name'] = operators[type(node)] + ' (%s)'%result['name']
        result['color'] = 'red'
    if type(node) in [ast.Num]:
        result['name'] += ' = ' + str(node.n)
    
    #keeping track of position to be able to "preview" BinOp expressions 
    if 'left' in node._fields:
        result['position'] = 'left'
    if 'right' in node._fields:
        result['position'] = 'right'
    
    level = level + 1 #increasing the tree level before visiting children nodes
    
    children = [] #create a list to put the children nodes if there is any
    for n in ast.iter_child_nodes(node):
        children.append(parse_ast(n,level)) #this is the recursive call over all the node's children
    
    #append the children list to the result dict if there is at least one child
    if children:
        assert children != [] 
        result['children'] = children
        if DEBUG:
            print children
    return result


#generate the collapsed steps (preview) -- TODO (not working).
def generate_steps(tree):
    assert type(to_return) == dict
    for n in tree.keys():
        #children are lists. we need to call it recursively
        if n == 'children':
            for _n in tree[n]:
                generate_steps(_n)
        #when find part of algebric expression, put it on 'collapsed' attribute (parent)
        elif n == 'position':
            if tree[n] == 'right':
                tree['collapsed'] += tree['name']
            if tree[n] == 'left':
                pass 
            tree['collapsed'] 
            print tree 
            return tree[n]
            
    if DEBUG:
        return tree



#call the parse function on the example code 
#c = ast.parse('x = 2 + 3') #test-case 1
c = ast.parse('z = x * (y -z)') #test-case 2

to_return =  parse_ast(c,0) #making root = level 0

print generate_steps(to_return)


