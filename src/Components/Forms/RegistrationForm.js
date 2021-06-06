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
        event.preventDefault();
        console.log(this.state)

        const request = {
            method : "POST",
            headers : {
                "Content-Type" : "application/json"
            },
            body : JSON.stringify({
                username : this.state.username,
                email : this.state.email,
                password : this.state.password
            })

        };

        fetch("api/register", request)
            .then(response =>
                response.json())
            .then(json => {
                this.setState({
                    userData : json
                })
            })
            .catch( () => {
                console.log("Error happened meanwhile")
            })
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
            <label>
                Name:
                <input type="text" value={this.state.username} name = "username" onChange={this.handleChange} required autoComplete = "on" />
            </label>
            <label>
                Email:
                <input type="text" value={this.state.email} name = "email" onChange={this.handleChange} required autoComplete = "on"/>
            </label>
            <label>
                Password:
                <input type="password" value={this.state.password} name = "password" onChange={this.handleChange} required autoComplete = "off"/>
            </label>
            <input type="submit" value="Submit" />
            </form>
        );
    }
  }
