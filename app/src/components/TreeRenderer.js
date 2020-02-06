import Graph from 'vis-react';
import React from 'react';
import ReactDOM from 'react-dom';

var utils = require('../utils/tree_preprocessing');

var options = {
    layout: {
        hierarchical: {
            // direction: "LR",
            // sortMethod: "directed",
            // nodeSpacing: 200,
            // treeSpacing: 400,
            levelSeparation: 100,
        }
    },
    physics: false,
    nodes: {
        shape: 'box'
    },

    edges: {
        color: "#000000",
        smooth: {
            enabled: true,
        }
    },
    height: window.innerHeight - 90
};


var events = {
    select: function(event) {
        var { nodes, edges } = event;
    }
}


class TreeRenderer extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            tree: utils.tree_converter(props.tree),
        };
    }
    
    componentDidMount() {
        const { network } = this.state;
        network.fit();
    }
    
    render() {
        const { tree } = this.state;
        return (
            <div id="tree-container">
                <Graph  graph={tree}
                        options={options}
                        events={events}
                        getNetwork={network =>this.setState({network: network})}/> 
            </div>
        );
    }
}

export default TreeRenderer;
