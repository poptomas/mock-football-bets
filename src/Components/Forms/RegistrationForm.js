import React from 'react'

export class Form extends React.Component {
    constructor(props) {
        super(props);
        this.state = {username: "", email : "", password : ""};
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
  
    handleChange(event) {
        const value = event.target.value
         this.setState({
            ...this.state,
            [event.target.name] : value
        });
    }
  
    handleSubmit(event) {
        alert('A name was submitted: ' + this.state);
        console.log(this.state)
        event.preventDefault();
    }
  
    render() {
        return (
            <form onSubmit={this.handleSubmit}>
            <label>
                Name:
                <input type="text" value={this.state.username} name = "username" onChange={this.handleChange} required />
            </label>
            <label>
                Email:
                <input type="text" value={this.state.email} name = "email" onChange={this.handleChange} required />
            </label>
            <label>
                Password:
                <input type="password" value={this.state.password} name = "password" onChange={this.handleChange} required />
            </label>
            <input type="submit" value="Submit" />
            </form>
        );
    }
  }
