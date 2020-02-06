
module.exports = {
    tree_converter: hierachicalToAdjacency
};

function hierachicalToAdjacency(treeData) {

    var hierarchicalTreeRoot = treeData.tree;
    var tokens = treeData.tokens;

    function recursiveImpl(node, nodes, edges, level = 0) {
        // Tokens are inserted separately to preserver sentece order 
        // (hierarchical layout uses insertion order)
        if (node.type == 'UNUSED') {
            return;
        }

        var visjsNode = {
            id: node.id,
            level: level,
            internalType: node.type,
            label: node.type,
        }

        nodes.push(visjsNode);
        
        if (node.children) {
            for (var i = 0; i < node.children.length; i++) {
                var child = node.children[i];
                recursiveImpl(child, nodes, edges, level + 1);
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

    
    var output = {}
    output.nodes = [];
    output.edges = [];

    recursiveImpl(hierarchicalTreeRoot, output.nodes, output.edges);
    var maxDepth = computeMaxDepth(hierarchicalTreeRoot);
    // addTokens(output.nodes, output.edges, tokens, maxDepth);
    for (var i = 0; i < output.nodes.length; i++) {
        var node = output.nodes[i];
        if (node.internalType == 'TOKEN') {
            node.level = maxDepth;
            node.label = tokens[node.id];
        }
    }

    return output;
}
