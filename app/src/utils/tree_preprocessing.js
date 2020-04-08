
module.exports = {
    tree_converter: hierachicalToAdjacency
};

function hierachicalToAdjacency(treeData) {
    if (treeData == null) return null;

    function recursiveImpl(node, nodes, edges, lastProcessedToken, level = 0) {

        nodes.push({
            id: node.id,
            level: level,
            internalType: node.type,
            label: node.type,
            title: node.kb_resources == null ? '' : node.kb_resources.join('\n')
        });
        
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
                            color: {
                                background: 'rgba(30, 30, 30, 0.3)'
                            },
                            title: 'Unused token'
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

    console.log("flurchy:", output);

    return output;
}
