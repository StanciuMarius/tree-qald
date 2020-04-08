import Graph from 'vis-react';
import React from 'react';
import Modal from 'react-bootstrap/Modal';

var utils = require('../utils/tree_preprocessing');

var options = {
    layout: {
        hierarchical: {
            // direction: "LR",
            sortMethod: "directed",
            // treeSpacing: 400,
            levelSeparation: 100,
        }
    },
    interaction: {
        zoomView: false,
        dragNodes: false,
        dragView: false
    },

    physics: {
        hierarchicalRepulsion: {
          nodeDistance: 1
        }
    },
    nodes: {
        shape: 'box'
    },

    edges: {
        color: "#000000",
        smooth: {
            enabled: true,
        }
    },
    height: (Math.round(window.innerHeight * 0.6)).toString(),
};


var events = {
    select: function(event) {
        // var { nodes, edges } = event;
    }
}

class TreeRenderer extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {tree: utils.tree_converter(props.tree)};
        this.network = null;
    }

    componentWillReceiveProps({tree}) {
        this.setState({
            tree: utils.tree_converter(tree)
        });
    }


    render() {
        const {tree} = this.state;
        return (
            <div id="tree-container">
                    <Graph  graph={tree}
                            options={options}
                            events={events}
                            getNetwork={network => network.fit()}/> 
            </div>
        );
    }
}

export default TreeRenderer;
