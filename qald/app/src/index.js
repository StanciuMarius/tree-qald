import React from 'react';
import ReactDOM from 'react-dom';

import Graph from 'vis-react';
 
var options = {
    layout: {
        hierarchical: true
    },
    edges: {
        color: "#000000"
    }
};
 
var events = {
    select: function(event) {
        var { nodes, edges } = event;
    }
}
 
class QueryTree extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            treeData: {},
            tokens: []
        };
    }
    
    componentDidMount() {
        fetch("http://localhost:5001/parse?input=yobama")
        .then(res => res.json())
        .then(
            (result) => {
                console.log(result)
                this.setState({
                    isLoaded: true,
                    treeData: result.tree,
                    tokens: result.tokens
                });
            },
            (error) => {
                this.setState({
                    isLoaded: true,
                    error
                });
            }
        );
    }
    
    render() {
        const { error, isLoaded, treeData, tokens } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return (
                <Graph graph={treeData} options={options} events={events} /> 
            );
        }
    }
}

ReactDOM.render(
    <QueryTree />,
    document.getElementById('root')
  );
  
