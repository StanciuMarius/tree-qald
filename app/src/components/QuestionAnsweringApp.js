import React from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import TreeRenderer from './TreeRenderer.js';
import SyncLoader from "react-spinners/ClipLoader";


class QuestionAnsweringApp extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            tree: null,
            sparqlQuery: null,
            answerNull: null,
            modalClass: 'modal-dialog-small',
            questionInputValue: '', 
            handleResponse: props.responseHandler,
            isLoading: false,
            error: null,
        };
    }

    
    componentDidMount() {
        document.getElementById('question-input').focus();
    }

    handleSubmit(event) {
        const { questionInputValue } = this.state;
        this.setState({answer: null, isLoading: true});

        fetch("http://localhost:5005/answer?input=" + questionInputValue)
        .then(res => res.json())
        .then(
            (result) => {
                this.setState({ 
                    tree: result.tree,
                    sparqlQuery: result.query,
                    answer: result.answer,
                    isLoading: false,
                    modalClass: result.tree == null ? 'modal-dialog-small' : 'modal-dialog-large'
                 });

            },
            (error) => {
                this.setState({
                    isLoaded: true,
                    error: error
                });
            }
        );
      event.preventDefault();
    }
      
    handleInputChange(event) {
        this.setState({questionInputValue: event.target.value});
    }

    render() {
        const {modalClass, tree, questionInputValue, isLoading} = this.state;
        return (
        <>
            <Modal show={true} class={modalClass}>
                <form onSubmit={this.handleSubmit.bind(this)}>
                    <Modal.Header closeButton>
                        <Modal.Title>Question Answering</Modal.Title>
                    </Modal.Header>


                    <Modal.Body style={this.state.boxWidth}>
                        <input id='question-input' placeholder='Ask a question' type="text" value={questionInputValue} onChange={this.handleInputChange.bind(this)}/>
                        {/* {isLoading && <SyncLoader css='margin-top: 10px; display: block; margin-left: auto; margin-right: auto;' size='150px' color={"#001a33"} loading={isLoading}/>} */}
                        {tree != null && <TreeRenderer tree={tree}/>}
                    </Modal.Body>


                    <Modal.Footer>  
                        <Button id='submit-button' type="submit" value="Submit" variant="primary">Ask</Button>
                    </Modal.Footer>
                </form>

            </Modal>
        </>
        );
    }
}


export default QuestionAnsweringApp;