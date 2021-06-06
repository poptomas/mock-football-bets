import React, {useState} from 'react';
import { useHistory } from "react-router-dom";

export const Form = () => {

    const [state, setState] = useState({username: "", email : "", password : ""});
    const history = useHistory();

    const handleChange = (event) => {
        const value = event.target.value
        setState({
            ...state,
            [event.target.name] : value
        });
    }
  
    const handleSubmit = (event) =>{
        event.preventDefault();
        const request = {
            method : "POST",
            headers : {
                "Content-Type" : "application/json"
            },
            body : JSON.stringify({
                username : state.username,
                email : state.email,
                password : state.password
            })
        };

        fetch("api/register", request)
            .then(response => 
                response.json())
            .then(json => {
                setState({
                    userData : json
                })
                console.log(state);
                console.log("Email confirmation required");
                //history.push("/");
                //todo nofify user that email confirmation is required
            })
            .catch( () => {
                console.log("Error encountered")
            })
    }
  
    return (
        <form onSubmit={handleSubmit}>
        <label> Username: </label><br/>
            <input type="text" value={state.username || ""} name = "username" onChange={handleChange} required autoComplete = "on" />
        
        <br/><label> Email: </label><br/>
            <input type="text" value={state.email || ""} name = "email" onChange={handleChange} required autoComplete = "on"/>
        
        <br/><label> Password: </label><br/>
            <input type="password" value={state.password || ""} name = "password" onChange={handleChange} required autoComplete = "off"/>
        <br/>
        <input type="submit" value="Submit" />
        </form>
    );
  }
