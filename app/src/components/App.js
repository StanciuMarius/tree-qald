import React from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Tree from './Tree.js';
import Code from './Code.js';
import Answer from './Answer.js';
import SyncLoader from "react-spinners/ClipLoader";
import {NavLink, BrowserRouter, Route, Switch} from "react-router-dom";

class App extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            tree: null,
            sparqlQuery: null,
            answer: null,
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
        return (
        <BrowserRouter>
            <Modal show={true} class={this.state.modalClass} onHide={() => false}>
                <form onSubmit={this.handleSubmit.bind(this)}>
                    <Modal.Header closeButton>
                        <Modal.Title>TreeQALD</Modal.Title>
                        {this.state.answer && <ul class="nav nav-pills">
                            <li class="nav-item"> <NavLink to="/answer" className='nav-link'> Answer </NavLink> </li>
                            <li class="nav-item"> <NavLink to="/tree"   className='nav-link'> Tree </NavLink> </li>
                            <li class="nav-item"> <NavLink to="/code"   className='nav-link'> Code </NavLink> </li>
                        </ul>}   
                    </Modal.Header>


                    <Modal.Body>
                        <input id='question-input' placeholder='Ask a question' type="text" value={this.statequestionInputValue} onChange={this.handleInputChange.bind(this)}/>
                        {this.state.isLoading && <SyncLoader css='margin-top: 10px; display: block; margin-left: auto; margin-right: auto;' size='150px' color={"#001a33"} loading={this.state.isLoading}/>}
                        <Switch>
                            <Route path='/answer' render={(_) => (<Answer answer={this.state.answer}/>)}/>
                            <Route path='/tree'   render={(_) => (<Tree tree={this.state.tree}/>)}/>
                            <Route path='/code'   render={(_) => (<Code code={this.state.sparqlQuery}/>)}/>
                        </Switch>
                        
                    </Modal.Body>


                    <Modal.Footer>
                        <Button id='submit-button' type='submit' variant="primary">Ask</Button>
                    </Modal.Footer>
                </form>

            </Modal>
        </BrowserRouter>

        );
    }
}


export default App;