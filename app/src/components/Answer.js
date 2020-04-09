import React from 'react';


class Answer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            answer: props.answer
        }
    }

    componentWillReceiveProps(props) {
        this.setState({
            answer: props.answer
        });
    }

    render() {
        if (this.state.answer == null) return null;
        var answerType = typeof this.state.answer;
        return (
            <div class='answer-container'>
                {(answerType === 'boolean') && this.state.answer.toString()}
                {(answerType !== 'boolean') && <ul>{this.state.answer.map((entity, _) => <li><a href={entity}>{entity}</a></li>)}</ul>}
            </div>
        );
    }
}

export default Answer;