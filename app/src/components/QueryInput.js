import React from 'react';
import ReactDOM from 'react-dom';

class QueryInput extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            value: '', 
            handleResponse: props.handleResponse,
            isLoaded: false,
            error: null,
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
  
    handleChange(event) {
        this.setState({value: event.target.value});
    }
  
    handleSubmit(event) {
        const { value, handleResponse } = this.state;
        fetch("http://localhost:5001/parse?input=" + value)
        .then(res => res.json())
        .then(
            (result) => {
                handleResponse(result);
            },
            (error) => {
                this.setState({
                    isLoaded: true,
                    error
                });
            }
        );
      event.preventDefault();
    }
  
    render() {
      return (
        <form onSubmit={this.handleSubmit}>
          <label>
            Name:
            <input type="text" value={this.state.value} onChange={this.handleChange} />
          </label>
          <input type="submit" value="Submit" />
        </form>
      );
    }
  }

  export default QueryInput;
