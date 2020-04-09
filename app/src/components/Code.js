import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

class Code extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            code: props.code
        }
    }

    componentWillReceiveProps(props) {
        this.setState({
            code: props.code
        });
    }

    render() {
        if (this.state.code == null) return null;

        return (
            <SyntaxHighlighter language="sql">
                {this.state.code.replace(/\n\n/g, '\n')}
            </SyntaxHighlighter>
        );
    }
}

export default Code;