#!/usr/bin/python

#this module automatically converts ast to json.
#So if you want pure AST, this is the best option. It needs to be installed from the internet though. It's not a default Python module.
#from ast2json_modified import ast2json
import ast
import json
from flask import Flask,render_template,request,session
from wtforms import TextField,validators
from flask_wtf import Form
from flask_bootstrap import Bootstrap
app = Flask(__name__)
app.secret_key = 'abc'
Bootstrap(app)

DEBUG = False
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
    Returns a dictionary containing the ast structure modified to match the
    d3.js library that will render the tree. Which means that the rendered tree
    IS NOT exactly the original AST, it's a slightly modified version of it"""
    
    #first thing is to make sure that node is a AST subtype 
    assert isinstance(node, ast.AST)
    node_dict = parse_node(node,level)  #create a dict representing the  node 
    level = level + 1 #increasing the tree level before visiting children nodes
    
    children = [] #create a list to put the children nodes if there is any
    for n in ast.iter_child_nodes(node):
        _node = parse_ast(n,level)
        #_node['parent'] = node_dict
        children.append(_node)
    
    #append the children list to the result dict if there is at least one child
    if children:
        assert children != [] 
        node_dict['children'] = children
        if DEBUG:
            print children
    return node_dict


def parse_node(node,level):
    node_dict = {}
    node_dict['name'] = node.__class__.__name__ #gets the "name" of the Node
    node_dict['level']= level #keeping track of the tree level
    node_dict['type'] = node.__class__.__name__
    #for each node type we're supposed to make little changes to make it matches
    #the expected node format for the lib we're using to render it (d3.js)
    
    #ast.Assign
    if type(node) in [ast.Assign]:
        node_dict['name'] += '( = )'
    
    #ast.Store, ast.Load, ast.Delete
    if type(node) in [ast.Store,ast.Load,ast.Delete]:
        pass 
    
    #ast.Name
    if isinstance(node,ast.Name):
        node_dict['name'] += ' = ' + str(node.id)
    
    #ast.BinOp
    if isinstance(node,ast.BinOp):
        #include a fiekd with the 'result' to show when collapsed
        node_dict['collapsed'] = parse_BinOp(node)
    
    #BinOp arguments "op" types --> operators dictionary
    if type(node) in operators.keys():
        node_dict['name'] = operators[type(node)] + ' (%s)'%node_dict['name']
    if type(node) in [ast.Num]:
        node_dict['name'] += ' = ' + str(node.n)
    
    #keeping track of position to be able to "preview" BinOp expressions 
    if 'left' in node._fields:
        node_dict['position'] = 'left'
    if 'right' in node._fields:
        node_dict['position'] = 'right'

    return node_dict


def parse_BinOp(x):
    """ Every BinOp has exactly tree children: left, op & right
    The idea here is to use the ast built-in iterator to get them
    in order and make the string that represents the current node
    collapsed """
    result = '' 
    iterBinOp = ast.iter_child_nodes(x)

    #left operand 
    left = iterBinOp.next()
    if isinstance(left,ast.BinOp):
        left = parse_BinOp(left)
        result += left
    else:
        result += str(left.n) if isinstance (left,ast.Num) else left.id
    
    #operator
    op = iterBinOp.next()
    result += ' ' + operators[type(op)] + ' '
    
    #right operand 
    right = iterBinOp.next()
    if isinstance(right,ast.BinOp):
        right = parse_BinOp(right)
        result += right 
    else:
        result += str(right.n) if isinstance (right,ast.Num) else right.id

    return result

def get_max_level(tree):
    max_level = 0
    for k in tree.keys():
        #recursion on children nodes
        if k == 'children':
            for c in tree[k]:
                assert type(c) == dict
                max_level = max(max_level,get_max_level(c))
        #return the level value
        if k == 'level':
            max_level = max(max_level,tree[k])
    return max_level

#Flask part
class CodeForm(Form):
    code = TextField('source')

@app.route('/',methods=['GET','POST'])
def index(name=None):
    form = CodeForm()
    #first usage - initial content
    if isinstance(form.code.data,type(None)):
        form.code.data = 'z = x * (y - z)'
        session['code'] = form.code.data
    else:
        session['code'] = form.code.data 
    return render_template('index.html',name=name,form=form)
    #return render_template('base.html',name=name,form=form)

@app.route('/get_ast')
def get_ast(name=None):
    assert session.has_key('code')
    code = ast.parse(session['code'])
    #TODO: assertions to verifiy for valid code
    return json.dumps(parse_ast(code,0))

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)


