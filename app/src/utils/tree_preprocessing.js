
module.exports = {
    tree_converter: hierachicalToAdjacency
};

// TODO: centralize node descriptions to a .json maybe. They are repeated in comments in common/QueryTree.py and common/grammar.cfg.
var node_properties = {
    'ROOT': {description: 'Answer of the question', color: '#EEAAAA'},
    'PROPERTY': {description: 'This is the property object of all the children entities. Any of the following properties are considered:', color: '#EEAAAA'},
    'PROPERTYCONTAINS': {description: 'Filtered children non-entity nodes by property object containing the child entity/literal', color: '#EEAAAA'},
    'ARGMAX': {description: 'The child entity with the highest property value. Any of the following properties are considered:', color: '#EEAAAA'},
    'ARGMIN': {description: 'The child entity with the lowest property value. Any of the following properties are considered:', color: '#EEAAAA'},
    'ARGNTH': {description: 'N-th child entity by property value (ascending order) where N is the child literal. Any of the following properties are considered:', color: '#EEAAAA'},
    'SAMPLE': {description: 'Picks a random sample from the union of child entities', color: '#EEAAAA'},
    'TOPN': {description: 'The first N children entities by property value (descending order) where N is the child literal. Any of the following properties are considered:', color: '#EEAAAA'},
    'LESS': {description: 'Filtered children entities by property value less than the child literal. Any of the following properties are considered:', color: '#EEAAAA'},
    'GREATER': {description: 'Filtered children entities by property value greater than the child literal. Any of the following properties are considered:', color: '#EEAAAA'},
    'GREATERCOUNT': {description: 'Filtered children entities by property object cardinal greater than the given literal. Any of the following properties are considered:', color: '#EEAAAA'},
    'COUNT': {description: 'Cardinal of the union of children entities', color: '#EEAAAA'},
    'EXISTS': {description: 'True if the union of children entities is not empty', color: '#EEAAAA'},
    'EXISTSRELATION': {description: 'True if any of the following relations exist between the children entities: ', color: '#EEAAAA'},
    'ISA': {description: 'True if the children entities are instances of the child type', color: '#EEAAAA'},
    'ISGREATER': {description: 'True if the children entities have a property value greater than the child literal. Any of the following properties are considered:', color: '#EEAAAA'},
    'ISLESS': {description: 'True if the children entities have a property value less than the child literal. Any of the following properties are considered:', color: '#EEAAAA'},
    'ENTITY': {description: 'Union of the following knowledge base resources:', color: '#AAEEAA'},
    'TYPE': {description: 'This restricts the parent node to be an instance of any of the following classes:', color: '#adc2ff'},
    'LITERAL': {description: 'A date, number or a string literal:', color: '#EE00EE'},
    'TOKEN': {description: 'Relevant keyword, used in the mapping process of the parent', color: '#ffecc7'},
    'UNUSED': {description: 'Irrelevant word of the input question', color: '#AAAAAA'}
}
function hierachicalToAdjacency(treeData) {
    if (treeData == null) return null;

    function recursiveImpl(node, nodes, edges, lastProcessedToken, level = 0) {
        
        var visjsNode = {
            id: node.id,
            level: level,
            internalType: node.type,
            label: node.type,
            color: node_properties[node.type].color
        };
        var description = document.createElement('div');
        description.appendChild(document.createTextNode(node_properties[node.type].description));
        description.appendChild(document.createElement('br'));

        if (node.kb_resources != null) {
            var ul = document.createElement('ul')
            node.kb_resources.forEach(function(url) {     
                url = url.replace(/[<>]/g, '');           
                var li = document.createElement('li'); // create a new list item
                var a = document.createElement('a');
                a.appendChild(document.createTextNode(url));
                a.href = url;

                li.appendChild(a); // append the text to the li
                ul.appendChild(li); // append the list item to the ul
            });
            description.appendChild(ul);
        }
        visjsNode.title = description;
        
        nodes.push(visjsNode);        
        if (node.children) {
            for (var i = 0; i < node.children.length; i++) {
                var child = node.children[i];
                recursiveImpl(child, nodes, edges, lastProcessedToken, level + 1);

                if (child.id >= 0) {
                    // All tokens between last processed token and current token are unusused.
                    for (var tokenIndex = lastProcessedToken.id + 1; tokenIndex < child.id; tokenIndex++) {

                        nodes.push({
                            id: tokenIndex,
                            internalType: 'TOKEN',
                            color: node_properties['UNUSED'].color,
                            title: node_properties['UNUSED'].description
                        });

                        edges.push({
                            from: lastProcessedToken.parentId == null ? node.id : lastProcessedToken.parentId,
                            to: tokenIndex,
                            color: 'rgba(0,0,0,0.1)' // invisible
                        });
                    }
                    lastProcessedToken.id = child.id;
                    lastProcessedToken.parentId = node.id;
                }
                edges.push({
                    from: node.id,
                    to: child.id
                });
            }
        }
    }

    function computeMaxDepth(node, level = 0) {
        var maxDepth = level
        if (node.children) {
            for (var i = 0; i < node.children.length; i++) {
                var child = node.children[i];
                maxDepth = Math.max(maxDepth, computeMaxDepth(child, level + 1));
            }
        }
        return maxDepth;
    }


    var hierarchicalTreeRoot = treeData.root;
    var tokens = treeData.tokens;
    var output = {}
    output.nodes = [];
    output.edges = [];

    var lastProcessedToken = {
        id: -1,
        parentId: null,
    }

    recursiveImpl(hierarchicalTreeRoot, output.nodes, output.edges, lastProcessedToken);
    var maxDepth = computeMaxDepth(hierarchicalTreeRoot);

    for (var i = 0; i < output.nodes.length; i++) {
        var node = output.nodes[i];
        if (node.internalType === 'TOKEN') {
            node.level = maxDepth.toString();
            node.label = tokens[node.id];
        }
    }

    return output;
}
