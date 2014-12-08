#!/usr/bin/python

import ast
import json
from flask import Flask,render_template,request,session
from wtforms import StringField,validators
from wtforms.widgets import TextArea
from flask_wtf import Form
from flask_bootstrap import Bootstrap
#Flask config
app = Flask(__name__)
app.secret_key = 'abc'
Bootstrap(app)

DEBUG = False
#TODO
# implement one node parse per type in order to parse the tree correctly
# as there's no other way to figure out how many children each node has.
# a lot ast types to implement
#Reference: http://greentreesnakes.readthedocs.org/en/latest/nodes.html

#BinOp operators. 
operators = {ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.Div:'/',ast.FloorDiv:'/',
    ast.Mod: '%',ast.Pow: '^',ast.LShift: '<',ast.RShift: '>',ast.BitOr: '|',
    ast.BitAnd: '&',ast.BitXor: 'XOR'}

expr_operators = {ast.Assign:'=',ast.Expr:'='}

#main parsing function
def parse_ast(node,level):
    """This function is called recursively keeping track of its current depth
    Returns a dictionary containing the ast structure modified to match the
    d3.js library that will render the tree. Which means that the rendered tree
    IS NOT exactly the original AST, it's a slightly modified version of it
    
    Returns:
        node_dict - dictionary containing the modified parsed ast"""
    #Each entry is a pair: ast.Type => str_representation
    #first thing to do is to make sure that node is a AST subtype
    assert isinstance(node, ast.AST)
    node_dict = parse_node(node,level) #create a dict representing the node
    level = level + 1 #increasing tree level before visiting children nodes
    
    children = [] #create a list to put the children nodes if there is any
    for n in ast.iter_child_nodes(node):
        _node = parse_ast(n,level)
        #_node['parent'] = node_dict
        children.append(_node)
    
    #append the children list to the result if there is at least one child
    if children:
        assert children != []
        node_dict['children'] = children
        if DEBUG:
            print children
    #also the collapsed forms for Expr and Assign should be generated here
    #as we now have all the nested BinOp solved
        if type(node) in [ast.Assign,ast.Expr]:
            node_dict['collapsed'] = parse_Assign_Expr(node,children)
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
        node_dict['var'] = str(node.id) 
    
    #ast.Num
    if type(node) in [ast.Num]:
        node_dict['name'] += ' = ' + str(node.n)
        node_dict['n'] = str(node.n)
    
    #ast.BinOp
    if isinstance(node,ast.BinOp):
        #include a fiekd with the 'result' to show when collapsed
        node_dict['collapsed'] = parse_BinOp(node)
    
    #BinOp arguments "op" types --> operators dictionary
    if type(node) in operators.keys():
        node_dict['name'] = operators[type(node)] + ' (%s)'%node_dict['name']
   
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
        result += '('+ left +')'
    else:
        result += str(left.n) if isinstance (left,ast.Num) else left.id
    
    #operator
    op = iterBinOp.next()
    result += ' ' + operators[type(op)] + ' '
    
    #right operand
    right = iterBinOp.next()
    if isinstance(right,ast.BinOp):
        right = parse_BinOp(right)
        result += '('+ right + ')'
    else:
        result += str(right.n) if isinstance (right,ast.Num) else right.id

    return result

def parse_Assign_Expr(node,children):
    #make sure that this function is called with proper params
    assert type(node) in [ast.Assign,ast.Expr]
    if isinstance(node,ast.Assign):
        collapsed = children[0]['var'] + ' = '
        if children[1].has_key('collapsed'):
            collapsed += children[1]['collapsed']
        else:
            collapsed += children[1].id if children[1].has_key('id') else children[1]['n']
    if isinstance(node,ast.Expr):
        #treat as Binop with left and right parts
        #first operand (left) when n=0, right n=1
        for c in children:
            if c.has_key('collapsed'):
                collapsed = c['collapsed']
            elif c.has_key('id'):
                collapsed = c['id']
            elif c.has_key('n'):
                collapsed = c['n']
    return collapsed

########### Flask part ###########
class CodeForm(Form):
    code = StringField(u'source',widget=TextArea())

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

@app.route('/get_ast')
def get_ast(name=None):
    assert session.has_key('code')
    code = ast.parse(session['code'])
    #TODO: assertions to verifiy for valid code (python assertion)
    return json.dumps(parse_ast(code,0))

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)


